from flask import Flask, jsonify
import json
import os
from flask_cors import CORS
import logging
from influxdb_client import InfluxDBClient, WriteOptions
from flask_mqtt import Mqtt
from analysis_secrets import influxdb_api_token
from accuracy_script import get_sensor_sleep_data

logging.basicConfig(level=logging.INFO)

# flask config
app = Flask(__name__)
FLASK_APP_PORT = int(os.getenv("FLASK_APP_PORT", 5000))

# MQTT configuration
app.config['MQTT_BROKER_URL'] = os.getenv('MQTT_BROKER_HOST', 'localhost')
app.config['MQTT_BROKER_PORT'] = int(os.getenv('MQTT_BROKER_PORT', 1883))

# MQTT topic for receiving delay data
MQTT_TOPIC_DELAY = "iot_alarm/delay"

try:
    mqtt = Mqtt(app)
except Exception as e:
    logging.error(f"Error starting MQTT connection: {e}\n" \
        "Have you started the MQTT Broker?")
    exit()

CORS(app) # enable CORS for all routes

# Comulative Average setup
cumulative_average = 0
num_delays = 0

# InfluxDB configuration
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUXDB_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
INFLUXDB_BUCKET = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET", "iot-bucket")
INFLUXDB_TOKEN = influxdb_api_token
INFLUXDB_ORG = os.getenv("DOCKER_INFLUXDB_INIT_ORG", "iot-org")

# flags
alarm_triggered = False
alarm_filename = "alarms.json"
alarms = []
latest_alarm_id = 0

# connect to InfluxDB
influx_client = InfluxDBClient(
    url=f"http://{INFLUXDB_HOST}:{INFLUXDB_PORT}",
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global cumulative_average, num_delays
    topic = message.topic
    try:
        payload = json.loads(message.payload.decode())
        logging.info(f"MQTT received from broker on topic: {topic}")

        if topic == MQTT_TOPIC_DELAY:
            try:
                delay = float(payload.get("delay"))
                if delay is not None:
                    # Update the cumulative average
                    num_delays += 1
                    cumulative_average = ((cumulative_average * (num_delays - 1)) + delay) / num_delays
                    logging.info(f"Received delay: {delay} ms, Updated CA: {cumulative_average:.2f} ms")
                else:
                    logging.error(f"Invalid delay value received: {payload}")
            except Exception as e:
                logging.error(f"Error processing delay data: {e}")

    except json.JSONDecodeError:
        logging.error(f"Received invalid JSON on topic {topic}: {message.payload.decode()}")

# Handle MQTT connect event
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT broker with reason code {rc}")
    mqtt.subscribe(MQTT_TOPIC_DELAY)

@app.route('/delay', methods=['GET'])
def get_average_delay():
    global cumulative_average
    return jsonify({"delay": cumulative_average}), 200

@app.route('/sleep_time', methods=['GET'])
def sleep_time():
    try:
        sleep_time = get_sensor_sleep_data(client=influx_client, org=INFLUXDB_ORG, bucket=INFLUXDB_BUCKET)
        return jsonify({"sleep": sleep_time}), 200
    except:
        return "Could not compute sleep data", 500

if __name__ == '__main__':
    # Start MQTT app
    mqtt.init_app(app)

    # Start Flask app/backend server
    app.run(host="0.0.0.0", port=FLASK_APP_PORT)
