from classic_node.models import QuantumTask, QuantumResult
from quantum_classical_interface import QuantumClassicalInterface

class ExecutionManager:
    """
    Gestiona la ejecución de tareas híbridas cuántico-clásicas.
    """

    @staticmethod
    def execute_hybrid_task(classical_data, quantum_task_data):
        """
        Coordina la ejecución de una tarea híbrida.

        :param classical_data: Datos clásicos para procesar.
        :param quantum_task_data: Información de la tarea cuántica.
        :return: Resultado combinado de la ejecución híbrida.
        """
        if not classical_data or not quantum_task_data:
            raise ValueError("Los datos clásicos y la tarea cuántica son requeridos.")

        # Procesar datos clásicos (ejemplo: escalar valores por un factor)
        factor = classical_data.get("factor", 1)
        processed_classical = [
            x * factor for x in classical_data.get("values", [])
        ]

        # Crear una instancia de QuantumTask
        quantum_task = QuantumTask.from_dict(quantum_task_data)

        # Enviar la tarea cuántica al nodo cuántico
        quantum_interface = QuantumClassicalInterface()
        quantum_result_data = quantum_interface.execute_quantum_task(quantum_task)

        # Crear una instancia de QuantumResult a partir de los datos recibidos
        quantum_result = QuantumResult.from_dict(quantum_result_data)

        # Combinar los resultados
        combined_result = {
            "processedClassicalData": processed_classical,
            "quantumResult": quantum_result.to_dict(),
        }

        return combined_result

    @staticmethod
    def execute_quantum_only_task(quantum_task_data):
        """
        Coordina la ejecución de una tarea exclusivamente cuántica.

        :param quantum_task_data: Información de la tarea cuántica.
        :return: Resultado de la ejecución cuántica.
        """
        if not quantum_task_data:
            raise ValueError("La tarea cuántica es requerida.")

        # Crear una instancia de QuantumTask
        quantum_task = QuantumTask.from_dict(quantum_task_data)

        # Enviar la tarea cuántica al nodo cuántico
        quantum_interface = QuantumClassicalInterface()
        quantum_result_data = quantum_interface.execute_quantum_task(quantum_task)

        # Crear una instancia de QuantumResult
        quantum_result = QuantumResult.from_dict(quantum_result_data)

        return quantum_result.to_dict()
