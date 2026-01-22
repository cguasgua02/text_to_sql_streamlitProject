# Asistente Inteligente Text-to-SQL: Proyecto Equilibrium

Este proyecto es una solución integral de procesamiento de lenguaje natural (NLP) diseñada para democratizar el acceso a bases de datos estructuradas. Permite a usuarios realizar consultas complejas mediante lenguaje natural, transformándolas en código SQL ejecutable en tiempo real.

## 1. Arquitectura del Sistema
La solución utiliza una arquitectura de capas desacopladas para garantizar escalabilidad y flexibilidad.

* **Interfaz de Usuario (app.py):** Desarrollada en **Streamlit**, implementa una interfaz de chat interactiva con memoria de sesión y soporte para carga de archivos (CSV/SQLite).
* **Motor de Orquestación (llm_engine.py):** Utiliza **LangChain** para gestionar el flujo de trabajo, desde la recepción de la pregunta hasta la ejecución del SQL.
* **Capa de Abstracción de Datos (SQLAlchemy):** Actúa como el puente entre el código y la base de datos. Permite que el sistema sea agnóstico al motor (SQLite local o PostgreSQL remoto).
* **Descubrimiento de Metadatos:** Un módulo dinámico que interroga el esquema de la base de datos para inyectar contexto preciso en el prompt del LLM, reduciendo alucinaciones.



---

## 2. Motores de Inferencia (Dualidad Estratégica)
El sistema está diseñado para operar en dos modalidades según las necesidades de privacidad o potencia de cálculo:

1.  **Modelo Local (Llama 3):** Ejecutado mediante **Ollama**. Ideal para entornos que requieren soberanía absoluta de los datos y costo cero por token.
2.  **Modelo Cloud (Gemini 1.5 Pro):** Integrado vía API para casos de uso que requieren un razonamiento lógico superior en esquemas multitable complejos (como el dataset Spider).

---

## 3. Justificación Técnica y Escalabilidad

* **Soberanía de Datos:** El uso de **Llama 3** local permite procesar información sensible sin que esta salga del perímetro de seguridad de la empresa.
* **Conectividad Empresarial:** Gracias a **SQLAlchemy**, el asistente puede conectarse a bases de datos pesadas (PostgreSQL, BigQuery) mediante URIs de conexión sin modificar la lógica principal.
* **Robustez en Ingesta:** El pipeline de datos maneja errores comunes de codificación (UTF-8/Latin-1) y normaliza esquemas de archivos CSV dinámicamente.

---

## 4. Análisis de Riesgos y Mitigación

| Riesgo | Impacto | Mitigación |
| :--- | :--- | :--- |
| **Alucinaciones SQL** | Alto | Uso de **Metadata Discovery** para restringir el modelo a tablas y columnas existentes en tiempo real. |
| **Inyección SQL** | Medio | Ejecución de consultas mediante SQLAlchemy, lo que permite implementar políticas de solo lectura y parametrización. |
| **Latencia de Inferencia** | Bajo | Optimización de prompts (Few-shot prompting) para minimizar el tiempo de generación de respuesta. |

---

## 5. Requisitos y Librerías
Para asegurar el funcionamiento del sistema, se requieren las siguientes dependencias:

* `streamlit`: Interfaz de usuario.
* `sqlalchemy`: Abstracción de base de datos.
* `pandas`: Procesamiento de archivos CSV y visualización de resultados.
* `langchain-ollama`: Integración con Llama 3 local.
* `google-generativeai`: Acceso a la API de Gemini (Opcional para modo Cloud).
* `python-dotenv`: Gestión segura de API Keys mediante archivos `.env`.
* `psycopg2-binary`: Driver para conexiones remotas a PostgreSQL.

---

## 6. Instrucciones de Instalación y Uso

1.  **Preparar el entorno:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
2.  **Inicializar base de datos local:**
    ```bash
    python src/database.py
    ```
3.  **Configurar credenciales:**
    Cree un archivo `.env` en la raíz y añada su `GEMINI_API_KEY=tu_llave_aqui`.
4.  **Ejecutar la aplicación:**
    ```bash
    streamlit run src/app.py
    ```

---
**Postulante:** Cristian Guasgua  
**Institución:** Universidad San Francisco de Quito (USFQ)  
**Cargo:** Data Scientist / Ingeniero en Automatización