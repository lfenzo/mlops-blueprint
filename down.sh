podman compose \
    -f docker-compose.feast.yaml \
    -f docker-compose.jupyter.yaml \
    -f docker-compose.mlflow.yaml \
    down "$@"

# deleting podman named volumes
podman compose \
    -f docker-compose.feast.yaml \
    -f docker-compose.jupyter.yaml \
    -f docker-compose.mlflow.yaml \
    down -v "$@"
