#!/usr/bin/env python3
"""
Ejemplo para probar la implementación de IBM Quantum con arquitectura de servicios.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from classic_node.services.ibm_quantum_service import IBMQuantumService
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


def create_bell_state_qasm():
    """
    Crea un circuito de estado de Bell y retorna su QASM.
    
    :return: Código QASM del circuito
    """
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    circuit.h(qr[0])
    circuit.cx(qr[0], qr[1])
    circuit.measure(qr, cr)
    
    return circuit.qasm()


def main():
    """
    Función principal para probar la implementación.
    """
    print("🚀 Probando implementación de IBM Quantum")
    print("=" * 50)
    
    # Verificar configuración
    if not os.getenv("IBM_QUANTUM_TOKEN"):
        print("❌ Error: IBM_QUANTUM_TOKEN no está configurado")
        print("   Por favor, configura tu token de IBM Quantum en el archivo .env")
        return
    
    try:
        # Inicializar servicio
        print("🔧 Inicializando servicio de IBM Quantum...")
        service = IBMQuantumService()
        
        # Verificar disponibilidad
        print("\n🌐 Verificando disponibilidad...")
        if service.is_available():
            print("✅ Servicio disponible")
        else:
            print("❌ Servicio no disponible")
            return
        
        # Obtener estado de backends
        print("\n📋 Obteniendo estado de backends...")
        backend_status = service.get_backend_status()
        
        if backend_status.get("success"):
            print(f"   Simuladores: {backend_status['total_simulators']} (disponibles: {backend_status['available_simulators']})")
            print(f"   Dispositivos reales: {backend_status['total_real_devices']} (disponibles: {backend_status['available_real_devices']})")
            
            # Mostrar algunos backends
            backends = backend_status.get("backends", {})
            real_devices = backends.get("real_devices", [])
            
            if real_devices:
                print("\n   Dispositivos reales:")
                for device in real_devices[:3]:  # Mostrar solo los primeros 3
                    status = "✅" if device.get("available") else "❌"
                    queue_status = device.get("queue_status", "unknown")
                    print(f"     {status} {device['name']} - {device.get('num_qubits')} qubits - Cola: {queue_status} ({device.get('pending_jobs', 0)} trabajos)")
        else:
            print(f"❌ Error: {backend_status.get('error')}")
            return
        
        # Obtener backend recomendado
        print("\n🎯 Obteniendo backend recomendado...")
        recommendation = service.get_recommended_backend()
        
        if recommendation.get("success"):
            backend_name = recommendation["recommended_backend"]
            backend_type = recommendation["type"]
            reason = recommendation["reason"]
            print(f"   Recomendado: {backend_name} ({backend_type})")
            print(f"   Razón: {reason}")
            
            if backend_type == "real_device":
                pending_jobs = recommendation.get("pending_jobs", 0)
                queue_status = recommendation.get("queue_status", "unknown")
                print(f"   Cola: {queue_status} ({pending_jobs} trabajos)")
        else:
            print(f"❌ Error: {recommendation.get('error')}")
            return
        
        # Crear circuito de prueba
        print("\n🔬 Creando circuito de estado de Bell...")
        bell_qasm = create_bell_state_qasm()
        print("   Circuito creado (QASM):")
        print("   " + "\n   ".join(bell_qasm.split("\n")[:5]) + "...")
        
        # Ejecutar circuito
        print("\n⚡ Ejecutando circuito...")
        print("   NOTA: Esto puede tomar varios minutos dependiendo de la cola")
        
        result = service.execute_circuit(
            circuit_qasm=bell_qasm,
            shots=50  # Pocos shots para prueba rápida
        )
        
        if result.get("success"):
            print("✅ Ejecución exitosa!")
            print(f"   Job ID: {result.get('job_id')}")
            print(f"   Backend usado: {result.get('backend')}")
            print(f"   Shots: {result.get('shots')}")
            
            # Mostrar métricas de cola
            queue_metrics = result.get("queue_metrics", {})
            if queue_metrics:
                print("\n📊 Métricas de cola:")
                print(f"   Tiempo en cola: {queue_metrics.get('queue_time_seconds', 0):.2f} segundos")
                print(f"   Tiempo de ejecución: {queue_metrics.get('execution_time_seconds', 0):.2f} segundos")
                print(f"   Tiempo total: {queue_metrics.get('total_time_seconds', 0):.2f} segundos")
            
            # Mostrar resultados
            print("\n📈 Resultados:")
            counts = result.get("counts", {})
            probabilities = result.get("probabilities", {})
            
            for state, count in counts.items():
                prob = probabilities.get(state, 0)
                print(f"   |{state}⟩: {count} veces ({prob:.3f} probabilidad)")
            
            # Verificar estado de Bell
            if '00' in counts and '11' in counts:
                print("✅ Resultados consistentes con estado de Bell")
            else:
                print("⚠️  Resultados inesperados para estado de Bell")
        else:
            print(f"❌ Error en ejecución: {result.get('error')}")
        
        print("\n🎉 Prueba completada")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


