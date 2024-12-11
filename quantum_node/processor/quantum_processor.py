from spinqit.qiskit.circuit import QuantumCircuit
from spinqit import get_compiler, get_nmr, get_basic_simulator, NMRConfig


class QuantumProcessor:
    """
    Procesador cuántico para ejecutar circuitos en hardware físico o simuladores.
    """

    def __init__(self, execution_type="simulator"):
        """
        Inicializa el procesador con el tipo de ejecución deseado.

        :param execution_type: 'simulator' para simulación, 'physical' para hardware físico.
        """
        self.execution_type = execution_type
        self.compiler = get_compiler("qiskit")
        self.engine = None
        self.config = NMRConfig()

        if self.execution_type == "simulator":
            print("Conectando con simulador cuántico...")
            self.engine = get_basic_simulator()
            self.config.configure_shots(1024)
        elif self.execution_type == "physical":
            print("Conectando con hardware físico...")
            self.engine = get_nmr()
            self.config.configure_shots(1024)
            self.config.configure_ip("172.27.52.229")
            self.config.configure_port(8989)
            self.config.configure_account("SpinQ001", "123456")
            self.config.configure_task("QuantumTask", "QuantumTask")
        else:
            raise ValueError("Tipo de ejecución inválido. Use 'simulator' o 'physical'.")

    def execute(self, circuit: QuantumCircuit):
        """
        Compila y ejecuta un circuito cuántico.

        :param circuit: Instancia de QuantumCircuit a ejecutar.
        :return: Resultados de la ejecución en formato de diccionario.
        """
        executable = self.compiler.compile(circuit, 0)
        result = self.engine.execute(executable, self.config)

        return {"probabilities": result.probabilities}
