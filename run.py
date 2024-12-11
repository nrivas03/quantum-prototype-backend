from flask import Flask
from classic_node import classic_bp, quantum_integration_bp

def create_app():
    """
    Crea e inicializa la aplicación Flask.
    """
    app = Flask(__name__)

    # Registrar Blueprints
    app.register_blueprint(classic_bp, url_prefix='/classic')
    app.register_blueprint(quantum_integration_bp, url_prefix='/hybrid')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
