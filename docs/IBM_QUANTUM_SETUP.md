# Configuración y Uso de IBM Quantum

Este documento describe cómo configurar y usar IBM Quantum en el prototipo de computación cuántica híbrida.

## Requisitos Previos

1. **Cuenta de IBM Quantum**: Necesitas una cuenta en [IBM Quantum](https://quantum-computing.ibm.com/)
2. **Token de API**: Obtén tu token de API desde el dashboard de IBM Quantum
3. **Dependencias**: Asegúrate de tener instaladas las dependencias de Qiskit

## Configuración

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# Configuración de IBM Quantum
IBM_QUANTUM_TOKEN=tu_token_aqui
IBM_QUANTUM_INSTANCE=ibm-q/open/main
IBM_QUANTUM_CHANNEL=ibm_quantum
IBM_QUANTUM_DEFAULT_BACKEND=ibm_qasm_simulator
IBM_QUANTUM_DEFAULT_SHOTS=1024
IBM_QUANTUM_OPTIMIZATION_LEVEL=1
```

### 2. Obtener Token de IBM Quantum

1. Ve a [IBM Quantum](https://quantum-computing.ibm.com/)
2. Inicia sesión o crea una cuenta
3. Ve a "Account" → "API token"
4. Copia tu token y agrégalo al archivo `.env`

## Uso

### Ejecución de Circuitos Individuales

```python
from quantum_node.processor import QuantumProcessor
from qiskit import QuantumCircuit

# Crear procesador para IBM Quantum
processor = QuantumProcessor(
    execution_type="simulator",
    backend_provider="ibm",
    backend_name="ibm_qasm_simulator"
)

# Crear un circuito simple
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])

# Ejecutar el circuito
result = processor.execute(circuit, shots=1024)
print(result)
```

### Ejecución en Dispositivos Reales

```python
# Obtener dispositivos reales disponibles
real_devices = processor.get_available_real_devices()

# Ejecutar en un dispositivo real
if real_devices:
    device_name = real_devices[0]['name']
    result = processor.execute(
        circuit, 
        shots=100,  # Menos shots para dispositivos reales
        backend_name=device_name
    )
```

### Ejecución en Lote

```python
# Crear múltiples circuitos
circuits = [circuit1, circuit2, circuit3]

# Ejecutar en lote
result = processor.execute_batch(circuits, shots=512)
```

## API REST

### Endpoints Disponibles

#### Verificar Conexión
```bash
GET /api/ibm-quantum/health
```

#### Listar Backends
```bash
GET /api/ibm-quantum/backends
GET /api/ibm-quantum/backends/simulators
GET /api/ibm-quantum/backends/real-devices
```

#### Ejecutar Circuito
```bash
POST /api/ibm-quantum/execute
Content-Type: application/json

{
    "circuit": {
        "qasm": "OPENQASM 2.0; include \"qelib1.inc\"; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q -> c;"
    },
    "backend_name": "ibm_qasm_simulator",
    "shots": 1024,
    "optimization_level": 1
}
```

#### Ejecutar Circuitos en Lote
```bash
POST /api/ibm-quantum/execute/batch
Content-Type: application/json

{
    "circuits": [
        {"qasm": "..."},
        {"qasm": "..."}
    ],
    "shots": 512
}
```

#### Estado de Trabajo
```bash
GET /api/ibm-quantum/jobs/{job_id}/status
POST /api/ibm-quantum/jobs/{job_id}/cancel
```

## Backends Disponibles

### Simuladores
- `ibm_qasm_simulator`: Simulador QASM básico
- `ibm_statevector_simulator`: Simulador de vector de estado
- `ibm_density_matrix_simulator`: Simulador de matriz de densidad

### Dispositivos Reales
- `ibmq_manila`: 5 qubits
- `ibmq_lima`: 5 qubits
- `ibmq_belem`: 5 qubits
- `ibmq_quito`: 5 qubits
- Y otros dispositivos disponibles según tu cuenta

## Ejemplos

### Ejemplo 1: Estado de Bell

```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def create_bell_state():
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    circuit.h(qr[0])
    circuit.cx(qr[0], qr[1])
    circuit.measure(qr, cr)
    
    return circuit

# Ejecutar
bell_circuit = create_bell_state()
result = processor.execute(bell_circuit, shots=1024)
```

### Ejemplo 2: Estado GHZ

```python
def create_ghz_state(num_qubits=3):
    qr = QuantumRegister(num_qubits, 'q')
    cr = ClassicalRegister(num_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    circuit.h(qr[0])
    for i in range(1, num_qubits):
        circuit.cx(qr[0], qr[i])
    circuit.measure(qr, cr)
    
    return circuit

# Ejecutar
ghz_circuit = create_ghz_state(3)
result = processor.execute(ghz_circuit, shots=1024)
```

## Monitoreo y Debugging

### Verificar Conexión
```python
if processor.validate_connection():
    print("✅ Conexión exitosa con IBM Quantum")
else:
    print("❌ Error de conexión")
```

### Información del Backend
```python
backend_info = processor.get_backend_info()
print(f"Backend: {backend_info['name']}")
print(f"Qubits: {backend_info['num_qubits']}")
print(f"Operacional: {backend_info['operational']}")
```

### Estado de Trabajos
```python
job_status = processor.get_job_status("job_id_here")
print(f"Estado: {job_status['status']}")
```

## Solución de Problemas

### Error: "IBM Quantum token no encontrado"
- Verifica que el token esté configurado en el archivo `.env`
- Asegúrate de que el token sea válido y no haya expirado

### Error: "Backend no está operativo"
- Verifica el estado del backend usando `get_backend_info()`
- Intenta con un backend diferente
- Para dispositivos reales, verifica la cola de trabajos

### Error: "Error de conexión"
- Verifica tu conexión a internet
- Asegúrate de que el token sea válido
- Verifica que la instancia de IBM Quantum sea correcta

### Trabajos que tardan mucho
- Los dispositivos reales pueden tener colas largas
- Usa `get_job_status()` para monitorear el progreso
- Considera usar simuladores para desarrollo y pruebas

## Límites y Consideraciones

### Límites de Dispositivos Reales
- Número máximo de qubits por dispositivo
- Tiempo de coherencia limitado
- Colas de trabajos
- Costos asociados (para cuentas pagadas)

### Optimizaciones
- Usa `optimization_level` apropiado (0-3)
- Considera el número de shots según tus necesidades
- Usa sesiones para múltiples ejecuciones

### Seguridad
- Nunca compartas tu token de API
- Usa variables de entorno para configurar credenciales
- Considera usar cuentas separadas para desarrollo y producción


