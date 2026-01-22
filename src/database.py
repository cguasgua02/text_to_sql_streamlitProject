import sqlite3
import pandas as pd
import os

def setup_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', 'data')
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    db_path = os.path.join(data_dir, 'titanic_data.db')

    # Dataset público por defecto (Titanic) para asegurar operatividad inicial
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.lower() for c in df.columns] 
        conn = sqlite3.connect(db_path)
        # Se guarda como tabla 'pasajeros'
        df.to_sql('pasajeros', conn, if_exists='replace', index=False)
        conn.close()
        print(f"Entorno inicializado en: {db_path}")
    except Exception as e:
        print(f"Error al inicializar: {e}")

if __name__ == "__main__":
    setup_database()