"""
Servicio para IBM Quantum.
Maneja la lógica de negocio para la ejecución de circuitos cuánticos en IBM Quantum.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from qiskit import QuantumCircuit
import logging

# Agregar path para importar módulos del proyecto
sys.path.append(str(Path(__file__).parent.parent.parent))

from quantum_node.backends.ibm_backend import IBMQuantumBackend
from config.settings import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IBMQuantumService:
    """
    Servicio para manejar operaciones con IBM Quantum.
    """
    
    def __init__(self):
        """
        Inicializa el servicio de IBM Quantum.
        """
        self.backend = None
        self._initialize_backend()
    
    def _initialize_backend(self):
        """
        Inicializa el backend de IBM Quantum.
        """
        try:
            if not Config.IBM_QUANTUM_TOKEN:
                raise ValueError("IBM_QUANTUM_TOKEN no está configurado")
            
            # Solo pasar instance si está configurado
            backend_kwargs = {
                'token': Config.IBM_QUANTUM_TOKEN
            }
            
            if Config.IBM_QUANTUM_INSTANCE:
                backend_kwargs['instance'] = Config.IBM_QUANTUM_INSTANCE
            
            self.backend = IBMQuantumBackend(**backend_kwargs)
            logger.info("Backend de IBM Quantum inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando backend de IBM Quantum: {e}")
            self.backend = None
    
    def is_available(self) -> bool:
        """
        Verifica si el servicio de IBM Quantum está disponible.
        
        :return: True si está disponible
        """
        return self.backend is not None and self.backend.validate_connection()
    
    def get_backend_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de los backends disponibles.
        
        :return: Estado de los backends
        """
        if not self.backend:
            return {"error": "Backend no disponible"}
        
        try:
            backends_info = self.backend.list_backends()
            
            # Agregar información adicional sobre disponibilidad
            for simulator in backends_info.get("simulators", []):
                simulator["available"] = simulator.get("status", False)
            
            for device in backends_info.get("real_devices", []):
                device["available"] = device.get("status", False)
                device["queue_status"] = self._get_queue_status(device.get("pending_jobs", 0))
            
            return {
                "success": True,
                "backends": backends_info,
                "total_simulators": len(backends_info.get("simulators", [])),
                "total_real_devices": len(backends_info.get("real_devices", [])),
                "available_simulators": len([s for s in backends_info.get("simulators", []) if s.get("status", False)]),
                "available_real_devices": len([d for d in backends_info.get("real_devices", []) if d.get("status", False)])
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de backends: {e}")
            return {"error": f"Error obteniendo estado de backends: {str(e)}"}
    
    def get_recommended_backend(self) -> Dict[str, Any]:
        """
        Obtiene el backend recomendado basado en la disponibilidad y cola.
        
        :return: Backend recomendado
        """
        if not self.backend:
            return {"error": "Backend no disponible"}
        
        try:
            backends_info = self.backend.list_backends()
            
            # Preferir simuladores si están disponibles
            simulators = [s for s in backends_info.get("simulators", []) if s.get("status", False)]
            if simulators:
                return {
                    "success": True,
                    "recommended_backend": simulators[0]["name"],
                    "type": "simulator",
                    "reason": "Simulador disponible sin cola"
                }
            
            # Si no hay simuladores, buscar el dispositivo real con menos cola
            real_devices = [d for d in backends_info.get("real_devices", []) if d.get("status", False)]
            if real_devices:
                # Ordenar por número de trabajos pendientes
                real_devices.sort(key=lambda x: x.get("pending_jobs", float('inf')))
                best_device = real_devices[0]
                
                return {
                    "success": True,
                    "recommended_backend": best_device["name"],
                    "type": "real_device",
                    "pending_jobs": best_device.get("pending_jobs", 0),
                    "queue_status": self._get_queue_status(best_device.get("pending_jobs", 0)),
                    "reason": f"Dispositivo real con menor cola ({best_device.get('pending_jobs', 0)} trabajos)"
                }
            
            return {"error": "No hay backends disponibles"}
            
        except Exception as e:
            logger.error(f"Error obteniendo backend recomendado: {e}")
            return {"error": f"Error obteniendo backend recomendado: {str(e)}"}
    
    def execute_circuit(self, 
                       circuit_qasm: str, 
                       backend_name: Optional[str] = None,
                       shots: Optional[int] = None,
                       optimization_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Ejecuta un circuito cuántico en IBM Quantum.
        
        :param circuit_qasm: Circuito en formato QASM
        :param backend_name: Nombre del backend (usa recomendado si no se especifica)
        :param shots: Número de disparos
        :param optimization_level: Nivel de optimización
        :return: Resultados de la ejecución
        """
        if not self.backend:
            return {"error": "Backend no disponible"}
        
        try:
            # Reconstruir circuito desde QASM
            circuit = QuantumCircuit.from_qasm_str(circuit_qasm)
            
            # Usar valores por defecto si no se especifican
            shots = shots or Config.IBM_QUANTUM_DEFAULT_SHOTS
            optimization_level = optimization_level or Config.IBM_QUANTUM_OPTIMIZATION_LEVEL
            
            # Obtener backend recomendado si no se especifica
            if not backend_name:
                recommended = self.get_recommended_backend()
                if not recommended.get("success"):
                    return recommended
                backend_name = recommended["recommended_backend"]
                logger.info(f"Usando backend recomendado: {backend_name}")
            
            # Ejecutar el circuito
            logger.info(f"Ejecutando circuito en {backend_name} con {shots} shots")
            result = self.backend.execute_circuit(
                circuit=circuit,
                backend_name=backend_name,
                shots=shots,
                optimization_level=optimization_level,
                use_session=Config.IBM_QUANTUM_USE_SESSION
            )
            
            # Agregar información del servicio
            if result.get("success"):
                result["service_info"] = {
                    "backend_selected": backend_name,
                    "shots_requested": shots,
                    "optimization_level": optimization_level,
                    "session_used": Config.IBM_QUANTUM_USE_SESSION
                }
                logger.info(f"Ejecución exitosa. Job ID: {result.get('job_id')}")
            else:
                logger.error(f"Error en ejecución: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando circuito: {e}")
            return {
                "success": False,
                "error": f"Error ejecutando circuito: {str(e)}"
            }
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un trabajo.
        
        :param job_id: ID del trabajo
        :return: Estado del trabajo
        """
        if not self.backend:
            return {"error": "Backend no disponible"}
        
        try:
            status = self.backend.get_job_status(job_id)
            return status
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del trabajo {job_id}: {e}")
            return {"error": f"Error obteniendo estado del trabajo: {str(e)}"}
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancela un trabajo.
        
        :param job_id: ID del trabajo
        :return: Resultado de la cancelación
        """
        if not self.backend:
            return {"error": "Backend no disponible"}
        
        try:
            result = self.backend.cancel_job(job_id)
            if result.get("success"):
                logger.info(f"Trabajo {job_id} cancelado exitosamente")
            else:
                logger.error(f"Error cancelando trabajo {job_id}: {result.get('error')}")
            return result
            
        except Exception as e:
            logger.error(f"Error cancelando trabajo {job_id}: {e}")
            return {"error": f"Error cancelando trabajo: {str(e)}"}
    
    def _get_queue_status(self, pending_jobs: int) -> str:
        """
        Obtiene el estado de la cola basado en el número de trabajos pendientes.
        
        :param pending_jobs: Número de trabajos pendientes
        :return: Estado de la cola
        """
        if pending_jobs == 0:
            return "empty"
        elif pending_jobs < 100:
            return "low"
        elif pending_jobs < 500:
            return "medium"
        elif pending_jobs < 2000:
            return "high"
        else:
            return "very_high"
    
    def get_backend_info(self, backend_name: str) -> Dict[str, Any]:
        """
        Obtiene información detallada de un backend específico.
        
        :param backend_name: Nombre del backend
        :return: Información del backend
        """
        if not self.backend:
            return {"error": "Backend no disponible"}
        
        try:
            info = self.backend.get_backend_info(backend_name)
            if not info.get("error"):
                info["queue_status"] = self._get_queue_status(info.get("pending_jobs", 0))
            return info
            
        except Exception as e:
            logger.error(f"Error obteniendo información del backend {backend_name}: {e}")
            return {"error": f"Error obteniendo información del backend: {str(e)}"}

