import sqlite3
import os
from langchain_ollama import OllamaLLM

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, '..', 'data', 'titanic_data.db')

llm = OllamaLLM(model="llama3")

def get_db_schema():
    """Descubrimiento dinámico de metadatos para escalabilidad."""
    if not os.path.exists(db_path):
        return "Base de datos no encontrada."
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Busca todas las tablas activas (incluyendo las subidas por el usuario)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_desc = "ESTRUCTURA DISPONIBLE:\n"
    for table in tables:
        t_name = table[0]
        cursor.execute(f"PRAGMA table_info({t_name});")
        cols = [c[1] for c in cursor.fetchall()]
        schema_desc += f"- Tabla '{t_name}': {', '.join(cols)}\n"
    
    conn.close()
    return schema_desc

def get_sql_query(user_question):
    schema = get_db_schema()
    
    prompt = f"""
    Eres un experto en SQLite. Genera consultas precisas basadas en este esquema:
    {schema}
    
    INSTRUCCIONES:
    1. Retorna ÚNICAMENTE el código SQL plano.
    2. NO uses bloques de código Markdown (```sql ... ```).
    3. NO uses comillas invertidas (`) alrededor de la consulta.
    4. Termina la consulta con un punto y coma (;).
    
    Pregunta: {user_question}
    SQL:"""
    
    response = llm.invoke(prompt)
    
    # LIMPIEZA ROBUSTA: Eliminamos backticks y espacios innecesarios
    clean_query = response.strip().replace("```sql", "").replace("```", "").replace("`", "")
    
    # Si el modelo devuelve texto antes del SQL, intentamos tomar solo la parte del SELECT
    if "SELECT" in clean_query.upper():
        clean_query = clean_query[clean_query.upper().find("SELECT"):]
        
    return clean_query.strip()

def run_query(query):
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe. Ejecuta database.py primero.", None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        res = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        return res, cols
    except Exception as e:
        return str(e), None
    finally:
        conn.close()