from flask import Flask
from flask_cors import CORS
from classic_node import classic_bp, quantum_integration_bp
from classic_node.controllers.ibm_quantum_controller import register_ibm_quantum_routes

def create_app():
    """
    Crea e inicializa la aplicación Flask.
    """
    app = Flask(__name__)

    # Habilitar CORS para toda la aplicación
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Registrar Blueprints
    app.register_blueprint(classic_bp, url_prefix='/classic')
    app.register_blueprint(quantum_integration_bp, url_prefix='/hybrid')
    
    # Registrar rutas de IBM Quantum
    register_ibm_quantum_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
