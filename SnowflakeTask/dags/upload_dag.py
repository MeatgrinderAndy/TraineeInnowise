from airflow.decorators import dag, task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime
import os
import logging

logger = logging.getLogger("airflow.task")

CSV_FILENAME = os.getenv('AIRLINE_CSV_FILENAME')

CSV_FILE_PATH = f'/opt/airflow/dags/data/{CSV_FILENAME}'
SQL_DIR = '/opt/airflow/dags/queries'

@dag(
    dag_id='snowflake_dwh_pipeline',
    schedule='@daily',
    start_date=datetime(2026, 2, 1),
    catchup=False,
    tags=['snowflake', 'etl', 'taskflow']
)
def snowflake_pipeline():

    @task
    def execute_sql_file(filename: str):
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        file_path = os.path.join(SQL_DIR, filename)
        
        if not os.path.exists(file_path):
            file_path = filename 
            
        with open(file_path, 'r') as f:
            query = f.read()
            hook.run(query)
            logger.info(f"Executed SQL from {filename}")

    @task(task_id='upload_csv_to_stage')
    def upload_csv_to_stage():
        if not os.path.exists(CSV_FILE_PATH):
            logger.error(f"File search failed at: {CSV_FILE_PATH}")
            raise FileNotFoundError(f"CRITICAL ERROR: File not found at {CSV_FILE_PATH}")
        
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        
        stage_path = "@SNOWFLAKE_LEARNING_DB.STAGE1.csv_stage"
        
        sql_command = f"PUT 'file://{CSV_FILE_PATH}' {stage_path} AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        logger.info(f"Executing: {sql_command}")
        hook.run(sql_command)

    @task
    def call_procedure(sql_query: str):
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        hook.run(sql_query)
        logger.info(f"Executed procedure: {sql_query}")

    setup = execute_sql_file.override(task_id='setup_infrastructure')(filename='setup.sql')
    
    procs = execute_sql_file.override(task_id='create_procedures')(filename='procedures.sql')

    upload = upload_csv_to_stage()

    stage1 = call_procedure.override(task_id='run_stage1_load')(sql_query="CALL STAGE1.load_raw_data();")
    stage2 = call_procedure.override(task_id='run_stage2_transform')(sql_query="CALL STAGE2.process_clean_data();")
    stage3 = call_procedure.override(task_id='run_stage3_aggregate')(sql_query="CALL STAGE3.aggregate_data();")

    setup >> procs >> upload >> stage1 >> stage2 >> stage3

pipeline = snowflake_pipeline()