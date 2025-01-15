#!/usr/bin/bash

# Setting up some services requires them to be running
docker exec mlops-blueprint-mlflow-minio-1 bash init-minio.sh
docker exec mlops-blueprint-mlflow-nexus-1 bash init-nexus.sh
