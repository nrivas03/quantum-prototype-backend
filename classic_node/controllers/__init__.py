from .classic_controller import classic_bp
from .quantum_integration_controller import quantum_integration_bp

# Lista de blueprints para registrar en la aplicación principal
blueprints = [
    classic_bp,
    quantum_integration_bp,
]
