from spinqit.qiskit.circuit import QuantumCircuit
from spinqit import get_compiler, get_basic_simulator, get_nmr, NMRConfig


class QuantumMiddleware:
    """
    Middleware para construir y ejecutar circuitos cuánticos.
    """

    @staticmethod
    def build_circuit(circuit_data):
        """
        Construye un circuito cuántico basado en los datos proporcionados.
        """
        num_qubits = len(circuit_data.get("qubits", []))
        qc = QuantumCircuit(num_qubits, num_qubits)

        for operation in circuit_data.get("operations", []):
            gate = operation["gate"]
            targets = [t["qId"] for t in operation["targets"]]

            if gate == "H":
                qc.h(targets[0])
            elif gate == "CX":
                controls = [c["qId"] for c in operation.get("controls", [])]
                qc.cx(controls[0], targets[0])
            elif gate == "X":
                if "controls" in operation:
                    controls = operation["controls"]
                    classical_bit = controls[0]["qId"]
                    qc.x(targets[0]).c_if(qc.clbits[classical_bit], 1)
                else:
                    qc.x(targets[0])
            elif gate == "SWAP":
                qc.swap(targets[0], targets[1])
            elif gate == "Measure":
                qc.measure(targets[0], targets[0])

        return qc

    @staticmethod
    def execute_circuit(circuit, execution_type):
        """
        Ejecuta el circuito cuántico en el simulador o hardware físico.
        """
        compiler = get_compiler("qiskit")

        if execution_type == "simulator":
            engine = get_basic_simulator()
            config = NMRConfig()
            config.configure_shots(1024)
        elif execution_type == "physical":
            engine = get_nmr()
            config = NMRConfig()
            config.configure_shots(1024)
            config.configure_ip("172.27.52.229")
            config.configure_port(8989)
            config.configure_account("SpinQ001", "123456")
            config.configure_task("QuantumTask", "QuantumTask")
        else:
            raise ValueError("Tipo de ejecución inválido. Use 'simulator' o 'physical'.")

        executable = compiler.compile(circuit, 0)
        result = engine.execute(executable, config)
        return {"probabilities": result.probabilities}
