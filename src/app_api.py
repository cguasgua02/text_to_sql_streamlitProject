import streamlit as st
import pandas as pd
import sqlite3
import os
from llm_engine_api import get_sql_query, run_query, local_db_uri, db_path

st.set_page_config(page_title="Equilibrium AI Chat", layout="wide")

# --- BARRA LATERAL: GESTIÓN DE FUENTES ---
with st.sidebar:
    st.title("Configuración de Datos")
    
    # Opción de conectar a DB remota o usar local
    source_type = st.radio("Fuente de datos:", ["Local (CSV/SQLite)", "Remota (URI)"])
    
    current_uri = local_db_uri # Por defecto usamos la local

    if source_type == "Local (CSV/SQLite)":
        uploaded_file = st.file_uploader("Sube tu archivo", type=["csv", "db", "sqlite"])
        if uploaded_file:
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext == '.csv':
                try:
                    df = pd.read_csv(uploaded_file)
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                
                df.columns = [c.lower().replace(" ", "_") for c in df.columns]
                conn = sqlite3.connect(db_path)
                df.to_sql(uploaded_file.name.split('.')[0], conn, if_exists='replace', index=False)
                conn.close()
                st.success("CSV procesado.")
            else:
                with open(db_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("SQLite vinculado.")
    else:
        remote_uri = st.text_input("URI de conexión:", placeholder="postgresql://user:pass@host/db")
        if remote_uri:
            current_uri = remote_uri
            st.success("Conexión remota configurada.")

# --- INTERFAZ DE CHAT ---
st.title("Data Assistant (Gemini API)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "df" in msg: st.dataframe(msg["df"])

if prompt := st.chat_input("¿Qué deseas consultar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando al LLM..."):
            # Pasamos la URI actual (local o remota) al motor
            sql_query = get_sql_query(prompt, current_uri)
            st.markdown(f"**SQL Generado:**\n`{sql_query}`")
            
            results_df, columns = run_query(sql_query, current_uri)
            
            if columns:
                st.dataframe(results_df)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"SQL: `{sql_query}`", 
                    "df": results_df
                })
            else:
                st.error(f"Error: {results_df}")