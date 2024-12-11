from classic_node.models import QuantumTask, QuantumResult
from quantum_classical_interface import QuantumClassicalInterface
from quantum_node.middleware import QuantumMiddleware


class HybridTaskService:
    """
    Servicio para manejar tareas híbridas cuántico-clásicas.
    """

    @staticmethod
    def process_hybrid_task(classical_data, quantum_task_data):
        """
        Procesa una tarea híbrida, combinando lógica clásica y cuántica.
        """
        # Procesar datos clásicos
        factor = classical_data.get("factor", 1)
        processed_classical = [x * factor for x in classical_data.get("values", [])]

        # Crear modelo de QuantumTask
        quantum_task = QuantumTask.from_dict(quantum_task_data)

        # Construir y ejecutar el circuito cuántico
        middleware = QuantumMiddleware()
        circuit = middleware.build_circuit(quantum_task.circuit)
        quantum_result_data = middleware.execute_circuit(circuit, quantum_task.execution_type)

        # Crear modelo de QuantumResult
        quantum_result = QuantumResult.from_dict({
            "taskId": quantum_task.task_id,
            "probabilities": quantum_result_data["probabilities"]
        })

        # Combinar resultados
        return {
            "processedClassicalData": processed_classical,
            "quantumResult": quantum_result.to_dict()
        }
