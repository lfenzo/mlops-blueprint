#!/usr/bin/bash

# Setting up some services requires them to be running
podman exec mlops-blueprint_mlflow-minio_1 bash init-minio.sh
podman exec mlops-blueprint_mlflow-nexus_1 bash init-nexus.sh
