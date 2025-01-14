#!/usr/bin/bash

set -e

# Download the current docker-compose file
AIRFLOW_VERSION="2.10.4"
AIRFLOW_COMPOSE_FILE="docker-compose.airflow.yaml"

curl -Lf -o $AIRFLOW_COMPOSE_FILE "https://airflow.apache.org/docs/apache-airflow/$AIRFLOW_VERSION/docker-compose.yaml"

# Add the ':z' to prevent problems with SELinux mapped volumes
sed -i '/- \${AIRFLOW_PROJ_DIR:-.}:/s|$|:z|' $AIRFLOW_COMPOSE_FILE

# Remove default airflow examples 
sed -i "/AIRFLOW__CORE__LOAD_EXAMPLES:/s/'true'/'false'/" $AIRFLOW_COMPOSE_FILE

# creating the necessary directories for airflow
mkdir -p ./airflow/{logs,plugins,config}
chmod -R 777 ./airflow/dags  # we expect a pre-existing airflow/dags dir

export AIRFLOW_UID=$(id -u)
export AIRFLOW_PROJ_DIR=$(pwd)/airflow

podman compose -f $AIRFLOW_COMPOSE_FILE up airflow-init -d
