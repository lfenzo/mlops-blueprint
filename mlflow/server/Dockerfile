FROM ghcr.io/mlflow/mlflow

ADD requiremsnts.txt /tmp/requiremsnts.txt

RUN apt update -y && apt install git -y

RUN pip install -r /tmp/requiremsnts.txt
