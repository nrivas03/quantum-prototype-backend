
# Quantum Prototype Backend

Este proyecto es un backend para manejar tareas híbridas cuántico-clásicas, utilizando `Flask` para exponer APIs, `SpinQit` para construir y ejecutar circuitos cuánticos, y una arquitectura modular que facilita la escalabilidad y la integración.

---

## 📋 Tabla de Contenidos
1. [Características](#características)
2. [Requisitos](#requisitos)
3. [Instalación](#instalación)
4. [Uso](#uso)
6. [API Endpoints](#api-endpoints)

---

## 🌟 Características

- Ejecución de circuitos cuánticos en simuladores y hardware físico.
- Arquitectura modular para facilitar la extensión.
- API REST para integraciones con aplicaciones frontend.
- Sincronización de tareas cuántico-clásicas.

---

## 🛠️ Requisitos

- Python 3.9 o superior
- Entorno virtual (opcional, recomendado)
- Dependencias listadas en `requirements.txt`

---

## 🧩 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/quantum-prototype-backend.git
   cd quantum-prototype-backend`` 

2.  Crea y activa un entorno virtual:
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows: venv\\Scripts\\activate``` 
3.  Instala las dependencias:
    
    ```bash
    pip install -r requirements.txt
----------

## 🚀 Uso

1.  Inicia el servidor:
    
    ```bash
    python run.py
2.  Accede a los endpoints desde Postman o un navegador en `http://127.0.0.1:5000`.
    

---------

## 🌐 API Endpoints

### **1. Operaciones Clásicas**

-   **URL:** `/classic/classic-operation`
-   **Método:** `POST`
-   **Ejemplo de Body (JSON):**
    
    ```json
    {
      "numbers": [1, 2, 3, 4, 5]
    }
-   **Respuesta Esperada:**
    
    ```json
	{
      "result": 15
    }
### **2. Operaciones Híbridas (Simulador)**

-   **URL:** `/hybrid/hybrid-operation`
-   **Método:** `POST`
-   **Ejemplo de Body (JSON):**
    
    ```json
    {
      "classicalData": {
        "factor": 2,
        "values": [1, 2, 3]
      },
      "quantumTask": {
        "taskId": "task123",
        "circuit": {
          "qubits": [0, 1],
          "operations": [
            {"gate": "H", "targets": [{"qId": 0}]},
            {"gate": "CX", "controls": [{"qId": 0}], "targets": [{"qId": 1}]},
            {"gate": "Measure", "targets": [{"qId": 0}]}
          ]
        },
        "executionType": "simulator"
      }
    } 
-   **Respuesta Esperada:**
    
    ```json
    {
      "processedClassicalData": [2, 4, 6],
      "quantumResult": {
        "task": {
          "taskId": "task123",
          "circuit": {
            "qubits": [0, 1],
            "operations": [
              {"gate": "H", "targets": [{"qId": 0}]},
              {"gate": "CX", "controls": [{"qId": 0}], "targets": [{"qId": 1}]},
              {"gate": "Measure", "targets": [{"qId": 0}]}
            ]
          },
          "executionType": "simulator"
        },
        "probabilities": {"00": 0.5, "01": 0.3, "10": 0.2}
      }
    }
----------
### **3. Operaciones Híbridas (Simulador)**

-   **URL:** `/hybrid/hybrid-operation`
-   **Método:** `POST`
-   **Ejemplo de Body (JSON):**
    
    ```json
    {
      "classicalData": {
        "factor": 2,
        "values": [1, 2, 3]
      },
      "quantumTask": {
        "taskId": "task123",
        "circuit": {
          "qubits": [0, 1],
          "operations": [
            {"gate": "H", "targets": [{"qId": 0}]},
            {"gate": "CX", "controls": [{"qId": 0}], "targets": [{"qId": 1}]},
            {"gate": "Measure", "targets": [{"qId": 0}]}
          ]
        },
        "executionType": "physical"
      }
    } 
-   **Respuesta Esperada:**
    
    ```json
    {
      "processedClassicalData": [2, 4, 6],
      "quantumResult": {
        "task": {
          "taskId": "task123",
          "circuit": {
            "qubits": [0, 1],
            "operations": [
              {"gate": "H", "targets": [{"qId": 0}]},
              {"gate": "CX", "controls": [{"qId": 0}], "targets": [{"qId": 1}]},
              {"gate": "Measure", "targets": [{"qId": 0}]}
            ]
          },
          "executionType": "physical"
        },
        "probabilities": {"00": 0.5, "01": 0.3, "10": 0.2}
      }
    }
----------

