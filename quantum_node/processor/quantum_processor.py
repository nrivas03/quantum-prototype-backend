from spinqit.qiskit.circuit import QuantumCircuit as SpinQCircuit
from spinqit import get_compiler, get_nmr, get_basic_simulator, NMRConfig
from qiskit import QuantumCircuit
from quantum_node.backends import IBMQuantumBackend
from config import Config


class QuantumProcessor:
    """
    Procesador cuántico para ejecutar circuitos en hardware físico o simuladores.
    Soporta tanto SpinQ como IBM Quantum backends.
    """

    def __init__(self, execution_type="simulator", backend_provider="spinq", backend_name=None):
        """
        Inicializa el procesador con el tipo de ejecución deseado.

        :param execution_type: 'simulator' para simulación, 'physical' para hardware físico, 'ibm' para IBM Quantum.
        :param backend_provider: 'spinq' para SpinQ, 'ibm' para IBM Quantum.
        :param backend_name: Nombre específico del backend (para IBM Quantum).
        """
        self.execution_type = execution_type
        self.backend_provider = backend_provider
        self.backend_name = backend_name

        # Configuración para SpinQ
        self.compiler = None
        self.engine = None
        self.spinq_config = None

        # Configuración para IBM Quantum
        self.ibm_backend = None

        self._initialize_backend()

    def _initialize_backend(self):
        """
        Inicializa el backend según el proveedor especificado.
        """
        if self.backend_provider == "spinq":
            self._initialize_spinq_backend()
        elif self.backend_provider == "ibm":
            self._initialize_ibm_backend()
        else:
            raise ValueError("Proveedor de backend inválido. Use 'spinq' o 'ibm'.")

    def _initialize_spinq_backend(self):
        """
        Inicializa el backend de SpinQ.
        """
        self.compiler = get_compiler("qiskit")
        self.spinq_config = NMRConfig()

        if self.execution_type == "simulator":
            print("Conectando con simulador cuántico SpinQ...")
            self.engine = get_basic_simulator()
            self.spinq_config.configure_shots(1024)
        elif self.execution_type == "physical":
            print("Conectando con hardware físico SpinQ...")
            self.engine = get_nmr()
            self.spinq_config.configure_shots(1024)
            self.spinq_config.configure_ip(Config.QUANTUM_ENGINE_IP)
            self.spinq_config.configure_port(Config.QUANTUM_ENGINE_PORT)
            self.spinq_config.configure_account(Config.QUANTUM_ACCOUNT_USER, Config.QUANTUM_ACCOUNT_PASSWORD)
            self.spinq_config.configure_task(Config.QUANTUM_TASK_NAME, Config.QUANTUM_TASK_NAME)
        else:
            raise ValueError("Tipo de ejecución inválido para SpinQ. Use 'simulator' o 'physical'.")

    def _initialize_ibm_backend(self):
        """
        Inicializa el backend de IBM Quantum.
        """
        print("Conectando con IBM Quantum...")
        self.ibm_backend = IBMQuantumBackend(
            token=Config.IBM_QUANTUM_TOKEN,
            instance=Config.IBM_QUANTUM_INSTANCE
        )

        # Configurar backend específico si se proporciona
        if self.backend_name:
            self.ibm_backend.set_backend(self.backend_name)
        elif Config.IBM_QUANTUM_DEFAULT_BACKEND:
            self.ibm_backend.set_backend(Config.IBM_QUANTUM_DEFAULT_BACKEND)

    def execute(self, circuit, shots=None, **kwargs):
        """
        Compila y ejecuta un circuito cuántico.

        :param circuit: Instancia de QuantumCircuit a ejecutar.
        :param shots: Número de disparos (opcional).
        :param kwargs: Argumentos adicionales específicos del backend.
        :return: Resultados de la ejecución en formato de diccionario.
        """
        if self.backend_provider == "spinq":
            return self._execute_spinq(circuit, shots, **kwargs)
        elif self.backend_provider == "ibm":
            return self._execute_ibm(circuit, shots, **kwargs)
        else:
            raise ValueError("Backend no configurado correctamente.")

    def _execute_spinq(self, circuit: SpinQCircuit, shots=None, **kwargs):
        """
        Ejecuta un circuito en SpinQ.

        :param circuit: Circuito SpinQ a ejecutar.
        :param shots: Número de disparos.
        :return: Resultados de la ejecución.
        """
        if shots:
            self.spinq_config.configure_shots(shots)

        executable = self.compiler.compile(circuit, 0)
        result = self.engine.execute(executable, self.spinq_config)

        return {
            "success": True,
            "backend_provider": "spinq",
            "backend_type": self.execution_type,
            "probabilities": result.probabilities,
            "shots": shots or 1024
        }

    def _execute_ibm(self, circuit: QuantumCircuit, shots=None, **kwargs):
        """
        Ejecuta un circuito en IBM Quantum.

        :param circuit: Circuito Qiskit a ejecutar.
        :param shots: Número de disparos.
        :param kwargs: Argumentos adicionales para IBM Quantum.
        :return: Resultados de la ejecución.
        """
        shots = shots or Config.IBM_QUANTUM_DEFAULT_SHOTS
        optimization_level = kwargs.get('optimization_level', Config.IBM_QUANTUM_OPTIMIZATION_LEVEL)
        backend_name = kwargs.get('backend_name', self.backend_name)
        use_session = kwargs.get('use_session', True)

        # Validar que el backend esté configurado
        if not self.ibm_backend:
            return {
                "success": False,
                "error": "Backend de IBM Quantum no está inicializado",
                "backend_provider": "ibm"
            }

        # Si se especifica un backend específico, configurarlo
        if backend_name and (not self.ibm_backend.current_backend or 
                           self.ibm_backend.current_backend.name != backend_name):
            if not self.ibm_backend.set_backend(backend_name):
                return {
                    "success": False,
                    "error": f"No se pudo configurar el backend {backend_name}",
                    "backend_provider": "ibm"
                }

        result = self.ibm_backend.execute_circuit(
            circuit=circuit,
            backend_name=backend_name,
            shots=shots,
            optimization_level=optimization_level,
            use_session=use_session
        )

        # Agregar información del proveedor
        result["backend_provider"] = "ibm"
        return result

    def get_backend_info(self):
        """
        Obtiene información del backend actual.

        :return: Información del backend.
        """
        if self.backend_provider == "spinq":
            return {
                "provider": "spinq",
                "execution_type": self.execution_type,
                "shots": getattr(self.spinq_config, 'shots', 1024) if self.spinq_config else 1024
            }
        elif self.backend_provider == "ibm":
            if self.ibm_backend and self.ibm_backend.current_backend:
                return self.ibm_backend.get_backend_info()
            else:
                return {"provider": "ibm", "error": "No hay backend configurado"}

        return {"error": "Backend no configurado"}

    def list_available_backends(self):
        """
        Lista los backends disponibles según el proveedor.

        :return: Lista de backends disponibles.
        """
        if self.backend_provider == "ibm":
            return self.ibm_backend.list_backends() if self.ibm_backend else {}
        elif self.backend_provider == "spinq":
            return {
                "spinq": {
                    "simulators": ["basic_simulator"],
                    "real_devices": ["nmr_device"]
                }
            }

        return {}

    def execute_batch(self, circuits, shots=None, **kwargs):
        """
        Ejecuta múltiples circuitos en lote.

        :param circuits: Lista de circuitos a ejecutar.
        :param shots: Número de disparos.
        :param kwargs: Argumentos adicionales.
        :return: Resultados de la ejecución en lote.
        """
        if self.backend_provider == "ibm":
            return self._execute_ibm_batch(circuits, shots, **kwargs)
        elif self.backend_provider == "spinq":
            return self._execute_spinq_batch(circuits, shots, **kwargs)
        else:
            raise ValueError("Backend no configurado correctamente.")

    def _execute_ibm_batch(self, circuits, shots=None, **kwargs):
        """
        Ejecuta múltiples circuitos en IBM Quantum.

        :param circuits: Lista de circuitos Qiskit.
        :param shots: Número de disparos.
        :param kwargs: Argumentos adicionales.
        :return: Resultados de la ejecución en lote.
        """
        shots = shots or Config.IBM_QUANTUM_DEFAULT_SHOTS
        optimization_level = kwargs.get('optimization_level', Config.IBM_QUANTUM_OPTIMIZATION_LEVEL)
        backend_name = kwargs.get('backend_name', self.backend_name)
        use_session = kwargs.get('use_session', True)

        if not self.ibm_backend:
            return {
                "success": False,
                "error": "Backend de IBM Quantum no está inicializado",
                "backend_provider": "ibm"
            }

        result = self.ibm_backend.execute_batch_circuits(
            circuits=circuits,
            backend_name=backend_name,
            shots=shots,
            optimization_level=optimization_level,
            use_session=use_session
        )

        result["backend_provider"] = "ibm"
        return result

    def _execute_spinq_batch(self, circuits, shots=None, **kwargs):
        """
        Ejecuta múltiples circuitos en SpinQ.

        :param circuits: Lista de circuitos SpinQ.
        :param shots: Número de disparos.
        :param kwargs: Argumentos adicionales.
        :return: Resultados de la ejecución en lote.
        """
        if shots:
            self.spinq_config.configure_shots(shots)

        results = []
        for i, circuit in enumerate(circuits):
            try:
                executable = self.compiler.compile(circuit, 0)
                result = self.engine.execute(executable, self.spinq_config)
                
                results.append({
                    "circuit_index": i,
                    "success": True,
                    "probabilities": result.probabilities,
                    "shots": shots or 1024
                })
            except Exception as e:
                results.append({
                    "circuit_index": i,
                    "success": False,
                    "error": str(e)
                })

        return {
            "success": True,
            "backend_provider": "spinq",
            "backend_type": self.execution_type,
            "total_circuits": len(circuits),
            "results": results
        }

    def get_available_simulators(self):
        """
        Obtiene lista de simuladores disponibles.

        :return: Lista de simuladores.
        """
        if self.backend_provider == "ibm":
            return self.ibm_backend.get_available_simulators() if self.ibm_backend else []
        elif self.backend_provider == "spinq":
            return [{"name": "basic_simulator", "provider": "spinq"}]
        return []

    def get_available_real_devices(self):
        """
        Obtiene lista de dispositivos reales disponibles.

        :return: Lista de dispositivos reales.
        """
        if self.backend_provider == "ibm":
            return self.ibm_backend.get_available_real_devices() if self.ibm_backend else []
        elif self.backend_provider == "spinq":
            return [{"name": "nmr_device", "provider": "spinq"}]
        return []

    def get_job_status(self, job_id):
        """
        Obtiene el estado de un trabajo.

        :param job_id: ID del trabajo.
        :return: Estado del trabajo.
        """
        if self.backend_provider == "ibm":
            return self.ibm_backend.get_job_status(job_id) if self.ibm_backend else {}
        return {"error": "Función no disponible para este proveedor"}

    def cancel_job(self, job_id):
        """
        Cancela un trabajo.

        :param job_id: ID del trabajo.
        :return: Resultado de la cancelación.
        """
        if self.backend_provider == "ibm":
            return self.ibm_backend.cancel_job(job_id) if self.ibm_backend else {}
        return {"error": "Función no disponible para este proveedor"}

    def validate_connection(self):
        """
        Valida la conexión con el backend.

        :return: True si la conexión es válida.
        """
        if self.backend_provider == "ibm":
            return self.ibm_backend.validate_connection() if self.ibm_backend else False
        elif self.backend_provider == "spinq":
            return self.engine is not None

        return False
