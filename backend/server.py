from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS
import logging
from influxdb_client import InfluxDBClient, Point, WriteOptions
from flask_mqtt import Mqtt
from backend_secrets import influxdb_api_token
from weather_utils import get_weather_data
from mqtt_utils import send_broker_ip
from alarm_utils import save_alarms_to_file, load_alarms_from_file

logging.basicConfig(level=logging.INFO)

# flask config
app = Flask(__name__)
FLASK_APP_PORT = int(os.getenv("FLASK_APP_PORT", 5000))

# MQTT configuration
app.config['MQTT_BROKER_URL'] = os.getenv('MQTT_BROKER_HOST', 'localhost')
app.config['MQTT_BROKER_PORT'] = int(os.getenv('MQTT_BROKER_PORT', 1883))

mqtt = Mqtt(app)
CORS(app) # enable CORS for all routes

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

def handle_alarm_trigger():
    pass

# ----- MQTT ENDPOINTS ------

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

# ----- API ENDPOINTS ------

@app.route('/alarms', methods=['POST'])
def add_alarm():
    global alarms
    global latest_alarm_id
    data = request.json
    print ("I TRIED FUCK!")
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    latest_alarm_id += 1
    alarm = {
        "id": latest_alarm_id,  # Simple ID generator
        "time": data.get("time"),
        "weekdays": data.get("weekdays", []),
        "active": True
    }
    alarms.append(alarm)
    save_alarms_to_file(alarm_filename, alarms)
    return jsonify({"message": "Alarm added successfully", "alarm": alarm}), 201

@app.route('/alarms', methods=['GET'])
def get_alarms():
    '''
    Returns all alarms.
    '''
    return jsonify(alarms)

@app.route('/alarms/<int:alarm_id>', methods=['PUT'])
def modify_alarm(alarm_id):
    '''
    Modifies the properties of an alarm.
    '''
    global alarms
    data = request.json
    for alarm in alarms:
        if alarm["id"] == alarm_id:
            alarm["time"] = data.get("time", alarm["time"])
            alarm["weekdays"] = data.get("weekdays", alarm["weekdays"])
            alarm["active"] = data.get("active", alarm["active"])
            save_alarms_to_file(alarm_filename, alarms)
            return jsonify({"message": "Alarm updated successfully", "alarm": alarm}), 200

    return jsonify({"error": "Alarm not found"}), 404

# API: Remove an alarm
@app.route('/alarms/<int:alarm_id>', methods=['DELETE'])
def remove_alarm(alarm_id):
    '''
    Deletes an alarm.
    '''
    global alarms
    alarms = [alarm for alarm in alarms if alarm["id"] != alarm_id]
    save_alarms_to_file(alarm_filename, alarms)  # Save to file after deletion
    return jsonify({"message": "Alarm deleted successfully"}), 200

# PATCH modifies the instance, while directly creates a new one
@app.route('/alarms/<int:alarm_id>/toggle', methods=['PATCH'])
def toggle_alarm(alarm_id):
    '''
    Enables alarm toggling.
    '''
    global alarms
    for alarm in alarms:
        if alarm["id"] == alarm_id:
            alarm["active"] = not alarm["active"]
            save_alarms_to_file(alarm_filename, alarms)
            return jsonify({"message": "Alarm toggled successfully", "alarm": alarm}), 200

    return jsonify({"error": "Alarm not found"}), 404


if __name__ == '__main__':
    # Notify ESP32 about broker IP in a separate thread
    alarms = load_alarms_from_file(alarm_filename)
    latest_alarm_id = len(alarms)
    # send_broker_ip(alarm_ip=ESP32_IP, alarm_port=ESP32_PORT)


    # weather_data = get_weather_data()
    # if weather_data:
    #     print(f"Weather data: {weather_data}")

    if alarm_triggered:
        logging.info("Triggered alarm!")
        handle_alarm_trigger()

    # start Flask app/backend server
    app.run(host="0.0.0.0", port=FLASK_APP_PORT)
