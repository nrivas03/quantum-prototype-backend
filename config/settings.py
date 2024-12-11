import os
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

class Config:
    # Configuración general
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY")  # Obligatoria

    # Configuración del servidor
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))

    # Configuración del entorno cuántico
    QUANTUM_ENGINE_IP = os.getenv("QUANTUM_ENGINE_IP")  # Obligatoria
    QUANTUM_ENGINE_PORT = int(os.getenv("QUANTUM_ENGINE_PORT", 8989))
    QUANTUM_ACCOUNT_USER = os.getenv("QUANTUM_ACCOUNT_USER")  # Obligatoria
    QUANTUM_ACCOUNT_PASSWORD = os.getenv("QUANTUM_ACCOUNT_PASSWORD")  # Obligatoria
    QUANTUM_TASK_NAME = os.getenv("QUANTUM_TASK_NAME", "QuantumTask")

    # Configuración de simulador
    SIMULATION_SHOTS = int(os.getenv("SIMULATION_SHOTS", 1024))

    @classmethod
    def validate(cls):
        """
        Valida que todas las configuraciones obligatorias estén presentes.
        Lanza una excepción si falta alguna.
        """
        required = [
            "SECRET_KEY",
            "QUANTUM_ENGINE_IP",
            "QUANTUM_ACCOUNT_USER",
            "QUANTUM_ACCOUNT_PASSWORD",
        ]
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise RuntimeError(f"Las siguientes variables de entorno son obligatorias y faltan: {', '.join(missing)}")

    @classmethod
    def to_dict(cls):
        """
        Retorna las configuraciones como un diccionario.
        Útil para debugging o exportar configuraciones (excluye credenciales sensibles).
        """
        return {
            key: ("*****" if "PASSWORD" in key or "SECRET" in key else value)
            for key, value in cls.__dict__.items() if not key.startswith("_")
        }
