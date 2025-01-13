#!/usr/bin/env bash

set -e

ROOT_DIR=$(pwd)
COMPOSE_FILES=$(find "$ROOT_DIR" -name "docker-compose.yaml")
 
# Loop through each Compose file and run the `podman-compose` commands
for COMPOSE_FILE in $COMPOSE_FILES; do
    COMPOSE_DIR=$(dirname "$COMPOSE_FILE")
    echo "Running podman-compose in $COMPOSE_DIR"
    
    cd "$COMPOSE_DIR"
    podman compose "$@"
    cd "$ROOT_DIR"
done

echo "All services have been started successfully!"
