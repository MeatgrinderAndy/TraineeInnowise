import os
import logging
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.datasets import Dataset
from airflow.utils.dates import days_ago

logger = logging.getLogger(__name__)

DATA_FOLDER = os.getenv("DATA_FOLDER")
OUTPUT_FILE = os.getenv("OUTPUT_FILENAME")
FULL_PATH = f"{DATA_FOLDER}/{OUTPUT_FILE}"
processed_dataset = Dataset(f"file://{FULL_PATH}")

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

def upload_to_mongo():
    logger.info(f"Uploading to MongoDB. Reading file: {FULL_PATH}")
    
    try:
        df = pd.read_csv(FULL_PATH, keep_default_na=False, na_values=[])
    except FileNotFoundError:
        logger.error(f"File not found at path: {FULL_PATH}. Stopping task.")
        raise
    
    records = df.to_dict(orient='records')

    try:
        hook = MongoHook(conn_id='mongo_default')
        
        try:
            hook.delete_many(mongo_collection='comments', filter_doc={}, mongo_db='airflow_db')
            logger.info("Old data cleared successfully.")
        except Exception as e:
            logger.warning(f"Could not clear collection. Еmpty or first run: {e}")
        
        hook.insert_many(mongo_collection='comments', docs=records, mongo_db='airflow_db')
        logger.info(f"Success. Inserted {len(records)} records into MongoDB.")
        
    except Exception as e:
        logger.error(f"Failed to connect or insert into MongoDB: {e}")
        raise e 
with DAG(
    dag_id='2_mongo_loader_dag',
    default_args=default_args,
    schedule=[processed_dataset], 
    catchup=False
) as dag:

    load_task = PythonOperator(
        task_id='upload_to_mongo',
        python_callable=upload_to_mongo
    )