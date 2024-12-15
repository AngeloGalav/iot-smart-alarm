FROM python:3.10-slim

WORKDIR /app

# COPY . /app

RUN pip install paho-mqtt numpy pandas requests influxdb-client flask Flask-MQTT flask-cors prophet

CMD ["python", "server.py"]