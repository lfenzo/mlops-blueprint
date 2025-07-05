# MLOps Project Blueprint

This repository contains the necessary infrastructure to setup a basic MLFlow/Airflow setup
for Machine Learning projects. 

For more details on the architecture and components, checkout [this issue](https://gitlab.com/Robbyson/Robbyson/-/issues/33756).


## Setup

Install the base host dependencies (Docker, Git, etc):

```bash
bash install.sh
```

Fetch the current Airflow docker-compose file from the Apache Airflow resources. This step is performed
dynamically because we are using a third-party compose file (with some minor changes). Running this
step will also spawn and rum the data-related Airflow containers, you can keep them running and
move on to the next step.

```bash
bash setup-airflow.sh
```

Next, launch the containers with the `start.sh` script. Some services may take longer to start than
others, a delay of about 3 minutes is expected in this step.

```bash
bash start.sh
```

After running the first initialization, some services (e.g. Nexus and Minio) need some basic
configuration, like creating users, setting up resources, etc. Some of these operations steps have
been automated and can be run with the following:

```bash
bash setup-services.sh
```
