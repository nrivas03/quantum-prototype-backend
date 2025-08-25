#!/usr/bin/env python3
"""
Quantum Backend Benchmark Script

This script benchmarks the same quantum circuit across different backends:
1. Local simulator using SpinQit
2. Real hardware with SpinQit  
3. Real hardware with IBM Cloud

The script provides detailed timing and execution results for comparison.
"""

import time
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent))

# Qiskit imports
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister

# SpinQit imports
try:
    from spinqit.qiskit.circuit import QuantumCircuit as SpinQCircuit
    from spinqit import get_compiler, get_nmr, get_basic_simulator, NMRConfig
    SPINQIT_AVAILABLE = True
except ImportError:
    print("Warning: SpinQit not available. SpinQit benchmarks will be skipped.")
    SPINQIT_AVAILABLE = False

# Project imports
from quantum_node.processor.quantum_processor import QuantumProcessor
from classic_node.services.ibm_quantum_service import IBMQuantumService
from config.settings import Config


class QuantumBenchmark:
    """
    Comprehensive quantum backend benchmark suite.
    """
    
    def __init__(self, shots: int = 1024, optimization_level: int = 1):
        """
        Initialize the benchmark suite.
        
        :param shots: Number of shots for each execution
        :param optimization_level: Optimization level for transpilation
        """
        self.shots = shots
        self.optimization_level = optimization_level
        self.results = {}
        self.test_circuits = []
        
        # Initialize timestamp
        self.benchmark_start_time = datetime.now()
        
        print(f"🚀 Quantum Backend Benchmark Suite")
        print(f"📅 Started at: {self.benchmark_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Shots per execution: {shots}")
        print(f"⚡ Optimization level: {optimization_level}")
        print("=" * 60)
    
    def generate_test_circuits(self) -> List[Dict[str, Any]]:
        """
        Generate a set of test circuits (maximum 2 qubits).
        
        :return: List of test circuit definitions
        """
        circuits = []
        
        # Circuit 1: Simple Bell State (2 qubits)
        bell_circuit = QuantumCircuit(2, 2)
        bell_circuit.h(0)
        bell_circuit.cx(0, 1)
        bell_circuit.measure_all()
        
        circuits.append({
            "name": "Bell State",
            "description": "Creates a Bell state |00⟩ + |11⟩",
            "qiskit_circuit": bell_circuit,
            "expected_states": ["00", "11"],
            "complexity": "low"
        })
        
        # Circuit 2: Single Qubit Superposition
        superposition_circuit = QuantumCircuit(1, 1)
        superposition_circuit.h(0)
        superposition_circuit.measure_all()
        
        circuits.append({
            "name": "Single Qubit Superposition",
            "description": "Creates superposition |0⟩ + |1⟩",
            "qiskit_circuit": superposition_circuit,
            "expected_states": ["0", "1"],
            "complexity": "minimal"
        })
        
        # Circuit 3: Two-qubit phase circuit
        phase_circuit = QuantumCircuit(2, 2)
        phase_circuit.h(0)
        phase_circuit.h(1)
        phase_circuit.cz(0, 1)
        phase_circuit.measure_all()
        
        circuits.append({
            "name": "Two-Qubit Phase",
            "description": "Two qubits with controlled-Z gate",
            "qiskit_circuit": phase_circuit,
            "expected_states": ["00", "01", "10", "11"],
            "complexity": "medium"
        })
        
        self.test_circuits = circuits
        print(f"📋 Generated {len(circuits)} test circuits")
        return circuits
    
    def convert_to_spinq_circuit(self, qiskit_circuit: QuantumCircuit) -> Optional[SpinQCircuit]:
        """
        Convert a Qiskit circuit to SpinQ format.
        
        :param qiskit_circuit: Qiskit quantum circuit
        :return: SpinQ circuit or None if conversion fails
        """
        if not SPINQIT_AVAILABLE:
            return None
            
        try:
            # Create SpinQ circuit with same number of qubits
            num_qubits = qiskit_circuit.num_qubits
            spinq_circuit = SpinQCircuit(num_qubits)
            
            # Convert gates (basic conversion for common gates)
            for instruction in qiskit_circuit.data:
                gate = instruction.operation
                qubits = [qubit._index for qubit in instruction.qubits]
                
                if gate.name == 'h':
                    spinq_circuit.h(qubits[0])
                elif gate.name == 'cx':
                    spinq_circuit.cnot(qubits[0], qubits[1])
                elif gate.name == 'cz':
                    spinq_circuit.cz(qubits[0], qubits[1])
                elif gate.name == 'x':
                    spinq_circuit.x(qubits[0])
                elif gate.name == 'y':
                    spinq_circuit.y(qubits[0])
                elif gate.name == 'z':
                    spinq_circuit.z(qubits[0])
                elif gate.name == 'measure':
                    # SpinQ handles measurement differently
                    pass
                else:
                    print(f"Warning: Gate {gate.name} not supported in SpinQ conversion")
            
            return spinq_circuit
            
        except Exception as e:
            print(f"Error converting circuit to SpinQ format: {e}")
            return None
    
    def benchmark_spinq_simulator(self, circuit_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Benchmark execution on SpinQ local simulator.
        
        :param circuit_info: Circuit information dictionary
        :return: Benchmark results
        """
        print(f"🔬 Testing SpinQ Simulator: {circuit_info['name']}")
        
        if not SPINQIT_AVAILABLE:
            return {
                "success": False,
                "error": "SpinQit library not available",
                "backend": "spinq_simulator"
            }
        
        try:
            # Convert circuit to SpinQ format
            spinq_circuit = self.convert_to_spinq_circuit(circuit_info['qiskit_circuit'])
            if not spinq_circuit:
                return {
                    "success": False,
                    "error": "Circuit conversion to SpinQ failed",
                    "backend": "spinq_simulator"
                }
            
            # Initialize SpinQ processor
            start_time = time.time()
            processor = QuantumProcessor(
                execution_type="simulator",
                backend_provider="spinq"
            )
            
            initialization_time = time.time() - start_time
            
            # Execute circuit
            execution_start = time.time()
            result = processor.execute(spinq_circuit, shots=self.shots)
            execution_time = time.time() - execution_start
            
            if result.get("success"):
                return {
                    "success": True,
                    "backend": "spinq_simulator",
                    "backend_type": "simulator",
                    "provider": "SpinQ",
                    "execution_time": round(execution_time, 3),
                    "initialization_time": round(initialization_time, 3),
                    "total_time": round(initialization_time + execution_time, 3),
                    "shots": self.shots,
                    "probabilities": result.get("probabilities", {}),
                    "counts": self._probabilities_to_counts(result.get("probabilities", {}), self.shots),
                    "circuit_info": {
                        "name": circuit_info["name"],
                        "complexity": circuit_info["complexity"],
                        "num_qubits": circuit_info["qiskit_circuit"].num_qubits
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown SpinQ simulator error"),
                    "backend": "spinq_simulator"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"SpinQ simulator execution failed: {str(e)}",
                "backend": "spinq_simulator"
            }
    
    def benchmark_spinq_hardware(self, circuit_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Benchmark execution on SpinQ real hardware.
        
        :param circuit_info: Circuit information dictionary
        :return: Benchmark results
        """
        print(f"🔧 Testing SpinQ Hardware: {circuit_info['name']}")
        
        if not SPINQIT_AVAILABLE:
            return {
                "success": False,
                "error": "SpinQit library not available",
                "backend": "spinq_hardware"
            }
        
        try:
            # Convert circuit to SpinQ format
            spinq_circuit = self.convert_to_spinq_circuit(circuit_info['qiskit_circuit'])
            if not spinq_circuit:
                return {
                    "success": False,
                    "error": "Circuit conversion to SpinQ failed",
                    "backend": "spinq_hardware"
                }
            
            # Initialize SpinQ processor for hardware with timeout protection
            start_time = time.time()
            
            # Use a timeout mechanism to prevent hanging
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("SpinQ hardware connection timeout")
            
            # Set timeout for hardware connection (30 seconds)
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            try:
                processor = QuantumProcessor(
                    execution_type="physical",
                    backend_provider="spinq"
                )
                
                initialization_time = time.time() - start_time
                
                # Execute circuit with timeout protection
                signal.alarm(60)  # 60 seconds for execution
                execution_start = time.time()
                result = processor.execute(spinq_circuit, shots=self.shots)
                execution_time = time.time() - execution_start
                
                # Clear timeout
                signal.alarm(0)
                
                if result.get("success"):
                    return {
                        "success": True,
                        "backend": "spinq_hardware",
                        "backend_type": "real_device",
                        "provider": "SpinQ",
                        "execution_time": round(execution_time, 3),
                        "initialization_time": round(initialization_time, 3),
                        "total_time": round(initialization_time + execution_time, 3),
                        "shots": self.shots,
                        "probabilities": result.get("probabilities", {}),
                        "counts": self._probabilities_to_counts(result.get("probabilities", {}), self.shots),
                        "circuit_info": {
                            "name": circuit_info["name"],
                            "complexity": circuit_info["complexity"],
                            "num_qubits": circuit_info["qiskit_circuit"].num_qubits
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Unknown SpinQ hardware error"),
                        "backend": "spinq_hardware"
                    }
            
            except TimeoutError as te:
                signal.alarm(0)  # Clear timeout
                return {
                    "success": False,
                    "error": f"SpinQ hardware connection/execution timeout: {str(te)}",
                    "backend": "spinq_hardware"
                }
                
        except Exception as e:
            # Clear any pending alarms
            try:
                signal.alarm(0)
            except:
                pass
            
            # Check if it's a connection error (hardware not available)
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['connect', 'timeout', 'server', 'connection']):
                return {
                    "success": False,
                    "error": f"SpinQ hardware not available (expected if device is off): {str(e)}",
                    "backend": "spinq_hardware",
                    "hardware_available": False
                }
            else:
                return {
                    "success": False,
                    "error": f"SpinQ hardware execution failed: {str(e)}",
                    "backend": "spinq_hardware"
                }
    
    def benchmark_ibm_quantum(self, circuit_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Benchmark execution on IBM Quantum.
        
        :param circuit_info: Circuit information dictionary
        :return: Benchmark results
        """
        print(f"☁️  Testing IBM Quantum: {circuit_info['name']}")
        
        try:
            # Initialize IBM Quantum service
            start_time = time.time()
            ibm_service = IBMQuantumService()
            
            if not ibm_service.is_available():
                return {
                    "success": False,
                    "error": "IBM Quantum service not available",
                    "backend": "ibm_quantum"
                }
            
            initialization_time = time.time() - start_time
            
            # Get circuit QASM
            circuit = circuit_info['qiskit_circuit']
            circuit_qasm = circuit.qasm()
            
            # Execute circuit
            execution_start = time.time()
            result = ibm_service.execute_circuit(
                circuit_qasm=circuit_qasm,
                shots=self.shots,
                optimization_level=self.optimization_level
            )
            execution_time = time.time() - execution_start
            
            if result.get("success"):
                return {
                    "success": True,
                    "backend": result.get("backend", "ibm_quantum"),
                    "backend_type": "real_device" if "simulator" not in result.get("backend", "").lower() else "simulator",
                    "provider": "IBM Quantum",
                    "job_id": result.get("job_id"),
                    "execution_time": result.get("execution_time", execution_time),
                    "queue_time": result.get("queue_time", "N/A"),
                    "ibm_execution_time": result.get("ibm_execution_time", "N/A"),
                    "quantum_seconds": result.get("quantum_seconds", "N/A"),
                    "initialization_time": round(initialization_time, 3),
                    "total_time": round(initialization_time + execution_time, 3),
                    "shots": self.shots,
                    "counts": result.get("counts", {}),
                    "probabilities": result.get("probabilities", {}),
                    "timing_info": result.get("timing_info", {}),
                    "detailed_metrics": result.get("detailed_metrics", {}),
                    "circuit_info": {
                        "name": circuit_info["name"],
                        "complexity": circuit_info["complexity"],
                        "num_qubits": circuit_info["qiskit_circuit"].num_qubits,
                        "optimization_level": self.optimization_level
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown IBM Quantum error"),
                    "backend": "ibm_quantum"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"IBM Quantum execution failed: {str(e)}",
                "backend": "ibm_quantum"
            }
    
    def _probabilities_to_counts(self, probabilities: Dict[str, float], shots: int) -> Dict[str, int]:
        """
        Convert probabilities to approximate counts.
        
        :param probabilities: Probability distribution
        :param shots: Number of shots
        :return: Approximate counts
        """
        return {state: int(prob * shots) for state, prob in probabilities.items()}
    
    def run_benchmark(self) -> Dict[str, Any]:
        """
        Run the complete benchmark suite.
        
        :return: Complete benchmark results
        """
        print("🏁 Starting comprehensive quantum backend benchmark...")
        
        # Generate test circuits
        circuits = self.generate_test_circuits()
        
        # Initialize results structure
        benchmark_results = {
            "metadata": {
                "timestamp": self.benchmark_start_time.isoformat(),
                "shots": self.shots,
                "optimization_level": self.optimization_level,
                "total_circuits": len(circuits),
                "spinqit_available": SPINQIT_AVAILABLE
            },
            "circuits": {},
            "summary": {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "backends_tested": []
            }
        }
        
        # Test each circuit on each backend
        for circuit_info in circuits:
            circuit_name = circuit_info["name"]
            print(f"\n📊 Benchmarking circuit: {circuit_name}")
            print(f"   Description: {circuit_info['description']}")
            print(f"   Qubits: {circuit_info['qiskit_circuit'].num_qubits}")
            print(f"   Complexity: {circuit_info['complexity']}")
            
            circuit_results = {
                "circuit_info": circuit_info,
                "backends": {}
            }
            
            # Test SpinQ Simulator
            if SPINQIT_AVAILABLE:
                spinq_sim_result = self.benchmark_spinq_simulator(circuit_info)
                circuit_results["backends"]["spinq_simulator"] = spinq_sim_result
                benchmark_results["summary"]["total_executions"] += 1
                if spinq_sim_result["success"]:
                    benchmark_results["summary"]["successful_executions"] += 1
                else:
                    benchmark_results["summary"]["failed_executions"] += 1
                
                if "spinq_simulator" not in benchmark_results["summary"]["backends_tested"]:
                    benchmark_results["summary"]["backends_tested"].append("spinq_simulator")
            
            # Test SpinQ Hardware
            if SPINQIT_AVAILABLE:
                spinq_hw_result = self.benchmark_spinq_hardware(circuit_info)
                circuit_results["backends"]["spinq_hardware"] = spinq_hw_result
                benchmark_results["summary"]["total_executions"] += 1
                if spinq_hw_result["success"]:
                    benchmark_results["summary"]["successful_executions"] += 1
                else:
                    benchmark_results["summary"]["failed_executions"] += 1
                
                if "spinq_hardware" not in benchmark_results["summary"]["backends_tested"]:
                    benchmark_results["summary"]["backends_tested"].append("spinq_hardware")
            
            # Test IBM Quantum
            ibm_result = self.benchmark_ibm_quantum(circuit_info)
            circuit_results["backends"]["ibm_quantum"] = ibm_result
            benchmark_results["summary"]["total_executions"] += 1
            if ibm_result["success"]:
                benchmark_results["summary"]["successful_executions"] += 1
            else:
                benchmark_results["summary"]["failed_executions"] += 1
            
            if "ibm_quantum" not in benchmark_results["summary"]["backends_tested"]:
                benchmark_results["summary"]["backends_tested"].append("ibm_quantum")
            
            circuit_results["backends"] = dict(circuit_results["backends"])
            benchmark_results["circuits"][circuit_name] = circuit_results
        
        # Calculate total benchmark time
        benchmark_end_time = datetime.now()
        total_benchmark_time = (benchmark_end_time - self.benchmark_start_time).total_seconds()
        
        benchmark_results["metadata"]["end_timestamp"] = benchmark_end_time.isoformat()
        benchmark_results["metadata"]["total_benchmark_time"] = round(total_benchmark_time, 2)
        
        self.results = benchmark_results
        return benchmark_results
    
    def print_detailed_results(self):
        """
        Print detailed benchmark results to console.
        """
        if not self.results:
            print("❌ No benchmark results available. Run benchmark first.")
            return
        
        print("\n" + "="*80)
        print("📊 QUANTUM BACKEND BENCHMARK RESULTS")
        print("="*80)
        
        metadata = self.results["metadata"]
        print(f"🕐 Start Time: {metadata['timestamp']}")
        print(f"🕐 End Time: {metadata['end_timestamp']}")
        print(f"⏱️  Total Benchmark Time: {metadata['total_benchmark_time']} seconds")
        print(f"🎯 Shots per execution: {metadata['shots']}")
        print(f"⚡ Optimization Level: {metadata['optimization_level']}")
        print(f"🔬 SpinQit Available: {metadata['spinqit_available']}")
        
        summary = self.results["summary"]
        print(f"\n📈 SUMMARY:")
        print(f"   Total Executions: {summary['total_executions']}")
        print(f"   Successful: {summary['successful_executions']}")
        print(f"   Failed: {summary['failed_executions']}")
        print(f"   Success Rate: {(summary['successful_executions']/summary['total_executions']*100):.1f}%")
        print(f"   Backends Tested: {', '.join(summary['backends_tested'])}")
        
        # Detailed results for each circuit
        for circuit_name, circuit_data in self.results["circuits"].items():
            print(f"\n🔬 CIRCUIT: {circuit_name}")
            print(f"   Description: {circuit_data['circuit_info']['description']}")
            print(f"   Qubits: {circuit_data['circuit_info']['qiskit_circuit'].num_qubits}")
            print(f"   Complexity: {circuit_data['circuit_info']['complexity']}")
            
            # Results for each backend
            for backend_name, backend_result in circuit_data["backends"].items():
                print(f"\n   🖥️  {backend_name.upper()}:")
                if backend_result["success"]:
                    print(f"      ✅ Status: SUCCESS")
                    print(f"      🏷️  Provider: {backend_result.get('provider', 'N/A')}")
                    print(f"      🔧 Backend Type: {backend_result.get('backend_type', 'N/A')}")
                    print(f"      ⏱️  Execution Time: {backend_result.get('execution_time', 'N/A')} seconds")
                    
                    if 'queue_time' in backend_result and backend_result['queue_time'] != 'N/A':
                        print(f"      ⏳ Queue Time: {backend_result['queue_time']} seconds")
                    
                    if 'quantum_seconds' in backend_result and backend_result['quantum_seconds'] != 'N/A':
                        print(f"      ⚛️  Quantum Seconds: {backend_result['quantum_seconds']}")
                    
                    print(f"      🎯 Shots: {backend_result.get('shots', 'N/A')}")
                    
                    # Show top measurement results
                    counts = backend_result.get('counts', {})
                    if counts:
                        print(f"      📊 Top Results:")
                        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
                        for state, count in sorted_counts[:3]:
                            percentage = (count / backend_result.get('shots', 1)) * 100
                            print(f"         |{state}⟩: {count} ({percentage:.1f}%)")
                    
                    if 'job_id' in backend_result:
                        print(f"      🆔 Job ID: {backend_result['job_id']}")
                        
                else:
                    print(f"      ❌ Status: FAILED")
                    print(f"      🚨 Error: {backend_result.get('error', 'Unknown error')}")
        
        print("\n" + "="*80)
    
    def save_results_to_file(self, filename: str = None):
        """
        Save benchmark results to JSON file.
        
        :param filename: Output filename (auto-generated if None)
        """
        if not self.results:
            print("❌ No benchmark results to save. Run benchmark first.")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quantum_benchmark_results_{timestamp}.json"
        
        try:
            # Convert circuit objects to serializable format
            serializable_results = self._make_serializable(self.results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def _make_serializable(self, obj):
        """
        Convert objects to JSON-serializable format.
        
        :param obj: Object to convert
        :return: Serializable object
        """
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if key == 'qiskit_circuit':
                    # Convert circuit to QASM string
                    result[key + '_qasm'] = value.qasm()
                    result[key + '_info'] = {
                        'num_qubits': value.num_qubits,
                        'num_clbits': value.num_clbits,
                        'depth': value.depth(),
                        'size': value.size()
                    }
                else:
                    result[key] = self._make_serializable(value)
            return result
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj


def main():
    """
    Main function to run the benchmark.
    """
    print("🚀 Quantum Backend Benchmark Suite")
    print("This script will test the same circuits across multiple quantum backends.")
    print()
    
    # Configuration
    shots = 1024
    optimization_level = 1
    
    # Create and run benchmark
    benchmark = QuantumBenchmark(shots=shots, optimization_level=optimization_level)
    
    try:
        # Run the benchmark
        results = benchmark.run_benchmark()
        
        # Print detailed results
        benchmark.print_detailed_results()
        
        # Save results to file
        benchmark.save_results_to_file()
        
        print(f"\n🎉 Benchmark completed successfully!")
        print(f"📊 Total executions: {results['summary']['total_executions']}")
        print(f"✅ Successful: {results['summary']['successful_executions']}")
        print(f"❌ Failed: {results['summary']['failed_executions']}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user.")
    except Exception as e:
        print(f"\n❌ Benchmark failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()