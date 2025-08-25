"""
Controlador para IBM Quantum.
Proporciona endpoints para interactuar con backends de IBM Quantum.
"""

from flask import Blueprint, request, jsonify
from qiskit import QuantumCircuit
import json
import base64

from classic_node.services.ibm_quantum_service import IBMQuantumService
from config.settings import Config

# Crear blueprint para IBM Quantum
ibm_quantum_bp = Blueprint('ibm_quantum', __name__, url_prefix='/api/ibm-quantum')

# Servicio global para IBM Quantum
ibm_service = None


def get_ibm_service():
    """
    Obtiene o inicializa el servicio de IBM Quantum.
    
    :return: Servicio de IBM Quantum
    """
    global ibm_service
    
    if ibm_service is None:
        try:
            ibm_service = IBMQuantumService()
        except Exception as e:
            print(f"Error inicializando servicio IBM Quantum: {e}")
            return None
    
    return ibm_service


@ibm_quantum_bp.route('/health', methods=['GET'])
def health_check():
    """
    Verifica el estado de la conexión con IBM Quantum.
    
    :return: Estado de la conexión
    """
    service = get_ibm_service()
    if not service:
        return jsonify({
            "status": "error",
            "message": "Servicio IBM Quantum no disponible"
        }), 500
    
    is_connected = service.is_available()
    
    return jsonify({
        "status": "connected" if is_connected else "disconnected",
        "provider": "ibm",
        "message": "Conexión exitosa con IBM Quantum" if is_connected else "Error de conexión con IBM Quantum"
    })


@ibm_quantum_bp.route('/backends', methods=['GET'])
def list_backends():
    """
    Lista todos los backends disponibles con información de estado y cola.
    
    :return: Lista de backends
    """
    service = get_ibm_service()
    if not service:
        return jsonify({
            "error": "Servicio IBM Quantum no disponible"
        }), 500
    
    try:
        backend_status = service.get_backend_status()
        return jsonify(backend_status)
    except Exception as e:
        return jsonify({
            "error": f"Error obteniendo backends: {str(e)}"
        }), 500


@ibm_quantum_bp.route('/backends/recommended', methods=['GET'])
def get_recommended_backend():
    """
    Obtiene el backend recomendado basado en disponibilidad y cola.
    
    :return: Backend recomendado
    """
    service = get_ibm_service()
    if not service:
        return jsonify({
            "error": "Servicio IBM Quantum no disponible"
        }), 500
    
    try:
        recommendation = service.get_recommended_backend()
        return jsonify(recommendation)
    except Exception as e:
        return jsonify({
            "error": f"Error obteniendo backend recomendado: {str(e)}"
        }), 500





@ibm_quantum_bp.route('/execute', methods=['POST'])
def execute_circuit():
    """
    Ejecuta un circuito cuántico con manejo de colas y métricas de tiempo.
    
    :return: Resultados de la ejecución con métricas de cola
    """
    service = get_ibm_service()
    if not service:
        return jsonify({
            "error": "Servicio IBM Quantum no disponible"
        }), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No se proporcionaron datos"
            }), 400
        
        # Obtener parámetros
        circuit_data = data.get('circuit')
        backend_name = data.get('backend_name')  # Opcional, se usará recomendado si no se especifica
        shots = data.get('shots')
        optimization_level = data.get('optimization_level')
        
        if not circuit_data:
            return jsonify({
                "error": "No se proporcionó el circuito"
            }), 400
        
        # Obtener QASM del circuito
        circuit_qasm = _extract_qasm_from_circuit_data(circuit_data)
        if not circuit_qasm:
            return jsonify({
                "error": "Error al extraer QASM del circuito"
            }), 400
        
        # Ejecutar el circuito
        result = service.execute_circuit(
            circuit_qasm=circuit_qasm,
            backend_name=backend_name,
            shots=shots,
            optimization_level=optimization_level
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Error ejecutando circuito: {str(e)}"
        }), 500





@ibm_quantum_bp.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """
    Obtiene el estado de un trabajo.
    
    :param job_id: ID del trabajo
    :return: Estado del trabajo
    """
    service = get_ibm_service()
    if not service:
        return jsonify({
            "error": "Servicio IBM Quantum no disponible"
        }), 500
    
    try:
        status = service.get_job_status(job_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "error": f"Error obteniendo estado del trabajo: {str(e)}"
        }), 500


@ibm_quantum_bp.route('/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """
    Cancela un trabajo.
    
    :param job_id: ID del trabajo
    :return: Resultado de la cancelación
    """
    service = get_ibm_service()
    if not service:
        return jsonify({
            "error": "Servicio IBM Quantum no disponible"
        }), 500
    
    try:
        result = service.cancel_job(job_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": f"Error cancelando trabajo: {str(e)}"
        }), 500


@ibm_quantum_bp.route('/backend-info/<backend_name>', methods=['GET'])
def get_backend_info(backend_name):
    """
    Obtiene información detallada de un backend.
    
    :param backend_name: Nombre del backend
    :return: Información del backend
    """
    service = get_ibm_service()
    if not service:
        return jsonify({
            "error": "Servicio IBM Quantum no disponible"
        }), 500
    
    try:
        info = service.get_backend_info(backend_name)
        return jsonify(info)
    except Exception as e:
        return jsonify({
            "error": f"Error obteniendo información del backend: {str(e)}"
        }), 500


def _extract_qasm_from_circuit_data(circuit_data):
    """
    Extrae el código QASM desde los datos del circuito.
    
    :param circuit_data: Datos del circuito
    :return: Código QASM del circuito
    """
    try:
        if isinstance(circuit_data, str):
            # Si es una cadena base64
            try:
                circuit_bytes = base64.b64decode(circuit_data)
                circuit_dict = json.loads(circuit_bytes.decode('utf-8'))
            except:
                # Si no es base64, asumir que es QASM directo
                return circuit_data
        elif isinstance(circuit_data, dict):
            circuit_dict = circuit_data
        else:
            return None
        
        # Extraer QASM del diccionario
        qasm_str = circuit_dict.get('qasm')
        if qasm_str:
            return qasm_str
        
        # Si no hay QASM directo, intentar reconstruir desde otros formatos
        # Por ejemplo, si viene serializado de otra forma
        
        return None
        
    except Exception as e:
        print(f"Error extrayendo QASM del circuito: {e}")
        return None


# Registrar el blueprint en la aplicación principal
def register_ibm_quantum_routes(app):
    """
    Registra las rutas de IBM Quantum en la aplicación Flask.
    
    :param app: Aplicación Flask
    """
    app.register_blueprint(ibm_quantum_bp)
