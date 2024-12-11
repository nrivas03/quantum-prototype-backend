class QuantumClassicalInterface:
    """
    Interfaz para la comunicación entre sistemas cuánticos y clásicos.
    """

    def execute_quantum_task(self, quantum_task):
        """
        Envía una tarea cuántica al nodo cuántico y obtiene los resultados.

        :param quantum_task: Instancia de QuantumTask que representa la tarea cuántica.
        :return: Resultado de la ejecución en forma de diccionario.
        """
        if not quantum_task:
            raise ValueError("La tarea cuántica es requerida.")

        # Simulación de comunicación con el nodo cuántico
        print(f"Enviando tarea cuántica al nodo: {quantum_task.to_dict()}")

        # Aquí es donde se comunicaría con el nodo cuántico real o simulador
        # Este ejemplo devuelve resultados simulados
        simulated_result = {
            "taskId": quantum_task.task_id,
            "probabilities": {"00": 0.5, "01": 0.3, "10": 0.2},
            "metadata": {"executionTime": "50ms"},
        }

        print(f"Resultado recibido del nodo cuántico: {simulated_result}")
        return simulated_result
