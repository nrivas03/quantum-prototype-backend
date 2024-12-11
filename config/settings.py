# config/settings.py

import os

class Config:
    # Configuración general
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    
    # Configuración de servidor
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))
    
    # Configuración del entorno cuántico
    QUANTUM_ENGINE_IP = os.getenv("QUANTUM_ENGINE_IP", "172.27.52.229")
    QUANTUM_ENGINE_PORT = int(os.getenv("QUANTUM_ENGINE_PORT", 8989))
    QUANTUM_ACCOUNT_USER = os.getenv("QUANTUM_ACCOUNT_USER", "SpinQ001")
    QUANTUM_ACCOUNT_PASSWORD = os.getenv("QUANTUM_ACCOUNT_PASSWORD", "123456")
    QUANTUM_TASK_NAME = os.getenv("QUANTUM_TASK_NAME", "QuantumTask")

    # Configuración de simulador
    SIMULATION_SHOTS = int(os.getenv("SIMULATION_SHOTS", 1024))

    @classmethod
    def to_dict(cls):
        """
        Retorna las configuraciones como un diccionario.
        Útil para debugging o exportar configuraciones.
        """
        return {key: value for key, value in cls.__dict__.items() if not key.startswith("_")}
