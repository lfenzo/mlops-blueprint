from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="model-training",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    retrain_model = DockerOperator(
        task_id="retrain-model",
        image="model-retraining",
        command="--name modelo-novo-automatico",
        network_mode="mlops-blueprint_default",
    )

    retrain_model
