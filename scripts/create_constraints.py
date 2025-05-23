import os
import psycopg2
from pydbml import PyDBML
import re
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Absolute path to the 'logs' directory from the script in 'scripts/'
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

log_file_path = os.path.join(LOGS_DIR, 'create_constraints.log')

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
    log(f"Using DBML file: {dbml_path}")

    # Read DBML file
    with open(dbml_path, 'r') as f:
        dbml_text = f.read()

    dbml = PyDBML(dbml_text)

    statements = []

    # FOREIGN KEYS
    for line in dbml_text.splitlines():
        if line.startswith('Ref:'):
            ref_line = line.replace('Ref:', '').strip()
            left, right = re.split(r'[>-]', ref_line, maxsplit=1)
            table1, column1 = left.strip().split('.')
            table2, column2 = right.strip().split('.')
            statements.append(
                f'ALTER TABLE {table1} ADD FOREIGN KEY ({column1}) REFERENCES {table2}({column2});'
            )

    # Connect to the database
    conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    cur = conn.cursor()

    DUMMY_TIME_ID = 'not_applicable'

    # Identify columns that reference d_time.time_id
    time_fk_columns = []
    for line in dbml_text.splitlines():
        if line.startswith('Ref:') and 'd_time.time_id' in line:
            left, right = re.split(r'[>-]', line.replace('Ref:', '').strip(), maxsplit=1)
            if 'd_time.time_id' in right.strip():
                table, column = left.strip().split('.')
                time_fk_columns.append((table, column))

    # Replace NULLs with dummy value in tables that reference d_time.time_id
    for table, column in time_fk_columns:
        try:
            update_stmt = f"UPDATE {table} SET {column} = %s WHERE {column} = 'None';"
            log(f"Replacing NULLs in {table}.{column} → '{DUMMY_TIME_ID}'")
            cur.execute(update_stmt, (DUMMY_TIME_ID,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            log(f"ERROR while replacing NULLs in {table}.{column}: {e}")

    # Execute FK constraint statements
    for stmt in statements:
        try:
            log(f"Executing: {stmt}")
            cur.execute(stmt)
            conn.commit()
            log(f"Statement executed successfully: {stmt}")
        except Exception as e:
            conn.rollback()
            log(f"ERROR executing: {stmt}. Error: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
