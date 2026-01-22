import streamlit as st
import pandas as pd
import sqlite3
import os
import shutil
from llm_engine import get_sql_query, run_query, db_path

st.set_page_config(page_title="Equilibrium AI Chat", layout="wide")

# --- CONFIGURACIÓN DE DATOS (SIDEBAR) ---
with st.sidebar:
    st.title("Data Input")
    # Aceptamos ahora archivos CSV y DB/SQLite
    uploaded_file = st.file_uploader("Carga tus datos (CSV o SQLite)", type=["csv", "db", "sqlite"])
    
    if uploaded_file is not None:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension == '.csv':
            try:
                # Intentamos primero con UTF-8 (estándar moderno)
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                # Si falla, intentamos con latin-1 (común en archivos de Excel/Spanish)
                uploaded_file.seek(0) # Reiniciamos el puntero del archivo
                df = pd.read_csv(uploaded_file, encoding='latin-1')
            
            # Limpieza de nombres de columnas
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            
            conn = sqlite3.connect(db_path)
            table_name = uploaded_file.name.split('.')[0]
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            st.success(f"CSV '{table_name}' cargado con éxito (manejando caracteres especiales).")
            
        elif file_extension in ['.db', '.sqlite']:
            # Lógica para archivos SQLite: Reemplazamos la DB actual con la subida
            with open(db_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Base de datos SQLite cargada con éxito.")
            
    else:
        st.info("Usando base de datos por defecto (Titanic).")

# --- LÓGICA DEL CHAT ---
st.title("Data Assistant Chat")
st.markdown("Consulta tus datos estructurados usando lenguaje natural.")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "df" in message:
            st.dataframe(message["df"])

# Entrada del usuario
if prompt := st.chat_input("¿Qué quieres saber de los pasajeros?"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del Asistente
    with st.chat_message("assistant"):
        with st.spinner("Generando SQL y consultando..."):
            sql_query = get_sql_query(prompt)
            results, columns = run_query(sql_query)
            
            response_text = f"He generado la siguiente consulta SQL:\n`{sql_query}`"
            st.markdown(response_text)
            
            if columns:
                df_results = pd.DataFrame(results, columns=columns)
                st.dataframe(df_results)
                # Guardar respuesta en el historial
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "df": df_results
                })
            else:
                st.error(f"Error: {results}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Hubo un error al ejecutar la consulta: {results}"
                })