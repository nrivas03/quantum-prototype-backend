from flask import Blueprint, request, jsonify

# Crear el Blueprint para los controladores clásicos
classic_bp = Blueprint('classic_node', __name__)

# Controlador para operaciones clásicas
@classic_bp.route('/classic-operation', methods=['POST'])
def classic_operation():
    """
    Maneja operaciones clásicas específicas.
    Espera datos clásicos en el cuerpo de la solicitud.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Ejemplo de operación clásica
        result = sum(data.get("numbers", []))  # Suma de una lista de números
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@classic_bp.route('/hello', methods=['GET'])
def hello():
    """
    Saluda al usuario con un mensaje simple.
    """
    return jsonify({"message": "¡Hola! ¡Bienvenido al nodo clásico!"})