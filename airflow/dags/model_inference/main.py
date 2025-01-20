from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.empty import EmptyOperator


docker_in_docker_kwargs = {
    "image": "docker:dind",
    "privileged": True,
    "auto_remove": "success",
    "api_version": "auto",
    "network_mode": "mlops-blueprint_default",
    "environment": {
        "DOCKER_HOST": "unix:///var/run/docker.sock",
    },
}

with DAG(
    dag_id="model-inference",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual trigger
    description="Genrate the inference with the best model from MLFlow",
    catchup=False,
) as dag:

    REGISTRY = "mlflow-nexus:8082"
    IMAGE_NAME = "mlflow-best-model"
    DATE_TAG = datetime.now().strftime("%Y-%m-%d")

    generate_dockerfile = DockerOperator(
        task_id='generate-dockerfile',
        auto_remove="success",
        image='ghcr.io/mlflow/mlflow',
        command="""
            sh -c '
            pip install boto3;
            mlflow models generate-dockerfile --model-uri models:/test-model/1 -d /tmp/model;
        '""",
        network_mode="mlops-blueprint_default",
        environment={
            'AWS_ACCESS_KEY_ID': 'N7Fi8wZ5JPo4RLc4WC0d',
            'AWS_SECRET_ACCESS_KEY': 'VyrzX9QHcPywmGLusJSq7eJQAI07fV2x6OUVbieE',
            'MLFLOW_TRACKING_URI': 'http://mlflow:5000',
            'MLFLOW_S3_ENDPOINT_URL': 'http://mlflow-minio:9000',
        },
        host_tmp_dir="/tmp",
        mounts=[Mount(source="/tmp", target="/tmp", type="bind")]
    )

    build_image = DockerOperator(
        task_id="build-docker-image",
        **docker_in_docker_kwargs,
        command=f"""
            sh -c '
            dockerd --insecure-registry {REGISTRY} & sleep 10;
            docker build -t {IMAGE_NAME} /tmp/model;
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

    # TODO: 'mlflow-nexus' is not resolved in the webserver/worker because we are using
    # the host mount of the docker socket. We will need Docker-In-Docker for that here
    # After that, the Admin > Connections must be set property
    launch_inference_server = DockerOperator(
        task_id="launch-model-inference-server",
        image="localhost:8082/mlflow-best-model:latest",
        container_name="mlflow-inference-server",
        docker_conn_id="mlflow-model-registry",
        network_mode="mlops-blueprint_default",
    )

    run_model_inference = DockerOperator(
        task_id="run-model-inference",
        image="model-inference-client:latest",
    )

    remove_inference_server = EmptyOperator(task_id="remove-model-inference-server")

    generate_dockerfile >> build_image >> push_image >> launch_inference_server >> run_model_inference >> remove_inference_server.as_teardown(setups=launch_inference_server)
