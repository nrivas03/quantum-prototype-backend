class ResourceManager:
    """
    Gestiona los recursos necesarios para la ejecución de tareas híbridas.
    """

    def __init__(self):
        """
        Inicializa el gestor de recursos con recursos predeterminados.
        """
        self.resources = {
            "quantum_hardware": {"available": True, "tasks_in_progress": 0},
            "quantum_simulator": {"available": True, "tasks_in_progress": 0},
            "classical_resources": {"available": True, "tasks_in_progress": 0},
        }

    def allocate_resource(self, resource_type):
        """
        Asigna un recurso si está disponible.

        :param resource_type: Tipo de recurso a asignar ('quantum_hardware', 'quantum_simulator', 'classical_resources').
        :return: Booleano indicando si se pudo asignar el recurso.
        """
        resource = self.resources.get(resource_type)
        if resource and resource["available"]:
            resource["tasks_in_progress"] += 1
            if resource_type == "quantum_hardware" and resource["tasks_in_progress"] > 1:
                resource["available"] = False  # Limitar a una tarea cuántica por hardware
            return True
        return False

    def release_resource(self, resource_type):
        """
        Libera un recurso previamente asignado.

        :param resource_type: Tipo de recurso a liberar.
        """
        resource = self.resources.get(resource_type)
        if resource and resource["tasks_in_progress"] > 0:
            resource["tasks_in_progress"] -= 1
            resource["available"] = True

    def get_resource_status(self):
        """
        Retorna el estado actual de los recursos.

        :return: Diccionario con el estado de los recursos.
        """
        return self.resources
