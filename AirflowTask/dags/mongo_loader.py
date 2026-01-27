import os
import json
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.datasets import Dataset
from airflow.utils.dates import days_ago

DATA_FOLDER = os.getenv("DATA_FOLDER")
OUTPUT_FILE = os.getenv("OUTPUT_FILENAME")
FULL_PATH = f"{DATA_FOLDER}/{OUTPUT_FILE}"
processed_dataset = Dataset(f"file://{FULL_PATH}")

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

def upload_to_mongo():
    try:
        df = pd.read_csv(FULL_PATH)
    except FileNotFoundError:
        print("File not found.")
        return

    records = df.to_dict(orient='records')

    hook = MongoHook(conn_id='mongo_default')
    
    try:
        hook.delete_many(mongo_collection='comments', filter_doc={}, mongo_db='airflow_db')
        print("Old data cleared.")
    except Exception as e:
        print(f"Collection might be empty or not exists: {e}")
    
    hook.insert_many(mongo_collection='comments', docs=records, mongo_db='airflow_db')
    print(f"Inserted {len(records)} records into MongoDB.")

with DAG(
    dag_id='2_mongo_loader_dag',
    default_args=default_args,
    schedule=[processed_dataset], 
    catchup=False
) as dag:

    load_task = PythonOperator(
        task_id='load_to_mongodb',
        python_callable=upload_to_mongo
    )