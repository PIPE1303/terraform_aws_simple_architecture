import subprocess
import argparse
import os
import logging

# Configure general logging
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGS_DIR, 'pipeline.log'),
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    """Logs a message to both the console and the log file."""
    print(msg)
    logging.info(msg)


SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')

def run_script(script_name):
    """Runs a Python script and logs its execution."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    log(f"▶️ Running {script_name}...")
    result = subprocess.run(["python", script_path])
    if result.returncode != 0:
        log(f"Error running {script_name}")
        exit(result.returncode)
    log(f"{script_name} executed successfully\n")


def main():
    """Main function to parse arguments and run the pipeline scripts."""
    parser = argparse.ArgumentParser(description="Pipeline to create and populate the database.")
    parser.add_argument('--upload', action='store_true', help="Run upload_to_s3.py at the beginning")
    args = parser.parse_args()

    if args.upload:
        run_script('upload_to_s3.py')

    run_script('create_tables.py')
    run_script('load_data_bulk.py')
    run_script('create_constraints.py')

if __name__ == '__main__':
    main()
