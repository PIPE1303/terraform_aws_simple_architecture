import os
import boto3
import psycopg2
import csv
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

bucket_name = os.getenv("BUCKET_NAME")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")
delete_after_load = os.environ.get('DELETE_AFTER_LOAD', 'false').lower() == 'true'

import os
import boto3
import psycopg2
import csv
from io import StringIO
import logging

# Configurar logging
logging.basicConfig(
    filename='load_data.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    print(msg)
    logging.info(msg)

def load_data_to_db():
    # Conexión a S3
    s3_client = boto3.client('s3')
    
    # Listar todas las carpetas (prefijos) en el bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name, Delimiter='/')

    if 'CommonPrefixes' not in response:
        log("No se encontraron carpetas en el bucket.")
        return
    
    for prefix in response['CommonPrefixes']:
        table_name = prefix['Prefix'].strip('/')

        file_list = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix['Prefix'])

        if 'Contents' not in file_list:
            log(f"No se encontraron archivos en la carpeta {table_name}")
            continue

        for obj in file_list['Contents']:
            key = obj['Key']

            if key.endswith('/') or not key.endswith('.csv'):
                continue

            log(f"Procesando archivo {key} para tabla {table_name}")

            # Descargar CSV
            csv_obj = s3_client.get_object(Bucket=bucket_name, Key=key)
            csv_data = csv_obj['Body'].read().decode('utf-8')
            csv_file = StringIO(csv_data)
            csv_reader = csv.reader(csv_file)

            columns = next(csv_reader)
            columns_str = ', '.join(columns)

            # Conexión a la base de datos
            conn = psycopg2.connect(
                host=db_host,
                dbname=db_name,
                user=db_user,
                password=db_password,
                port=db_port
            )
            cur = conn.cursor()

            try:
                for row in csv_reader:
                    values_str = ', '.join([f"'{value.replace("'", "''")}'" for value in row])
                    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
                    cur.execute(query)

                conn.commit()
                log(f"Archivo {key} cargado exitosamente en tabla {table_name}")

                if delete_after_load:
                    s3_client.delete_object(Bucket=bucket_name, Key=key)
                    log(f"Archivo {key} eliminado de S3 tras carga")

            except Exception as e:
                conn.rollback()
                log(f"ERROR al cargar {key}: {e}")
            finally:
                cur.close()
                conn.close()

if __name__ == "__main__":
    load_data_to_db()
