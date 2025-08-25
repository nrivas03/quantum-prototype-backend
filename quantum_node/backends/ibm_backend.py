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
        :param use_session: Si usar sesión para la ejecución
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
            
            if use_session:
                # Usar sesión para ejecución
                with Session(service=self.service, backend=self.current_backend) as session:
                    sampler = Sampler(session=session, options=options)
                    job = sampler.run([transpiled_circuit])
                    result = job.result()
            else:
                # Ejecución directa sin sesión
                sampler = Sampler(backend=self.current_backend, options=options)
                job = sampler.run([transpiled_circuit])
                result = job.result()
            
            # Procesar resultados
            pub_result = result[0]
            counts = pub_result.data.meas.get_counts()
            
            return {
                "success": True,
                "job_id": job.job_id(),
                "backend": self.current_backend.name,
                "shots": shots,
                "counts": counts,
                "probabilities": self._counts_to_probabilities(counts, shots),
                "execution_time": getattr(result, 'time_taken', 'N/A'),
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
    
    def close_session(self):
        """
        Cierra la sesión actual si existe.
        """
        if self.session:
            self.session.close()
            self.session = None
