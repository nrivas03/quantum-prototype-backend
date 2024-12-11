from flask import Blueprint, request, jsonify
from classic_node.services import HybridTaskService

quantum_integration_bp = Blueprint('quantum_integration', __name__)

@quantum_integration_bp.route('/hybrid-operation', methods=['POST'])
def hybrid_operation():
    """
    Maneja solicitudes que requieren integración cuántico-clásica.
    Delegará la lógica al HybridTaskService.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Validar datos requeridos
        classical_data = data.get("classicalData")
        quantum_task_data = data.get("quantumTask")
        if not classical_data or not quantum_task_data:
            return jsonify({"error": "Faltan datos necesarios"}), 400

        # Delegar al servicio híbrido
        result = HybridTaskService.process_hybrid_task(classical_data, quantum_task_data)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
