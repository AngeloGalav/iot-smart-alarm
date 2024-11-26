"""
Multi-purpose server.
It should:
- collect the data from the esp32
- handle requests from the frontend
- manage the alarms
"""

import paho.mqtt.client as mqtt
from weather_utils import get_weather_data
import json
import os
import time
from backend_secrets import influxdb_api_token
from influxdb_client import InfluxDBClient, Point, WriteOptions

# MQTT config
MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', 1883))

# influxdb config
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUXDB_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
INFLUXDB_BUCKET = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET", "iot-bucket")
INFLUXDB_TOKEN = influxdb_api_token
INFLUXDB_ORG = os.getenv("DOCKER_INFLUXDB_INIT_ORG", "iot-org")

# mqtt topics
MQTT_TOPIC_COMMAND = "iot_alarm/command"
MQTT_TOPIC_SENSOR = "iot_alarm/sensor_data"

# flags
alarm_triggered = False
connected = False

# Connect to InfluxDB
influx_client = InfluxDBClient(
    url=f"http://{INFLUXDB_HOST}:{INFLUXDB_PORT}",
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))

# callback for when a message is received
def on_message(client, userdata, msg):
    global alarm_triggered
    print("received message!")

    topic = msg.topic
    # try if msg is json
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received from {payload["sensor_name"]}, {payload}")
    except json.JSONDecodeError:
        print(f"Received invalid JSON on topic {topic}: {msg.payload.decode()}")
        return

    if topic == MQTT_TOPIC_SENSOR:
        # store sensor data in InfluxDB
        try:
            point = Point("sensor_data").tag("device", "esp32")
            value = int(payload["state"])
            point = point.field("bed_state", value)
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            print("Sensor data written to InfluxDB.")
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")

    elif topic == MQTT_TOPIC_COMMAND:
        command = payload.get("command")
        if command == "trigger_alarm":
            alarm_triggered = True
            print("Alarm triggered! Notifying microcontroller.")
        elif command == "stop_alarm":
            alarm_triggered = False
            print("Alarm stopped.")

# callback for when the MQTT client connects to the broker
# mqttv5 requires the properties code
def on_connect(client, userdata, flags, reasonCode, properties=None):
    global connected
    print(f"Connected to MQTT broker with reason code {reasonCode}")
    client.subscribe([(MQTT_TOPIC_SENSOR, 0), (MQTT_TOPIC_COMMAND, 0)])
    connected = True

def main():
    global alarm_triggered

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    while not connected:
        try:
            mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            # loop start calls loop, which allows a "looping" connection
            # on a different thread
            mqtt_client.loop_start()
            time.sleep(2)
        except Exception as e:
            print(f"Connection attempt failed: {e}")
            time.sleep(5)  # Wait before retrying

    try:
        print("Fetching weather data and listening for MQTT messages...")
        mqtt_client.loop_start()

        while True:
            # fetch weather data periodically
            time.sleep(1)
            # weather_data = get_weather_data()
            # if weather_data:
            #     print(f"Weather data: {weather_data}")

            # if alarm_triggered:
            #     print("!!! ALARM TRIGGERED !!! User needs to get up.")

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == '__main__' :
    main()