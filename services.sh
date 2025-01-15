#!/usr/bin/bash

export AIRFLOW_UID=$(id -u)
export AIRFLOW_PROJ_DIR=$(pwd)/airflow

docker compose \
    -f docker-compose.feast.yaml \
    -f docker-compose.mlflow.yaml \
    -f docker-compose.airflow.yaml \
    -f docker-compose.jupyter.yaml \
    "$@"
