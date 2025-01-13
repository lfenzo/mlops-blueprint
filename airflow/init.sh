#!/usr/bin/bash

# Download the current docker-compose file
AIRFLOW_VERSION="2.10.4"
curl -LfO "https://airflow.apache.org/docs/apache-airflow/$AIRFLOW_VERSION/docker-compose.yaml"

# Add the ':z' to prevent problems with SELinux mapped volumes
sed -i '/- \${AIRFLOW_PROJ_DIR:-.}:/s|$|:z|' docker-compose.yaml

# Remove default airflow examples 
sed -i "/AIRFLOW__CORE__LOAD_EXAMPLES:/s/'true'/'false'/" docker-compose.yaml

# creating the necessary directories for airflow
mkdir -p ./{dags,logs,plugins,config}
chmod -R 777 ./dags

export AIRFLOW_UID=$(id -u)

podman compose up airflow-init
