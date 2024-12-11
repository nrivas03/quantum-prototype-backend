class QuantumResult:
    """
    Representa los resultados de una operación cuántica.
    """

    def __init__(self, task_id, probabilities, metadata=None):
        """
        Inicializa un resultado cuántico.

        :param task_id: ID único de la tarea cuántica.
        :param probabilities: Diccionario con las probabilidades de los estados cuánticos.
        :param metadata: Información adicional sobre la ejecución (opcional).
        """
        self.task_id = task_id
        self.probabilities = probabilities
        self.metadata = metadata or {}

    def to_dict(self):
        """
        Convierte el resultado cuántico en un diccionario.

        :return: Diccionario con la representación del resultado.
        """
        return {
            "taskId": self.task_id,
            "probabilities": self.probabilities,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data):
        """
        Crea una instancia de QuantumResult desde un diccionario.

        :param data: Diccionario con los datos del resultado.
        :return: Instancia de QuantumResult.
        """
        return QuantumResult(
            task_id=data.get("taskId"),
            probabilities=data.get("probabilities"),
            metadata=data.get("metadata", {}),
        )
