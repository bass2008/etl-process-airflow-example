from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
from dags.load_staging.main import LoadDataTask

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}


def run_task():
    """
    Run the task in Airflow using PostgresHook
    """
    pg_hook = PostgresHook(postgres_conn_id="postgres_default")
    conn = pg_hook.get_conn()

    try:
        path = Path("/opt/airflow/data/")
        task = LoadDataTask(path)
        return task.execute(conn)
    finally:
        conn.close()


with DAG(
    "load_data_dag",
    default_args=default_args,
    description="A simple DAG to load data",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    insert_task = PythonOperator(
        task_id="load_staging",
        python_callable=run_task,
    )