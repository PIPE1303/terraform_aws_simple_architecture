import os
import psycopg2
import logging
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Absolute path to the 'logs' folder from the script in 'scripts/'
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

log_file_path = os.path.join(LOGS_DIR, 'load_data.log')

# Configure logging to write to file and print to stdout
logging.basicConfig(
    filename=log_file_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    """Logs a message to both console and file."""
    print(msg)
    logging.info(msg)

# Environment variables
DATA_DIR = 'sample_data'
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

# Dummy values for null timestamp fields
DUMMY_TIME_ID = "not_applicable"
DUMMY_TIMESTAMP = "9999-01-01 00:00:00"
DUMMY_WEEK_ID = "-1"
DUMMY_MONTH_ID = "-1"
DUMMY_YEAR_ID = "-1"
DUMMY_WEEKDAY_ID = "-1"

def get_table_columns(cursor, table_name):
    """
    Retrieves the column names of a given table from PostgreSQL,
    ordered by their ordinal position.
    """
    cursor.execute(
        f"SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position",
        (table_name,)
    )
    return [row[0] for row in cursor.fetchall()]

def insert_dummy_if_needed(cursor):
    """
    Inserts a dummy row into dimension tables (d_time, d_week, d_month, d_weekday, d_year)
    if not already present. This is used to handle null timestamp dimensions.
    """
    # Check if dummy value already exists in d_time
    cursor.execute(f"SELECT 1 FROM d_time WHERE time_id = %s", (DUMMY_TIME_ID,))
    if cursor.fetchone() is None:
        # Insert dummy value into d_time if not present
        log(f"Inserting dummy row into d_time")
        cursor.execute(f"""
            INSERT INTO d_time (time_id, action_timestamp, week_id, month_id, year_id, weekday_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (DUMMY_TIME_ID, DUMMY_TIMESTAMP, DUMMY_WEEK_ID, DUMMY_MONTH_ID, DUMMY_YEAR_ID, DUMMY_WEEKDAY_ID))
        log(f"DUMMY_TIME_ID inserted into d_time")

        log(f"Inserting dummy row into d_week")
        cursor.execute(f"""
            INSERT INTO d_week (week_id, action_week)
            VALUES (%s, %s)
        """, (DUMMY_WEEK_ID, DUMMY_WEEK_ID))
        log(f"DUMMY_WEEK_ID inserted into d_week")

        log(f"Inserting dummy row into d_month")
        cursor.execute(f"""
            INSERT INTO d_month (month_id, action_month)
            VALUES (%s, %s)
        """, (DUMMY_MONTH_ID, DUMMY_MONTH_ID))
        log(f"DUMMY_MONTH_ID inserted into d_month")

        log(f"Inserting dummy row into d_weekday")
        cursor.execute(f"""
            INSERT INTO d_weekday (weekday_id, action_weekday)
            VALUES (%s, %s)
        """, (DUMMY_WEEKDAY_ID, DUMMY_WEEKDAY_ID))
        log(f"DUMMY_WEEKDAY_ID inserted into d_weekday")

        log(f"Inserting dummy row into d_year")
        cursor.execute(f"""
            INSERT INTO d_year (year_id, action_year)
            VALUES (%s, %s)
        """, (DUMMY_YEAR_ID, DUMMY_YEAR_ID))
        log(f"DUMMY_YEAR_ID inserted into d_year")

def load_csv_with_copy(cursor, table_name, csv_path, real_columns):
    """
    Loads a CSV file into a PostgreSQL table using COPY, aligning CSV columns with
    actual table columns and rewriting the file temporarily if needed.
    """
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ordered_fieldnames = [col for col in real_columns if col in reader.fieldnames]

        # Rewrite the CSV with reordered columns
        with open('temp_ordered.csv', 'w', newline='', encoding='utf-8') as temp_csv:
            writer = csv.DictWriter(temp_csv, fieldnames=ordered_fieldnames)
            writer.writeheader()
            for row in reader:
                writer.writerow({k: row[k] for k in ordered_fieldnames})

        # Use COPY to insert the reordered data
        with open('temp_ordered.csv', 'r', encoding='utf-8') as temp_csv:
            cursor.copy_expert(
                f"COPY {table_name} ({', '.join(ordered_fieldnames)}) FROM STDIN WITH CSV HEADER",
                temp_csv
            )

        os.remove('temp_ordered.csv')

def main():
    """
    Main function to load all CSV files from subfolders of the data directory
    into their respective PostgreSQL tables, ensuring dummy dimension values exist.
    """
    conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    cur = conn.cursor()

    # Insert dummy row in d_time if not already present
    insert_dummy_if_needed(cur)

    for root, dirs, files in os.walk(DATA_DIR):
        for dir_name in dirs:
            table_path = os.path.join(root, dir_name)
            for file_name in os.listdir(table_path):
                if not file_name.endswith('.csv'):
                    continue
                csv_path = os.path.join(table_path, file_name)
                try:
                    log(f"Loading file {csv_path} into table {dir_name}")
                    real_columns = get_table_columns(cur, dir_name)
                    load_csv_with_copy(cur, dir_name, csv_path, real_columns)
                    conn.commit()
                    log(f"Load completed for {csv_path}")
                except Exception as e:
                    conn.rollback()
                    log(f"ERROR while loading {csv_path}: {e}")

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
