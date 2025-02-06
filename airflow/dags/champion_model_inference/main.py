import os
from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator


CHAMPION_MODEL_TAG = "champion"
DOCKER_IMAGE_OUTPUT_DIR = "/tmp/model"
DEFAULT_NETWORK_MODE = os.environ['PROJECT_NAME'] + "_default"
MODEL_URI_FILE = "/tmp/chammpion-model-uri.txt"
REGISTRY = "mlflow-nexus:8082"
IMAGE_NAME = "mlflow-best-model"
DATE_TAG = datetime.now().strftime("%Y-%m-%d")
INFERENCE_SERVER = "mlflow-inference-server"


mlflow_tracking_server_variables = {
    'AWS_ACCESS_KEY_ID': os.environ["AWS_ACCESS_KEY_ID"],
    'AWS_SECRET_ACCESS_KEY': os.environ["AWS_SECRET_ACCESS_KEY"],
    'MLFLOW_TRACKING_URI': os.environ["MLFLOW_TRACKING_URI"],
    'MLFLOW_S3_ENDPOINT_URL': os.environ["MLFLOW_S3_ENDPOINT_URL"],
}

docker_in_docker_kwargs = {
    "image": "docker:dind",
    "privileged": True,
    "auto_remove": "success",
    "api_version": "auto",
    "network_mode": DEFAULT_NETWORK_MODE,
    "environment": {
        "DOCKER_HOST": "unix:///var/run/docker.sock",
    },
}

with DAG(
    dag_id="champion-model-inference",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual trigger
    description="Genrate the inference with the best model from MLFlow",
    catchup=False,
) as dag:

    get_model_uri = DockerOperator(
        task_id="get-champion-model-uri",
        image="get-champion-model-uri",
        auto_remove="success",
        network_mode=DEFAULT_NETWORK_MODE,
        host_tmp_dir="/tmp",
        environment=mlflow_tracking_server_variables,
        mounts=[Mount(source="/tmp", target="/tmp", type="bind")],
        command=f"--tag {CHAMPION_MODEL_TAG} --output {MODEL_URI_FILE} --tracking-uri {os.environ['MLFLOW_TRACKING_URI']}",
    )

    generate_dockerfile = DockerOperator(
        task_id='generate-dockerfile',
        auto_remove="success",
        image='ghcr.io/mlflow/mlflow:v2.19.0',
        network_mode=DEFAULT_NETWORK_MODE,
        environment=mlflow_tracking_server_variables,
        host_tmp_dir="/tmp",
        mounts=[Mount(source="/tmp", target="/tmp", type="bind")],
        command=f"""
            sh -c '
            set -e;
            pip install boto3;
            mlflow models generate-dockerfile \
                --model-uri $(cat {MODEL_URI_FILE}) \
                --output-directory {DOCKER_IMAGE_OUTPUT_DIR} \
                --env-manager virtualenv
        '""",
    )

    build_image = DockerOperator(
        task_id="build-docker-image",
        **docker_in_docker_kwargs,
        command=f"""
            sh -c '
            set -e;
            dockerd --insecure-registry {REGISTRY} & sleep 10;
            docker build -t {IMAGE_NAME} {DOCKER_IMAGE_OUTPUT_DIR}
            docker tag {IMAGE_NAME} {REGISTRY}/{IMAGE_NAME}:latest;
            docker tag {IMAGE_NAME} {REGISTRY}/{IMAGE_NAME}:{DATE_TAG};
            docker images;
        '""",
        host_tmp_dir="/tmp",
        mounts=[
            Mount(source="/tmp", target="/tmp", type="bind"),
            Mount(source="dind-data", target="/var/lib/docker"),
        ],
    )

    push_image = DockerOperator(
        task_id="push-image-to-registry",
        **docker_in_docker_kwargs,
        command=f"""
            sh -c '
            set -e;
            dockerd --insecure-registry {REGISTRY} & sleep 10;
            docker images;
            docker login {REGISTRY} -u airflow -p airflow;
            docker push {REGISTRY}/{IMAGE_NAME}:latest;
            docker push {REGISTRY}/{IMAGE_NAME}:{DATE_TAG};
        '""",
        mounts=[
            Mount(source="dind-data", target="/var/lib/docker"),
        ],
    )

    launch_inference_server = BashOperator(
        task_id="launch-model-inference-server",
        bash_command=f"""
            sh -c "
            docker login localhost:8082 \
                -u {os.environ['NEXUS_REGISTRY_AIRFLOW_USER']} \
                -p {os.environ['NEXUS_REGISTRY_AIRFLOW_PASSWORD']};
            docker run -d \
                --network {DEFAULT_NETWORK_MODE} \
                --name {INFERENCE_SERVER} \
                localhost:8082/{IMAGE_NAME}:latest \
                sh -c 'mlflow models serve -m /opt/ml/model -p 8080 -h 0.0.0.0 & sleep 10;'
        "
        """,
    )

    run_model_inference = DockerOperator(
        task_id="run-model-inference",
        image="run-model-inference",
        network_mode=DEFAULT_NETWORK_MODE,
        auto_remove="success",
        command="--output /tmp/predictions.txt",
        host_tmp_dir="/tmp",
        environment=mlflow_tracking_server_variables,
        mounts=[
            Mount(source="/tmp", target="/tmp", type="bind"),
        ],
    )

    remove_inference_server = BashOperator(
        task_id="remove-inference-server",
        bash_command=f"""
            docker stop {INFERENCE_SERVER};
            docker rm --force {INFERENCE_SERVER};
        """,
    )

    upload_predictions = EmptyOperator(
        task_id="upload-predictions",
    )

    (
        get_model_uri
        >> generate_dockerfile
        >> build_image
        >> push_image
        >> launch_inference_server
        >> run_model_inference
        >> remove_inference_server.as_teardown(setups=launch_inference_server)
        >> upload_predictions
    )
