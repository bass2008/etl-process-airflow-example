from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dags.download.main import DownloadTask
from pathlib import Path

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}


def run_task():

    path = Path("/opt/airflow/data/archive.zip")
    task = DownloadTask(path)
    return task.execute()


with DAG(
    "download_dag",
    default_args=default_args,
    description="A simple DAG to download data",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    insert_task = PythonOperator(
        task_id="download_data",
        python_callable=run_task,
    )
