podman compose \
    -f docker-compose.feast.yaml \
    -f docker-compose.jupyter.yaml \
    -f docker-compose.mlflow.yaml \
    up "$@"
