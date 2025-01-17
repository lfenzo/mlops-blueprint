from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator

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
    dag_id="generate-best-model-inference",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual trigger
    catchup=False,
) as dag:

    REGISTRY = "mlflow-nexus:8082"
    IMAGE_NAME = "mlflow-best-model";
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

    generate_dockerfile >> build_image >> push_image
