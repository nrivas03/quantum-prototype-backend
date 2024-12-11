class QuantumTask:
    """
    Representa una tarea cuántica que será enviada al nodo cuántico.
    """

    def __init__(self, task_id, circuit, execution_type, metadata=None):
        """
        Inicializa una tarea cuántica.

        :param task_id: ID único de la tarea cuántica.
        :param circuit: Representación del circuito cuántico.
        :param execution_type: Tipo de ejecución ('simulator' o 'physical').
        :param metadata: Información adicional sobre la tarea (opcional).
        """
        self.task_id = task_id
        self.circuit = circuit
        self.execution_type = execution_type
        self.metadata = metadata or {}

    def to_dict(self):
        """
        Convierte la tarea cuántica en un diccionario.

        :return: Diccionario con la representación de la tarea.
        """
        return {
            "taskId": self.task_id,
            "circuit": self.circuit,
            "executionType": self.execution_type,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data):
        """
        Crea una instancia de QuantumTask desde un diccionario.

        :param data: Diccionario con los datos de la tarea.
        :return: Instancia de QuantumTask.
        """
        return QuantumTask(
            task_id=data.get("taskId"),
            circuit=data.get("circuit"),
            execution_type=data.get("executionType"),
            metadata=data.get("metadata", {}),
        )
