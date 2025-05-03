import subprocess
import argparse
import os
import logging

# Configurar logging general
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGS_DIR, 'pipeline.log'),
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    print(msg)
    logging.info(msg)


SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')

def run_script(script_name):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    log(f"▶️ Ejecutando {script_name}...")
    result = subprocess.run(["python", script_path])
    if result.returncode != 0:
        log(f"❌ Error al ejecutar {script_name}")
        exit(result.returncode)
    log(f"✔️ {script_name} ejecutado con éxito\n")


def main():
    parser = argparse.ArgumentParser(description="Pipeline para crear y poblar la base de datos.")
    parser.add_argument('--upload', action='store_true', help="Ejecutar upload_to_s3.py al inicio")
    args = parser.parse_args()

    if args.upload:
        run_script('upload_to_s3.py')

    run_script('create_tables.py')
    run_script('load_data_bulk.py')
    run_script('create_constraints.py')

if __name__ == '__main__':
    main()
