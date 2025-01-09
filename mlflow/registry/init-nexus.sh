#!/usr/bin/bash

NEXUS_PORT=8081
NEXUS_HOST="nexus"

ADMIN_PASSWORD=$(cat /nexus-data/admin.password)
NEW_PASSWORD="condamargens"
echo "Changing default admin password"
curl -v -u admin:$ADMIN_PASSWORD -X PUT -v \
  -H "Content-Type: text/plain" \
  -d "$NEW_PASSWORD" \
  http://$NEXUS_HOST:$NEXUS_PORT/service/rest/v1/security/users/admin/change-password

echo "Creating Blob store for container image registry"
curl -u admin:$NEW_PASSWORD -X POST -v \
  -H "Content-Type: application/json" \
  -d '{
        "name": "docker-image-registry",
        "path": "/nexus-data/blobs/docker-image-registry"
      }' \
  http://$NEXUS_HOST:$NEXUS_PORT/service/rest/v1/blobstores/file

echo "Creating Docker image registry"
curl -u admin:$NEW_PASSWORD -X POST -v \
  -H "Content-Type: application/json" \
  -d '{
        "name": "mlflow-model-image-registry",
        "online": true,
        "storage": {
          "blobStoreName": "docker-image-registry",
          "strictContentTypeValidation": true,
          "writePolicy": "ALLOW_ONCE"
        },
        "docker": {
          "v1Enabled": false,
          "forceBasicAuth": true,
          "httpPort": 8082
        }
      }' \
  http://$NEXUS_HOST:$NEXUS_PORT/service/rest/v1/repositories/docker/hosted

echo "Nexus initialization completed."
