from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}


def log_start(**context):
    logger.info(f"Starting DAG: {context['dag'].dag_id}")
    logger.info(f"Execution date: {context['execution_date']}")


def log_end(**context):
    logger.info(f"Completed DAG: {context['dag'].dag_id}")
    logger.info(f"End time: {datetime.now()}")


def download_task():
    from dags.download.main import DownloadTask

    path = Path("/opt/airflow/data/archive.zip")
    task = DownloadTask(path)
    return task.execute()


def staging_task():
    from dags.load_staging.main import LoadDataTask

    pg_hook = PostgresHook(postgres_conn_id="postgres_default")
    conn = pg_hook.get_conn()
    try:
        path = Path("/opt/airflow/data/")
        task = LoadDataTask(path)
        return task.execute(conn)
    finally:
        conn.close()


def nds_task():
    from dags.load_nds.main import LoadNdsTask

    pg_hook = PostgresHook(postgres_conn_id="postgres_default")
    conn = pg_hook.get_conn()
    try:
        task = LoadNdsTask()
        return task.execute(conn)
    finally:
        conn.close()


def dds_task():
    from dags.load_dds.main import LoadDdsTask

    pg_hook = PostgresHook(postgres_conn_id="postgres_default")
    conn = pg_hook.get_conn()
    try:
        task = LoadDdsTask()
        return task.execute(conn)
    finally:
        conn.close()


with DAG(
    "full_etl_dag",
    default_args=default_args,
    description="Full ETL process with TaskGroups",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    start_log = PythonOperator(
        task_id="start_log",
        python_callable=log_start,
        provide_context=True,
    )

    with TaskGroup("download_group") as download_group:
        download = PythonOperator(
            task_id="download_data",
            python_callable=download_task,
        )

    with TaskGroup("staging_group") as staging_group:
        load_staging = PythonOperator(
            task_id="load_staging",
            python_callable=staging_task,
        )

    with TaskGroup("nds_group") as nds_group:
        load_nds = PythonOperator(
            task_id="load_nds",
            python_callable=nds_task,
        )

    with TaskGroup("dds_group") as dds_group:
        load_dds = PythonOperator(
            task_id="load_dds",
            python_callable=dds_task,
        )

    end_log = PythonOperator(
        task_id="end_log",
        python_callable=log_end,
        provide_context=True,
    )

    start_log >> download_group >> staging_group >> nds_group >> dds_group >> end_log
