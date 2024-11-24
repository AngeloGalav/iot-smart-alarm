FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install paho-mqtt requests

CMD ["python", "server.py"]