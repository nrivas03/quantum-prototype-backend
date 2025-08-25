#!/usr/bin/env python3
"""
Ejemplo de uso de IBM Quantum con el prototipo.
Este script demuestra cómo ejecutar circuitos cuánticos en simuladores y hardware real de IBM.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from quantum_node.processor import QuantumProcessor
from config import Config


def create_bell_state_circuit():
    """
    Crea un circuito para generar el estado de Bell.
    
    :return: Circuito cuántico
    """
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Crear estado de Bell
    circuit.h(qr[0])
    circuit.cx(qr[0], qr[1])
    circuit.measure(qr, cr)
    
    return circuit


def create_ghz_state_circuit(num_qubits=3):
    """
    Crea un circuito para generar el estado GHZ.
    
    :param num_qubits: Número de qubits
    :return: Circuito cuántico
    """
    qr = QuantumRegister(num_qubits, 'q')
    cr = ClassicalRegister(num_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Crear estado GHZ
    circuit.h(qr[0])
    for i in range(1, num_qubits):
        circuit.cx(qr[0], qr[i])
    circuit.measure(qr, cr)
    
    return circuit


def create_qft_circuit(num_qubits=3):
    """
    Crea un circuito QFT.
    
    :param num_qubits: Número de qubits
    :return: Circuito cuántico
    """
    qr = QuantumRegister(num_qubits, 'q')
    cr = ClassicalRegister(num_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Aplicar QFT
    circuit.compose(QFT(num_qubits), inplace=True)
    circuit.measure(qr, cr)
    
    return circuit


def test_ibm_quantum_connection():
    """
    Prueba la conexión con IBM Quantum.
    """
    print("🔍 Probando conexión con IBM Quantum...")
    
    try:
        processor = QuantumProcessor(
            execution_type="simulator",
            backend_provider="ibm",
            backend_name="ibm_qasm_simulator"
        )
        
        if processor.validate_connection():
            print("✅ Conexión exitosa con IBM Quantum")
            return processor
        else:
            print("❌ Error de conexión con IBM Quantum")
            return None
            
    except Exception as e:
        print(f"❌ Error al inicializar IBM Quantum: {e}")
        return None


def test_simulator_execution(processor):
    """
    Prueba la ejecución en simulador.
    
    :param processor: Procesador cuántico configurado
    """
    print("\n🧪 Probando ejecución en simulador...")
    
    # Crear circuito de Bell
    bell_circuit = create_bell_state_circuit()
    print(f"Circuito Bell creado: {bell_circuit.num_qubits} qubits")
    
    # Ejecutar en simulador
    result = processor.execute(
        bell_circuit, 
        shots=1024,
        backend_name="ibm_qasm_simulator"
    )
    
    if result.get("success"):
        print("✅ Ejecución exitosa en simulador")
        print(f"   Job ID: {result.get('job_id', 'N/A')}")
        print(f"   Backend: {result.get('backend', 'N/A')}")
        print(f"   Shots: {result.get('shots', 'N/A')}")
        print(f"   Tiempo de ejecución: {result.get('execution_time', 'N/A'):.2f}s")
        print(f"   Conteos: {result.get('counts', {})}")
        print(f"   Probabilidades: {result.get('probabilities', {})}")
    else:
        print(f"❌ Error en ejecución: {result.get('error', 'Error desconocido')}")


def test_real_device_execution(processor):
    """
    Prueba la ejecución en dispositivo real (si está disponible).
    
    :param processor: Procesador cuántico configurado
    """
    print("\n🔬 Probando ejecución en dispositivo real...")
    
    # Obtener dispositivos reales disponibles
    real_devices = processor.get_available_real_devices()
    
    if not real_devices:
        print("⚠️  No hay dispositivos reales disponibles")
        return
    
    # Buscar un dispositivo operativo
    operational_device = None
    for device in real_devices:
        if device.get("operational") and device.get("pending_jobs", 0) < 10:
            operational_device = device
            break
    
    if not operational_device:
        print("⚠️  No hay dispositivos reales operativos disponibles")
        return
    
    print(f"📡 Usando dispositivo: {operational_device['name']}")
    
    # Crear circuito simple para dispositivo real
    simple_circuit = create_bell_state_circuit()
    
    # Ejecutar en dispositivo real
    result = processor.execute(
        simple_circuit,
        shots=100,  # Menos shots para dispositivo real
        backend_name=operational_device['name']
    )
    
    if result.get("success"):
        print("✅ Ejecución exitosa en dispositivo real")
        print(f"   Job ID: {result.get('job_id', 'N/A')}")
        print(f"   Backend: {result.get('backend', 'N/A')}")
        print(f"   Shots: {result.get('shots', 'N/A')}")
        print(f"   Tiempo de ejecución: {result.get('execution_time', 'N/A'):.2f}s")
        print(f"   Conteos: {result.get('counts', {})}")
    else:
        print(f"❌ Error en ejecución: {result.get('error', 'Error desconocido')}")


def test_batch_execution(processor):
    """
    Prueba la ejecución en lote.
    
    :param processor: Procesador cuántico configurado
    """
    print("\n📦 Probando ejecución en lote...")
    
    # Crear múltiples circuitos
    circuits = [
        create_bell_state_circuit(),
        create_ghz_state_circuit(3),
        create_qft_circuit(2)
    ]
    
    print(f"Creando {len(circuits)} circuitos para ejecución en lote...")
    
    # Ejecutar en lote
    result = processor.execute_batch(
        circuits,
        shots=512,
        backend_name="ibm_qasm_simulator"
    )
    
    if result.get("success"):
        print("✅ Ejecución en lote exitosa")
        print(f"   Job ID: {result.get('job_id', 'N/A')}")
        print(f"   Total circuitos: {result.get('total_circuits', 'N/A')}")
        print(f"   Tiempo total: {result.get('execution_time', 'N/A'):.2f}s")
        
        # Mostrar resultados individuales
        for i, batch_result in enumerate(result.get('batch_results', [])):
            print(f"   Circuito {i}: {batch_result.get('counts', {})}")
    else:
        print(f"❌ Error en ejecución en lote: {result.get('error', 'Error desconocido')}")


def list_available_backends(processor):
    """
    Lista los backends disponibles.
    
    :param processor: Procesador cuántico configurado
    """
    print("\n📋 Backends disponibles:")
    
    # Simuladores
    simulators = processor.get_available_simulators()
    print(f"   Simuladores ({len(simulators)}):")
    for sim in simulators:
        status = "✅" if sim.get("operational") else "❌"
        print(f"     {status} {sim['name']} ({sim.get('num_qubits', 'N/A')} qubits)")
    
    # Dispositivos reales
    real_devices = processor.get_available_real_devices()
    print(f"   Dispositivos reales ({len(real_devices)}):")
    for device in real_devices:
        status = "✅" if device.get("operational") else "❌"
        pending = device.get("pending_jobs", 0)
        print(f"     {status} {device['name']} ({device.get('num_qubits', 'N/A')} qubits, {pending} jobs pendientes)")


def main():
    """
    Función principal que ejecuta todas las pruebas.
    """
    print("🚀 Iniciando pruebas de IBM Quantum")
    print("=" * 50)
    
    # Verificar configuración
    if not Config.IBM_QUANTUM_TOKEN:
        print("❌ Error: IBM_QUANTUM_TOKEN no está configurado")
        print("   Por favor, configura tu token de IBM Quantum en el archivo .env")
        return
    
    # Probar conexión
    processor = test_ibm_quantum_connection()
    if not processor:
        return
    
    # Listar backends disponibles
    list_available_backends(processor)
    
    # Probar ejecución en simulador
    test_simulator_execution(processor)
    
    # Probar ejecución en dispositivo real
    test_real_device_execution(processor)
    
    # Probar ejecución en lote
    test_batch_execution(processor)
    
    print("\n🎉 Pruebas completadas")


if __name__ == "__main__":
    main()


