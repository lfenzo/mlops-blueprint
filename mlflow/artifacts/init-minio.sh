#!/usr/bin/bash

ALIAS="local"
MLFLOW_ARTIFACT_BUCKET="mlflow-artifacts"

# Set the alias for the current server (necessary to recognize to use the alias 'local'
# referencing the current server)
mc alias set $ALIAS http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD

# Create the Mlflow artifact bucket (mb == make bucket)
mc mb $ALIAS/$MLFLOW_ARTIFACT_BUCKET

# Create the users with the necessary permissions
mc admin user add $ALIAS Enzo condamargens
mc admin policy attach $ALIAS readwrite --user Enzo

mc admin user add $ALIAS mlflow condamargens
mc admin policy create $ALIAS listbuckets policy-list-buckets.json
mc admin policy attach $ALIAS listbuckets --user mlflow
mc admin policy attach $ALIAS readonly --user mlflow
