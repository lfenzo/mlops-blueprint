import airflow

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='system_autoclean',
    schedule_interval='@weekly',
    catchup=False,
    default_args=default_args,
) as dag:

    clear_temp_files = BashOperator(
        task_id='clear_temp_files',
        bash_command='rm -rf /tmp/* /var/tmp/*',
    )

    clear_docker = BashOperator(
        task_id='clear_docker',
        bash_command='docker system prune -f',
    )

    (
        EmptyOperator(task_id="autoclean-start")
        >> [clear_temp_files, clear_docker]
        >> EmptyOperator(task_id="autoclean-done")
    )
