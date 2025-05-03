import os
import psycopg2
from pydbml import PyDBML
import re
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

# Ruta absoluta a la carpeta 'logs' desde el script en 'scripts/'
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

log_file_path = os.path.join(LOGS_DIR, 'create_tables.log')

logging.basicConfig(
    filename=log_file_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    print(msg)
    logging.info(msg)

bucket_name = os.getenv("BUCKET_NAME")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

def main():
    dbml_path = os.path.join(os.path.dirname(__file__), '..', 'dbml', 'tables_diagram.txt')
    log(f"Usando archivo DBML en: {dbml_path}")

    # Leer archivo DBML
    with open(dbml_path, 'r') as f:
        dbml_text = f.read()

    dbml = PyDBML(dbml_text)

    statements = []

    # CREATE TABLE con DROP previo
    for table in dbml.tables:
        table_name = table.name
        statements.append(f'DROP TABLE IF EXISTS {table_name} CASCADE;')
        statements.append(table.sql)

    # Conectar a la base de datos
    conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    cur = conn.cursor()

    try:
        for stmt in statements:
            log(f"Ejecutando: {stmt}")
            cur.execute(stmt)
        conn.commit()
        log(f"✔️ {len(statements)} sentencias ejecutadas correctamente.")
    except Exception as e:
        conn.rollback()
        log(f"❌ ERROR: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
