FROM python:3.12

ENV MLFLOW_TRACKING_URI="http://mlflow:5000"
ENV MLFLOW_S3_ENDPOINT_URL="http://mlflow-minio:9000"
ENV AWS_ACCESS_KEY_ID="N7Fi8wZ5JPo4RLc4WC0d"
ENV AWS_SECRET_ACCESS_KEY="VyrzX9QHcPywmGLusJSq7eJQAI07fV2x6OUVbieE"

WORKDIR /project

COPY requirements.txt /tmp/requirements.txt
COPY main.py main.py

RUN pip install -r /tmp/requirements.txt

ENTRYPOINT ["python", "main.py"]
