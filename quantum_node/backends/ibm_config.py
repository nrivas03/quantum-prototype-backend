"""
Configuración para IBM Quantum backends.
"""
import os
from typing import Optional, Dict, Any
from qiskit_ibm_runtime import QiskitRuntimeService
# from qiskit_ibm_provider import IBMProvider  # Comentado temporalmente por problemas de compatibilidad


class IBMQuantumConfig:
    """
    Maneja la configuración y autenticación para IBM Quantum.
    """
    
    def __init__(self, token: Optional[str] = None, instance: Optional[str] = None):
        """
        Inicializa la configuración de IBM Quantum.
        
        :param token: Token de IBM Quantum (si no se proporciona, se busca en variables de entorno)
        :param instance: Instancia de IBM Quantum (opcional)
        """
        self.token = token or os.getenv("IBM_QUANTUM_TOKEN")
        self.instance = instance or os.getenv("IBM_QUANTUM_INSTANCE")
        self.channel = os.getenv("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform")
        
        if not self.token:
            raise ValueError(
                "IBM Quantum token no encontrado. "
                "Proporcione el token como parámetro o configure la variable de entorno IBM_QUANTUM_TOKEN"
            )
    
    def get_runtime_service(self) -> QiskitRuntimeService:
        """
        Obtiene el servicio de IBM Quantum Runtime.
        
        :return: Instancia de QiskitRuntimeService
        """
        try:
            # Intentar usar credenciales guardadas primero
            service = QiskitRuntimeService(channel=self.channel, instance=self.instance)
        except Exception:
            # Si no hay credenciales guardadas, usar el token
            service = QiskitRuntimeService(
                channel=self.channel,
                token=self.token,
                instance=self.instance
            )
            # Guardar credenciales para uso futuro
            QiskitRuntimeService.save_account(
                channel=self.channel,
                token=self.token,
                instance=self.instance,
                overwrite=True
            )
        
        return service
    
    def get_provider(self):
        """
        Obtiene el proveedor de IBM Quantum (para backends legacy).
        
        :return: Instancia de IBMProvider o None si no está disponible
        """
        try:
            # Intentar importar IBMProvider
            from qiskit_ibm_provider import IBMProvider
            
            try:
                # Intentar usar credenciales guardadas primero
                provider = IBMProvider(instance=self.instance)
            except Exception:
                # Si no hay credenciales guardadas, usar el token
                provider = IBMProvider(token=self.token, instance=self.instance)
                # Guardar credenciales para uso futuro
                IBMProvider.save_account(
                    token=self.token,
                    instance=self.instance,
                    overwrite=True
                )
            
            return provider
        except ImportError:
            print("Warning: qiskit_ibm_provider no disponible")
            return None
    
    def list_available_backends(self) -> Dict[str, Any]:
        """
        Lista todos los backends disponibles.
        
        :return: Diccionario con información de backends disponibles
        """
        service = self.get_runtime_service()
        
        backends_info = {
            "simulators": [],
            "real_devices": []
        }
        
        try:
            backends = service.backends()
            for backend in backends:
                backend_info = {
                    "name": backend.name,
                    "status": backend.status().operational,
                    "pending_jobs": backend.status().pending_jobs,
                    "num_qubits": backend.configuration().n_qubits if hasattr(backend.configuration(), 'n_qubits') else 0,
                    "simulator": backend.configuration().simulator
                }
                
                if backend_info["simulator"]:
                    backends_info["simulators"].append(backend_info)
                else:
                    backends_info["real_devices"].append(backend_info)
        
        except Exception as e:
            print(f"Error al obtener información de backends: {e}")
        
        return backends_info
    
    def validate_connection(self) -> bool:
        """
        Valida la conexión con IBM Quantum.
        
        :return: True si la conexión es exitosa, False en caso contrario
        """
        try:
            service = self.get_runtime_service()
            # Intentar obtener la lista de backends como prueba de conexión
            backends = service.backends()
            return len(backends) > 0
        except Exception as e:
            print(f"Error de conexión con IBM Quantum: {e}")
            return False
    
    @staticmethod
    def setup_account(token: str, instance: str = "ibm-q/open/main", channel: str = "ibm_quantum"):
        """
        Configura y guarda las credenciales de IBM Quantum.
        
        :param token: Token de IBM Quantum
        :param instance: Instancia de IBM Quantum
        :param channel: Canal de IBM Quantum
        """
        # Guardar para Runtime Service
        QiskitRuntimeService.save_account(
            channel=channel,
            token=token,
            instance=instance,
            overwrite=True
        )
        
        # Guardar para Provider (legacy) si está disponible
        try:
            from qiskit_ibm_provider import IBMProvider
            IBMProvider.save_account(
                token=token,
                instance=instance,
                overwrite=True
            )
        except ImportError:
            print("Warning: qiskit_ibm_provider no disponible, solo se guardaron credenciales para Runtime")
        
        print(f"Credenciales de IBM Quantum guardadas exitosamente para la instancia: {instance}")
