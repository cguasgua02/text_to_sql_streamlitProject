# Asistente Inteligente Text-to-SQL: Proyecto Equilibrium

Este proyecto es una solución de Inteligencia Artificial Generativa diseñada para democratizar el acceso a datos estructurados. Permite a usuarios técnicos y no técnicos consultar bases de datos mediante lenguaje natural, transformando preguntas en consultas SQL ejecutables y visualizando resultados en tiempo real.

## 1. Diagrama de Flujo del Sistema

El flujo de información sigue un pipeline lineal y seguro para garantizar la precisión de la respuesta:

1.  **Entrada:** El usuario ingresa una pregunta en la interfaz de chat (Streamlit).
2.  **Extracción de Metadatos:** El sistema utiliza **SQLAlchemy** para leer el esquema actual de la base de datos (tablas y columnas).
3.  **Prompt Engineering:** Se construye un prompt que combina la pregunta del usuario con el esquema real para evitar alucinaciones.
4.  **Inferencia LLM:**
    * *Modo Local:* Llama 3 genera el código SQL (Privacidad).
    * *Modo Cloud:* Gemini 3 Flash procesa esquemas complejos (Potencia).
6.  **Limpieza y Ejecución:** Se eliminan caracteres de formato (backticks) y se ejecuta el SQL en el motor correspondiente.
7.  **Visualización:** Los resultados se presentan en tablas de datos interactivas dentro del chat.

---

## 2. Justificación de la Arquitectura

Se ha seleccionado una arquitectura modular basada en Python por las siguientes razones:

* **SQLAlchemy como Corazón:** Se utiliza como capa de abstracción para que el código sea agnóstico al motor. Esto permite que el asistente funcione hoy con **SQLite** para la prueba, pero sea compatible con **PostgreSQL**, **MySQL** o **BigQuery** mañana con solo cambiar una línea de configuración.
* **Dualidad Local/Cloud:** La implementación de **Llama 3 (vía Ollama)** responde a la necesidad de soberanía de datos, mientras que la integración de **APIs externas** asegura que el sistema pueda escalar a consultas multitable de alta complejidad que modelos pequeños no podrían resolver.
* **Streamlit para Prototipado Rápido:** Permite desplegar una herramienta funcional y estética en tiempo récord, enfocándose en la lógica de datos más que en el desarrollo frontend.

---

## 3. Análisis de Riesgos y Limitaciones

Durante el desarrollo y testeo, se identificaron y mitigaron los siguientes riesgos técnicos:

| Riesgo | Impacto | Mitigación Implementada |
| :--- | :--- | :--- |
| **Falta de Inicialización** | Medio | Manejo de excepciones que detecta si la base de datos existe e instruye al usuario a ejecutar `database.py`. |
| **Errores de Sintaxis (Backticks)** | Medio | Capa de post-procesamiento en `llm_engine.py` que limpia caracteres de formato Markdown antes de la ejecución. |
| **Latencia del LLM** | Bajo | Los modelos locales pueden tardar según el hardware; se recomienda el uso de GPUs o modelos cuantizados para mejorar el tiempo de respuesta. |
| **Costo de API** | Medio | El uso de modelos locales como Llama 3 elimina el costo por token, reservando las APIs pagas solo para tareas críticas. |
| **Alucinaciones** | Alto | Inyección estricta del esquema de la base de datos en el prompt para evitar que el LLM invente tablas o columnas inexistentes. |

---

## 4. Escalabilidad y Conexión con otros Proyectos

Esta solución ha sido diseñada para integrarse en el ecosistema de automatización de la empresa de las siguientes maneras:

1.  **Integración con n8n/Agentes:** El motor de `llm_engine.py` puede exponerse como una API propia para que agentes autónomos consulten bases de datos antes de tomar decisiones o responder a clientes.
2.  **Soporte de Big Data:** Al estar basado en SQLAlchemy, el sistema está listo para conectarse a almacenes de datos masivos como **BigQuery** o **Snowflake**, permitiendo el análisis de Giga/Terabytes de información desde el chat.
3.  **Multifuente:** La capacidad de subir archivos CSV y SQLite dinámicamente lo convierte en una herramienta de análisis *ad-hoc* para equipos de ventas o marketing que no tienen acceso directo a la infraestructura central.

---

## 5. Requisitos de Instalación

1.  **Entorno Virtual:** `python -m venv venv` y `pip install -r requirements.txt`.
2.  **Seguridad:** Configure su `GEMINI_API_KEY` en un archivo `.env` (ignore este archivo en Git).
3.  **Base de Datos:** Ejecute `python src/database.py` para crear el dataset semilla (Titanic).
4.  **Ejecución:** `streamlit run src/app.py`.

---
**Postulante:** Cristian Guasgua  
**Especialidad:** Data Science & Automation

