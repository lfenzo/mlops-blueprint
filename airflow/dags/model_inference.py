from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator


with DAG(
    dag_id="generate-best-model-inference",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual trigger
    catchup=False,
) as dag:

    generate_dockerfile = DockerOperator(
        task_id='generate-dockerfile',
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

    build_docker_image = DockerOperator(
        task_id='build-docker-image',
        image='docker:latest',
        command="sh -c 'docker build -t mlflow-best-model /tmp/model'",
        host_tmp_dir="/tmp",
        mounts=[
            Mount(source="/var/run/docker.sock", target="/var/run/docker.sock", type="bind"),
            Mount(source="/tmp", target="/tmp", type="bind")
        ]
    )

    # this needs to be address with docker in docker
    # currently the spawed container is not able to resolve 'mlflow-nexus:8082'
    # even though thery are int he same network
    push_image_to_registry = DockerOperator(
        task_id="push-docker-image-to-registry",
        image="docker:latest",
        command="""
            sh -c '
            DATE_TAG=$(date +%Y-%m-%d);
            IMAGE_NAME="mlflow-best-model";
            REGISTRY="localhost:8082";  # must be changed to "mlflow-nexus" in the future

            docker tag $REGISTRY/$IMAGE_NAME:latest $REGISTRY/$IMAGE_NAME:$DATE_TAG;

            docker login http://localhost:8082 -u airflow -p airflow;

            docker push $REGISTRY/$IMAGE_NAME:latest;
            docker push $REGISTRY/$IMAGE_NAME:$DATE_TAG;
        '""",
        network_mode="mlops-blueprint_default",
        mounts=[
            Mount(source="/var/run/docker.sock", target="/var/run/docker.sock", type="bind"),
            Mount(source="/tmp", target="/tmp", type="bind")
        ]
    )

    generate_dockerfile >> build_docker_image >> push_image_to_registry
