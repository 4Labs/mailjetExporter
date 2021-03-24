FROM python:3.9-alpine

RUN pip install prometheus_client requests mailjet_rest get_docker_secret

ADD src /app
WORKDIR /app

CMD ["python", "mailjet_exporter.py"]
