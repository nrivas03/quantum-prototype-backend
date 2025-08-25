# Quantum Prototype Backend

Un prototipo de backend para computación cuántica híbrida que integra múltiples proveedores cuánticos.

## Características

- **Múltiples Proveedores**: Soporte para SpinQ y IBM Quantum
- **Simuladores y Hardware Real**: Ejecución en simuladores y dispositivos físicos
- **API REST**: Interfaz REST completa para ejecutar circuitos cuánticos
- **Ejecución en Lote**: Soporte para ejecutar múltiples circuitos simultáneamente
- **Monitoreo**: Seguimiento de trabajos y estado de dispositivos

## Proveedores Soportados

### SpinQ
- Simulador básico
- Hardware físico NMR
- Configuración local

### IBM Quantum
- Simuladores QASM, Statevector, Density Matrix
- Dispositivos reales (ibmq_manila, ibmq_lima, etc.)
- Qiskit Runtime para optimizaciones

## Configuración Rápida

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
Copia `env.example` a `.env` y configura tus credenciales:

```bash
cp env.example .env
# Edita .env con tus credenciales
```

### 3. Verificar Configuración
```bash
python test_ibm_setup.py
```

### 4. Ejecutar Ejemplos
```bash
python examples/ibm_quantum_example.py
```

### 5. Iniciar Servidor
```bash
python run.py
```

## Uso

### Ejecución de Circuitos Individuales
```python
from quantum_node.processor import QuantumProcessor
from qiskit import QuantumCircuit

# Para IBM Quantum
processor = QuantumProcessor(
    execution_type="simulator",
    backend_provider="ibm",
    backend_name="ibm_qasm_simulator"
)

# Crear y ejecutar circuito
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])

result = processor.execute(circuit, shots=1024)
```

### API REST

#### Verificar Conexión
```bash
GET /api/ibm-quantum/health
```

#### Ejecutar Circuito
```bash
POST /api/ibm-quantum/execute
{
    "circuit": {
        "qasm": "OPENQASM 2.0; include \"qelib1.inc\"; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q -> c;"
    },
    "backend_name": "ibm_qasm_simulator",
    "shots": 1024
}
```

## Documentación

- [Configuración de IBM Quantum](docs/IBM_QUANTUM_SETUP.md)
- [API Reference](docs/API_REFERENCE.md)

## Estructura del Proyecto

```
quantum-prototype-backend/
├── classic_node/           # Nodo clásico (Flask API)
├── quantum_node/           # Nodo cuántico
│   ├── backends/          # Backends cuánticos
│   ├── processor/         # Procesador cuántico
│   └── middleware/        # Middleware
├── hybrid_managment/      # Gestión híbrida
├── quantum_classical_interface/  # Interfaz cuántico-clásico
├── config/               # Configuración
├── examples/             # Ejemplos de uso
├── docs/                 # Documentación
└── tests/                # Pruebas
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.