from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
from dags.load_dds.main import LoadDdsTask

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}


def run_task():
    pg_hook = PostgresHook(postgres_conn_id="postgres_default")
    conn = pg_hook.get_conn()

    try:
        task = LoadDdsTask()
        return task.execute(conn)
    finally:
        conn.close()


with DAG(
        "load_dds_dag",
        default_args=default_args,
        description="A simple DAG to load dds",
        schedule_interval=timedelta(days=1),
        start_date=datetime(2024, 1, 1),
        catchup=False,
) as dag:
    insert_task = PythonOperator(
        task_id="load_dds",
        python_callable=run_task,
    )