#!/usr/bin/bash

set -e

mkdir -p ./airflow/{logs,plugins,config}
chmod -R 777 ./airflow/dags  # we expect a pre-existing airflow/dags dir

docker compose -f $AIRFLOW_COMPOSE_FILE up airflow-init -d
