#!/usr/bin/bash

PROJECT_NAME="mlops-blueprint"

docker compose \
    -p $PROJECT_NAME \
    -f docker-compose.feast.yaml \
    -f docker-compose.mlflow.yaml \
    -f docker-compose.airflow.yaml \
    "$@"
