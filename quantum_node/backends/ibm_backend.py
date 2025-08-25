"""
Backend manager para IBM Quantum.
"""
from typing import Dict, Any, Optional, Union
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Session, SamplerV2 as Sampler
from qiskit_ibm_runtime.options import SamplerOptions
from qiskit.result import Result
from qiskit.providers import JobStatus
import time
import requests

from .ibm_config import IBMQuantumConfig


class IBMQuantumBackend:
    """
    Maneja la ejecución de circuitos cuánticos en backends de IBM Quantum.
    """
    
    def __init__(self, token: Optional[str] = None, instance: Optional[str] = None):
        """
        Inicializa el backend de IBM Quantum.
        
        :param token: Token de IBM Quantum
        :param instance: Instancia de IBM Quantum
        """
        self.config = IBMQuantumConfig(token=token, instance=instance)
        self.service = self.config.get_runtime_service()
        self.current_backend = None
        self.session = None
    
    def list_backends(self) -> Dict[str, Any]:
        """
        Lista todos los backends disponibles.
        
        :return: Diccionario con información de backends
        """
        return self.config.list_available_backends()
    
    def set_backend(self, backend_name: str) -> bool:
        """
        Configura el backend a utilizar.
        
        :param backend_name: Nombre del backend
        :return: True si se configuró exitosamente
        """
        try:
            self.current_backend = self.service.backend(backend_name)
            print(f"Backend configurado: {backend_name}")
            return True
        except Exception as e:
            print(f"Error al configurar backend {backend_name}: {e}")
            return False
    
    def get_backend_info(self, backend_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene información detallada de un backend.
        
        :param backend_name: Nombre del backend (usa el actual si no se especifica)
        :return: Información del backend
        """
        try:
            backend = self.current_backend
            if backend_name:
                backend = self.service.backend(backend_name)
            
            if not backend:
                return {"error": "No hay backend configurado"}
            
            config = backend.configuration()
            status = backend.status()
            
            return {
                "name": backend.name,
                "version": getattr(config, 'backend_version', 'N/A'),
                "num_qubits": getattr(config, 'n_qubits', 0),
                "simulator": getattr(config, 'simulator', False),
                "operational": status.operational,
                "pending_jobs": status.pending_jobs,
                "status_msg": status.status_msg,
                "max_shots": getattr(config, 'max_shots', 0),
                "max_experiments": getattr(config, 'max_experiments', 0),
                "coupling_map": getattr(config, 'coupling_map', []),
                "basis_gates": getattr(config, 'basis_gates', [])
            }
        except Exception as e:
            return {"error": f"Error al obtener información del backend: {e}"}
    
    def execute_circuit(self,
                       circuit: QuantumCircuit,
                       backend_name: Optional[str] = None,
                       shots: int = 1024,
                       optimization_level: int = 1,
                       use_session: bool = True) -> Dict[str, Any]:
        """
        Ejecuta un circuito cuántico en IBM Quantum.
        
        :param circuit: Circuito cuántico a ejecutar
        :param backend_name: Nombre del backend (usa el actual si no se especifica)
        :param shots: Número de disparos
        :param optimization_level: Nivel de optimización (0-3)
        :param use_session: Si usar sesión para la ejecución (siempre True para compatibilidad con SamplerV2)
        :return: Resultados de la ejecución
        """
        try:
            # Configurar backend si se especifica
            if backend_name and (not self.current_backend or self.current_backend.name != backend_name):
                if not self.set_backend(backend_name):
                    return {"error": f"No se pudo configurar el backend {backend_name}"}
            
            if not self.current_backend:
                return {"error": "No hay backend configurado"}
            
            # Transpilar el circuito para el backend
            transpiled_circuit = transpile(
                circuit, 
                backend=self.current_backend,
                optimization_level=optimization_level
            )
            
            # Configurar opciones del sampler
            options = SamplerOptions()
            options.default_shots = shots
            
            # Medir tiempo de ejecución total (incluyendo cola)
            import time
            start_time = time.time()
            
            # Intentar usar sesión primero, si falla (plan gratuito), usar modo directo
            try:
                if use_session:
                    # Intentar usar sesión para cuentas de pago
                    with Session(backend=self.current_backend) as session:
                        sampler = Sampler(session=session, options=options)
                        job = sampler.run([transpiled_circuit])
                        result = job.result()
                else:
                    # Modo directo para cuentas gratuitas - usar el servicio directamente
                    from qiskit_ibm_runtime import SamplerV2
                    sampler = SamplerV2(mode=self.current_backend, options=options)
                    job = sampler.run([transpiled_circuit])
                    result = job.result()
            except Exception as session_error:
                if "not authorized to run a session" in str(session_error):
                    # Fallback para cuentas gratuitas - usar modo directo
                    try:
                        from qiskit_ibm_runtime import SamplerV2
                        sampler = SamplerV2(mode=self.current_backend, options=options)
                        job = sampler.run([transpiled_circuit])
                        result = job.result()
                    except Exception as fallback_error:
                        # Si también falla el modo directo, usar el servicio
                        sampler = self.service.sampler(backend=self.current_backend, options=options)
                        job = sampler.run([transpiled_circuit])
                        result = job.result()
                else:
                    # Re-lanzar otros errores
                    raise session_error
            
            # Calcular tiempo total transcurrido
            end_time = time.time()
            total_execution_time = end_time - start_time
            
            # Procesar resultados - manejar diferentes formatos de DataBin
            pub_result = result[0]
            
            # Intentar diferentes formas de acceder a los conteos
            try:
                # Formato más reciente
                if hasattr(pub_result.data, 'meas'):
                    counts = pub_result.data.meas.get_counts()
                elif hasattr(pub_result.data, 'c'):
                    counts = pub_result.data.c.get_counts()
                else:
                    # Buscar el primer atributo que contenga conteos
                    data_attrs = [attr for attr in dir(pub_result.data) if not attr.startswith('_')]
                    if data_attrs:
                        counts = getattr(pub_result.data, data_attrs[0]).get_counts()
                    else:
                        # Fallback: usar el resultado directamente si es posible
                        counts = pub_result.data.get_counts() if hasattr(pub_result.data, 'get_counts') else {}
            except Exception as count_error:
                # Si todo falla, intentar extraer conteos de otra manera
                try:
                    counts = dict(pub_result.data)
                except:
                    counts = {"error": "No se pudieron extraer los conteos"}
            
            # Usar nuestro tiempo calculado como fallback
            execution_time = round(total_execution_time, 2)  # Redondear a 2 decimales
            
            # Intentar obtener métricas detalladas de IBM usando la API REST
            queue_time = "N/A"
            ibm_execution_time = "N/A"
            ibm_quantum_seconds = "N/A"
            position_in_queue = "N/A"
            detailed_metrics = {}
            
            try:
                # Obtener métricas detalladas usando la API REST de IBM
                metrics = self._get_job_metrics(job.job_id())
                
                if metrics and 'timestamps' in metrics:
                    timestamps = metrics['timestamps']
                    
                    # Parsear timestamps
                    from datetime import datetime
                    def parse_ibm_timestamp(ts_str):
                        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    
                    created = parse_ibm_timestamp(timestamps['created'])
                    running = parse_ibm_timestamp(timestamps['running']) if timestamps.get('running') else None
                    finished = parse_ibm_timestamp(timestamps['finished']) if timestamps.get('finished') else None
                    
                    # Calcular tiempos precisos
                    if running and finished:
                        ibm_execution_time = round((finished - running).total_seconds(), 2)
                        execution_time = ibm_execution_time  # Usar el tiempo preciso de IBM
                    
                    if created and running:
                        queue_time = round((running - created).total_seconds(), 2)
                
                # Obtener información adicional de las métricas
                if metrics:
                    if 'usage' in metrics and 'quantum_seconds' in metrics['usage']:
                        ibm_quantum_seconds = metrics['usage']['quantum_seconds']
                    
                    if 'position_in_queue' in metrics:
                        position_in_queue = metrics['position_in_queue']
                    
                    # Guardar métricas completas para información adicional
                    detailed_metrics = {
                        'bss_seconds': metrics.get('bss', {}).get('seconds', 'N/A'),
                        'executions': metrics.get('executions', 'N/A'),
                        'num_circuits': metrics.get('num_circuits', 'N/A'),
                        'qiskit_version': metrics.get('qiskit_version', 'N/A'),
                        'estimated_start_time': metrics.get('estimated_start_time', 'N/A'),
                        'estimated_completion_time': metrics.get('estimated_completion_time', 'N/A')
                    }
                            
            except Exception as metrics_error:
                print(f"Warning: No se pudieron obtener métricas detalladas: {metrics_error}")
                # Mantener nuestro tiempo calculado como fallback
                pass
            
            return {
                "success": True,
                "job_id": job.job_id(),
                "backend": self.current_backend.name,
                "shots": shots,
                "counts": counts,
                "probabilities": self._counts_to_probabilities(counts, shots),
                "execution_time": execution_time,  # Tiempo de ejecución real (IBM si está disponible, sino nuestro cálculo)
                "queue_time": queue_time,  # Tiempo en cola de IBM
                "ibm_execution_time": ibm_execution_time,  # Tiempo de ejecución puro de IBM
                "quantum_seconds": ibm_quantum_seconds,  # Segundos cuánticos utilizados
                "position_in_queue": position_in_queue,  # Posición en cola cuando se envió
                "timing_info": {
                    "total_time_measured": round(total_execution_time, 2),
                    "measurement_method": "hybrid" if ibm_execution_time != "N/A" else "client_side_timing",
                    "includes_queue_time": True,
                    "includes_network_latency": True,
                    "ibm_metrics_available": ibm_execution_time != "N/A"
                },
                "detailed_metrics": detailed_metrics,  # Métricas adicionales de IBM
                "metadata": {
                    "optimization_level": optimization_level,
                    "transpiled_depth": transpiled_circuit.depth(),
                    "transpiled_gates": len(transpiled_circuit.data)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en la ejecución: {str(e)}",
                "backend": self.current_backend.name if self.current_backend else "N/A"
            }
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un trabajo.
        
        :param job_id: ID del trabajo
        :return: Estado del trabajo
        """
        try:
            job = self.service.job(job_id)
            return {
                "job_id": job_id,
                "status": job.status().name,
                "creation_date": str(job.creation_date),
                "backend": job.backend().name if job.backend() else "N/A"
            }
        except Exception as e:
            return {"error": f"Error al obtener estado del trabajo: {e}"}
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancela un trabajo.
        
        :param job_id: ID del trabajo
        :return: Resultado de la cancelación
        """
        try:
            job = self.service.job(job_id)
            job.cancel()
            return {
                "success": True,
                "job_id": job_id,
                "message": "Trabajo cancelado exitosamente"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al cancelar trabajo: {e}"
            }
    
    def _counts_to_probabilities(self, counts: Dict[str, int], shots: int) -> Dict[str, float]:
        """
        Convierte conteos a probabilidades.
        
        :param counts: Conteos de mediciones
        :param shots: Número total de disparos
        :return: Probabilidades
        """
        return {state: count / shots for state, count in counts.items()}
    
    def validate_connection(self) -> bool:
        """
        Valida la conexión con IBM Quantum.
        
        :return: True si la conexión es válida
        """
        return self.config.validate_connection()
    
    def _get_job_metrics(self, job_id: str) -> dict:
        """
        Obtiene métricas detalladas de un job usando la API REST de IBM.
        
        :param job_id: ID del job
        :return: Diccionario con métricas del job
        """
        try:
            # Obtener token y service CRN del servicio
            token = self.config.token
            
            # Intentar obtener el service CRN de la instancia
            service_crn = None
            if hasattr(self.service, '_account') and hasattr(self.service._account, 'instance'):
                service_crn = self.service._account.instance
            
            # URL de la API de métricas
            url = f"https://quantum.cloud.ibm.com/api/v1/jobs/{job_id}/metrics"
            
            headers = {
                "Accept": "application/json",
                "IBM-API-Version": "2025-05-01",
                "Authorization": f"Bearer {token}"
            }
            
            # Agregar Service-CRN si está disponible
            if service_crn:
                headers["Service-CRN"] = service_crn
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Error obteniendo métricas del job {job_id}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Warning: Excepción obteniendo métricas del job {job_id}: {e}")
            return None
    
    def close_session(self):
        """
        Cierra la sesión actual si existe.
        """
        if self.session:
            self.session.close()
            self.session = None
