from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


def print_hello():
    print("Hello Airflow!")


with DAG(
    dag_id="test_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,  # Manual trigger
    catchup=False,
) as dag:

    hello_task = PythonOperator(task_id="hello_world", python_callable=print_hello)
