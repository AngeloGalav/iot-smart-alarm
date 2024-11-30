from flask import Flask, request, jsonify
import json
import threading
import os
import time
from datetime import datetime
from flask_cors import CORS
import logging
from influxdb_client import InfluxDBClient, Point, WriteOptions
from flask_mqtt import Mqtt
from backend_secrets import influxdb_api_token
from weather_utils import get_weather_data
import mqtt_utils
from alarm_utils import save_alarms_to_file, load_alarms_from_file

logging.basicConfig(level=logging.INFO)

# flask config
app = Flask(__name__)
FLASK_APP_PORT = int(os.getenv("FLASK_APP_PORT", 5000))

# MQTT configuration
app.config['MQTT_BROKER_URL'] = os.getenv('MQTT_BROKER_HOST', 'localhost')
app.config['MQTT_BROKER_PORT'] = int(os.getenv('MQTT_BROKER_PORT', 1883))

try:
    mqtt = Mqtt(app)
except Exception as e:
    logging.error(f"Error starting MQTT connection: {e}\n" \
        "Have you started the MQTT Broker?")
    exit()


CORS(app) # enable CORS for all routes

# ESP32 network info
ESP32_IP = "192.168.148.56"
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

# ----- MQTT ENDPOINTS ------

# handle incoming MQTT messages
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global alarm_triggered
    topic = message.topic
    try:
        payload = json.loads(message.payload.decode())
        logging.info(f"MQTT received from broker")

        # if I receive a message from esp32
        # it's already connected, stop send_broker_ip thread
        if not mqtt_utils.get_alarm_connected():
            mqtt_utils.set_alarm_connected(True)

    except json.JSONDecodeError:
        logging.error(f"Received invalid JSON on topic {topic}: {message.payload.decode()}")
        return

    if topic == MQTT_TOPIC_SENSOR:
        try:
            sensor_name = payload.get('sensor_name')
            sensor_ip = payload.get('sensor_ip')
            state = payload.get('state')

            if sensor_name is None or sensor_ip is None or state is None:
                logging.error("Sensor data missing required fields.")

            # store sensor data in InfluxDB
            point = Point("sensor_data").tag("device", sensor_name)
            value = int(state)
            point = point.field("bed_state", value)
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            logging.info("Sensor data written to InfluxDB.")
        except Exception as e:
            logging.error(f"Error writing to InfluxDB: {e}")

# Handle MQTT connect event
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT broker with reason code {rc}")
    mqtt.subscribe(MQTT_TOPIC_SENSOR)
    mqtt.subscribe(MQTT_TOPIC_COMMAND)

# ----- API ENDPOINTS ------
@app.route('/recv_data', methods=['POST'])
def recv_data():
    try:
        # if I receive a message from esp32
        # it's already connected, stop send_broker_ip thread
        if not mqtt_utils.get_alarm_connected():
            mqtt_utils.set_alarm_connected(True)

        # Get JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        logging.info(f"Received data: {data}")

        # Extract the required fields
        sensor_name = data.get('sensor_name')
        sensor_ip = data.get('sensor_ip')
        sensor_mac = data.get('sensor_mac')
        state = data.get('state')

        if sensor_name is None or sensor_ip is None or sensor_mac is None or state is None:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # write data to InfluxDB
        try:
            # store sensor data in InfluxDB
            point = Point("sensor_data").tag("device", sensor_name)
            value = int(state)
            point = point.field("bed_state", value)
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            logging.info("Sensor data written to InfluxDB.")
        except Exception as e:
            logging.error(f"Error writing to InfluxDB: {e}")

        # return a success response
        return jsonify({"status": "success", "message": "Data received and stored successfully"}), 200

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/alarms', methods=['POST'])
def add_alarm():
    global alarms
    global latest_alarm_id
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    latest_alarm_id += 1
    alarm = {
        "id": latest_alarm_id,  # Simple ID generator
        "time": data.get("time"),
        "weekdays": data.get("weekdays", []),
        "active": True
    }

    if alarm.get("time") is None or alarm.get("time") == []:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

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
    len1 = len(alarms)
    alarms = [alarm for alarm in alarms if alarm["id"] != alarm_id]
    if len(alarms) != len1-1:
        return jsonify({"message": "Alarm was not deleted."}), 400
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

@app.route('/stop_alarm', methods=['POST'])
def stop_alarm():
    '''
    Stops alarm running on the esp32.
    '''
    logging.info(f"Stopping alarm running on the esp32.")
    mqtt.publish(MQTT_TOPIC_COMMAND, json.dumps({"command": "stop_alarm"}))

@app.route('/switch_protocol', methods=['POST'])
def switch_protocol():
    '''
    Stops alarm running on the esp32.
    '''
    logging.info(f"Switched alarm data transmission protocol.")
    mqtt.publish(MQTT_TOPIC_COMMAND, json.dumps({"command": "switch_protocol"}))

@app.route('/sampling_rate', methods=['POST'])
def sampling_rate():
    '''
    Receives a sample rate from the POST request, validates it, and sends it to the ESP32 via MQTT.
    '''
    try:
        data = request.get_json()
        sample_rate_val = data.get('sampling_rate')
        if not isinstance(sample_rate_val, int) or sample_rate_val <= 0:
            return jsonify({"status": "error", "message": "'sample_rate' must be a positive integer"}), 400

        mqtt.publish(MQTT_TOPIC_COMMAND, json.dumps({"command": "sample_rate", "value": sample_rate_val}))
        logging.info(f"Published sample rate: {sample_rate_val} to topic {MQTT_TOPIC_COMMAND}")

        return jsonify({"status": "success", "message": f"Sample rate set to {sample_rate_val}"}), 200

    except Exception as e:
        logging.error(f"Error in /sample_rate endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ----- Alarm clock thread -----
def alarm_clock():
    """
    Runs in a separate thread, continuously checks for active alarms and triggers them.
    """
    logging.info("Alarm clock manager thread ready.")
    global alarms, alarm_triggered

    mqtt_utils.send_broker_ip(alarm_ip=ESP32_IP, alarm_port=ESP32_PORT)

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")  # format: HH:MM
        current_weekday = now.weekday()  # weekdays: 0-6 mon-sun

        for alarm in alarms:
            wk_days_cache = alarm.get("weekdays", [])
            if alarm["active"] and alarm["time"] == current_time \
                and ((current_weekday in wk_days_cache) or wk_days_cache == []):
                    # if wkd == [], then no repetition schedule is set: it will be repeated everyday
                    if not alarm_triggered:
                        alarm_triggered = True
                        logging.info(f"Alarm {alarm['id']} triggered at {current_time} on weekday {current_weekday}")
                        mqtt.publish(MQTT_TOPIC_COMMAND, json.dumps({"command": "trigger_alarm"}))
        time.sleep(10)  # check every 10 seconds, to make it less expensive



if __name__ == '__main__':
    # Notify ESP32 about broker IP in a separate thread
    alarms = load_alarms_from_file(alarm_filename)
    latest_alarm_id = len(alarms)

    # Start MQTT app
    mqtt.init_app(app)

    # weather_data = get_weather_data()
    # if weather_data:
    #     print(f"Weather data: {weather_data}")

    # set the alarm clock thread
    alarm_thread = threading.Thread(target=alarm_clock, daemon=True)
    alarm_thread.start()

    # start Flask app/backend server
    app.run(host="0.0.0.0", port=FLASK_APP_PORT)
