from flask import Flask
import json
import os
import logging
from influxdb_client import InfluxDBClient, Point, WriteOptions
from flask_mqtt import Mqtt
from backend_secrets import influxdb_api_token
from weather_utils import get_weather_data
from mqtt_utils import send_broker_ip

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# MQTT configuration
app.config['MQTT_BROKER_URL'] = os.getenv('MQTT_BROKER_HOST', 'localhost')
app.config['MQTT_BROKER_PORT'] = int(os.getenv('MQTT_BROKER_PORT', 1883))

mqtt = Mqtt(app)

# ESP32 network info
ESP32_IP = "192.168.254.56"
ESP32_PORT = 8080

# InfluxDB configuration
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUXDB_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
INFLUXDB_BUCKET = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET", "iot-bucket")
INFLUXDB_TOKEN = influxdb_api_token
INFLUXDB_ORG = os.getenv("DOCKER_INFLUXDB_INIT_ORG", "iot-org")

# MQTT topics
MQTT_TOPIC_COMMAND = "iot_alarm/command"
MQTT_TOPIC_SENSOR = "iot_alarm/sensor_data"

# flags
alarm_triggered = False

# connect to InfluxDB
influx_client = InfluxDBClient(
    url=f"http://{INFLUXDB_HOST}:{INFLUXDB_PORT}",
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))

# flask route for health check
@app.route('/')
def index():
    return "Server is running!"

# handle incoming MQTT messages
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global alarm_triggered
    topic = message.topic
    try:
        payload = json.loads(message.payload.decode())
        logging.info(f"Received from {payload['sensor_name']}, {payload}")
    except json.JSONDecodeError:
        logging.error(f"Received invalid JSON on topic {topic}: {message.payload.decode()}")
        return

    if topic == MQTT_TOPIC_SENSOR:
        try:
            # store sensor data in InfluxDB
            point = Point("sensor_data").tag("device", "esp32")
            value = int(payload["state"])
            point = point.field("bed_state", value)
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            logging.info("Sensor data written to InfluxDB.")
        except Exception as e:
            logging.error(f"Error writing to InfluxDB: {e}")

    # this is wrong. changing later after testing
    elif topic == MQTT_TOPIC_COMMAND:
        command = payload.get("command")
        if command == "trigger_alarm":
            alarm_triggered = True
            logging.info("Alarm triggered!")
        elif command == "stop_alarm":
            alarm_triggered = False
            logging.info("Alarm stopped.")

# Handle MQTT connect event
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT broker with reason code {rc}")
    mqtt.subscribe(MQTT_TOPIC_SENSOR)
    mqtt.subscribe(MQTT_TOPIC_COMMAND)

if __name__ == '__main__':
    # Notify ESP32 about broker IP in a separate thread
    send_broker_ip(alarm_ip=ESP32_IP, alarm_port=ESP32_PORT)


    # weather_data = get_weather_data()
    # if weather_data:
    #     print(f"Weather data: {weather_data}")

    # if alarm_triggered:
    #     print("!!! ALARM TRIGGERED !!! User needs to get up.")
    # Start Flask app
    app.run(host="0.0.0.0", port=5000)
