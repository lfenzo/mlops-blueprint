FROM python:3.12

WORKDIR /project

COPY requirements.txt requirements.txt
COPY main.py main.py

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
