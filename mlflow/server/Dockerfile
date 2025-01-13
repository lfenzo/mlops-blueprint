FROM ghcr.io/mlflow/mlflow

ADD requirements.txt /tmp/requirements.txt

RUN apt update -y && apt install git -y

RUN pip install -r /tmp/requirements.txt
