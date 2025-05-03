import boto3
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
log_file_path = os.path.join(LOGS_DIR, 'upload_to_s3.log')

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

log(f"Conectando a: host={db_host} db={db_name}")

DATA_FOLDER = './sample_data'
s3 = boto3.client('s3')

for foldername in os.listdir(DATA_FOLDER):
    folder_path = os.path.join(DATA_FOLDER, foldername)

    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            s3_key = f"{foldername}/{filename}"  # Subirlo con prefijo de carpeta

            if os.path.isfile(file_path):
                try:
                    s3.upload_file(file_path, bucket_name, s3_key)
                    log(f"✔️ Subido: {s3_key}")
                except Exception as e:
                    log(f"❌ Error al subir {s3_key}: {e}")
