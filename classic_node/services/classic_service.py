class ClassicService:
    """
    Servicio para manejar lógica de operaciones clásicas.
    """

    @staticmethod
    def process_classical_data(numbers):
        """
        Procesa una lista de números con lógica clásica.

        :param numbers: Lista de números a procesar.
        :return: Resultado del procesamiento (por ejemplo, suma).
        """
        if not isinstance(numbers, list):
            raise ValueError("Los datos deben ser una lista de números.")
        return sum(numbers)

    @staticmethod
    def transform_data_with_factor(data, factor=1):
        """
        Transforma datos clásicos aplicando un factor de multiplicación.

        :param data: Lista de números clásicos.
        :param factor: Factor de multiplicación.
        :return: Lista transformada.
        """
        if not isinstance(data, list):
            raise ValueError("Los datos deben ser una lista de números.")
        return [x * factor for x in data]
