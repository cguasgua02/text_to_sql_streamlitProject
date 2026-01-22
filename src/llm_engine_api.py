import os
import sqlite3
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

# 1. Configuración de Entorno y API
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No se encontró la GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=api_key)
# Usamos Gemini por su alta precisión en generación de código SQL
model = genai.GenerativeModel('gemini-3-flash-preview')

# 2. Configuración de Rutas para Base de Datos Local
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, '..', 'data', 'titanic_data.db')
# URI estándar para SQLAlchemy (compatible con SQLite local)
local_db_uri = f'sqlite:///{db_path}'

def get_db_schema(db_uri=local_db_uri):
    """
    Extrae dinámicamente el esquema de cualquier base de datos (Local o Remota).
    Esto permite que el LLM 'vea' la estructura actual de los datos.
    """
    try:
        engine = create_engine(db_uri)
        inspector = inspect(engine)
        schema_desc = "ESTRUCTURA DE LA BASE DE DATOS:\n"
        
        for table_name in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns(table_name)]
            schema_desc += f"- Tabla '{table_name}': {', '.join(columns)}\n"
        return schema_desc
    except Exception as e:
        return f"Error al obtener el esquema: {str(e)}"

def get_sql_query(user_question, db_uri=local_db_uri):
    """
    Envía la pregunta y el esquema a la API para generar la consulta SQL.
    """
    schema = get_db_schema(db_uri)
    
    prompt = f"""
    Eres un experto en Ciencia de Datos y SQL. Tu tarea es convertir preguntas en lenguaje natural 
    en consultas SQL válidas basadas estrictamente en el siguiente esquema:

    {schema}
    
    INSTRUCCIONES:
    1. Retorna ÚNICAMENTE el código SQL plano.
    2. No uses bloques de código Markdown (```sql), ni comillas invertidas (`).
    3. Si el usuario pide sobrevivientes o fallecidos en el Titanic, recuerda que 'survived' (1=Sí, 0=No).
    4. Asegúrate de que los nombres de tablas y columnas coincidan exactamente con el esquema.

    PREGUNTA DEL USUARIO: {user_question}
    SQL:"""

    try:
        response = model.generate_content(prompt)
        # Limpieza de seguridad para evitar caracteres de formato que rompan SQLite
        clean_query = response.text.strip().replace("```sql", "").replace("```", "").replace("`", "")
        
        # Validación mínima: Si el LLM devuelve texto explicativo, extraemos solo el SELECT
        if "SELECT" in clean_query.upper():
            clean_query = clean_query[clean_query.upper().find("SELECT"):]
            
        return clean_query.split(';')[0] + ';' # Aseguramos un solo punto y coma final
    except Exception as e:
        return f"-- Error al generar SQL: {str(e)}"

def run_query(query, db_uri=local_db_uri):
    """
    Ejecuta la consulta generada en la base de datos y devuelve los resultados en un DataFrame.
    """
    engine = create_engine(db_uri)
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
            return df, list(df.columns)
    except Exception as e:
        return str(e), None