FROM apache/airflow:3.1.6
USER root
RUN apt-get update && apt-get install -y gcc python3-dev
USER airflow
RUN pip install apache-airflow-providers-snowflake