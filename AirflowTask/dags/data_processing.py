import os
import pandas as pd
import re
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.task_group import TaskGroup
from airflow.datasets import Dataset
from airflow.utils.dates import days_ago

DATA_FOLDER = os.getenv("DATA_FOLDER")
INPUT_FILE = os.getenv("INPUT_FILENAME")
OUTPUT_FILE = os.getenv("OUTPUT_FILENAME")
FULL_INPUT_PATH = f"{DATA_FOLDER}/{INPUT_FILE}"
FULL_OUTPUT_PATH = f"{DATA_FOLDER}/{OUTPUT_FILE}"

processed_dataset = Dataset(f"file://{FULL_OUTPUT_PATH}")

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}


def check_file_empty(**kwargs):
    if os.path.getsize(FULL_INPUT_PATH) == 0:
        return 'file_empty_log'
    
    df = pd.read_csv(FULL_INPUT_PATH)
    if df.empty:
        return 'file_empty_log'
        
    return 'processing_group.replace_nulls'

def clean_content_text(text):
    text = str(text)
    cleaned = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)
    cleaned = cleaned.strip()
    if not cleaned or str(text) in ['NA', 'NaN']:
        return "-"
    return cleaned

def task_replace_nulls():
    df = pd.read_csv(FULL_INPUT_PATH)
    df.fillna("-", inplace=True)
    df.to_csv(FULL_OUTPUT_PATH, index=False)

def task_sort_data():
    df = pd.read_csv(FULL_OUTPUT_PATH)
    if 'at' in df.columns:
        df['at'] = pd.to_datetime(df['at'])
        df.sort_values(by='at', inplace=True)
    df.to_csv(FULL_OUTPUT_PATH, index=False)

def task_clean_content():
    df = pd.read_csv(FULL_OUTPUT_PATH)
    if 'content' in df.columns:
        df['content'] = df['content'].apply(clean_content_text)
    df.to_csv(FULL_OUTPUT_PATH, index=False)


with DAG(
    dag_id='1_data_processing_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    wait_for_file = FileSensor(
        task_id='wait_for_file',
        filepath=FULL_INPUT_PATH,
        poke_interval=10,
        timeout=600,
        mode='poke'
    )

    branch_task = BranchPythonOperator(
        task_id='check_if_empty',
        python_callable=check_file_empty
    )

    empty_log = BashOperator(
        task_id='file_empty_log',
        bash_command='echo "File is empty at $(date)" >> /opt/airflow/logs/empty_file.log'
    )

    with TaskGroup("processing_group") as processing_group:
        
        t1 = PythonOperator(
            task_id='replace_nulls',
            python_callable=task_replace_nulls
        )

        t2 = PythonOperator(
            task_id='sort_by_date',
            python_callable=task_sort_data
        )

        t3 = PythonOperator(
            task_id='clean_content',
            python_callable=task_clean_content,
            outlets=[processed_dataset] 
        )

        t1 >> t2 >> t3

    wait_for_file >> branch_task
    branch_task >> empty_log
    branch_task >> processing_group