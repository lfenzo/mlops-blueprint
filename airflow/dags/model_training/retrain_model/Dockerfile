FROM python:3.12

WORKDIR /project

COPY requirements.txt /tmp/requirements.txt
COPY main.py main.py

RUN pip install -r /tmp/requirements.txt

ENTRYPOINT ["python", "main.py"]
