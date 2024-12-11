import threading


class TaskSynchronization:
    """
    Gestiona la sincronización de tareas cuántico-clásicas mediante hilos.
    """

    def __init__(self):
        """
        Inicializa un diccionario para rastrear el estado de las tareas.
        """
        self.task_status = {}
        self.lock = threading.Lock()

    def start_task(self, task_id):
        """
        Marca el inicio de una tarea.

        :param task_id: Identificador único de la tarea.
        """
        with self.lock:
            self.task_status[task_id] = "in_progress"

    def complete_task(self, task_id):
        """
        Marca una tarea como completada.

        :param task_id: Identificador único de la tarea.
        """
        with self.lock:
            if task_id in self.task_status:
                self.task_status[task_id] = "completed"

    def get_task_status(self, task_id):
        """
        Obtiene el estado actual de una tarea.

        :param task_id: Identificador único de la tarea.
        :return: Estado de la tarea ('in_progress', 'completed' o 'unknown').
        """
        with self.lock:
            return self.task_status.get(task_id, "unknown")
