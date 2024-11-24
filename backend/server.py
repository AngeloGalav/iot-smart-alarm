"""
This python script only gets the weather for the next our.
In the future it will also serve as the backend for the webapp and the esp32. Godo.
"""

import paho.mqtt.client as mqtt
from weather_utils import get_weather_data
import json
import time

# MQTT configuration
mqtt_broker_host = "0.0.0.0"
mqtt_broker_port = 1883 # default mqtt port
sensor_data_topic = "sensor/data"
alarm_control_topic = "alarm/control"

# flags
alarm_triggered = False
connected = False

# callback for when a message is received
def on_message(client, userdata, msg):
    global alarm_triggered

    topic = msg.topic
    payload = json.loads(msg.payload.decode())

    if topic == sensor_data_topic:
        print(f"Received sensor data: {payload}")
        # TODO: store payload

    elif topic == alarm_control_topic:
        command = payload.get("command")
        if command == "trigger_alarm":
            alarm_triggered = True
            print("Alarm triggered! Notifying microcontroller.")
        elif command == "stop_alarm":
            alarm_triggered = False
            print("Alarm stopped.")

# callback for when the MQTT client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe([(sensor_data_topic, 0), (alarm_control_topic, 0)])

def main():
    global alarm_triggered

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    while not connected:
        try:
            mqtt_client.connect(mqtt_broker_host, mqtt_broker_port, 60)
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
            weather_data = get_weather_data()
            if weather_data:
                print(f"Weather data: {weather_data}")

            if alarm_triggered:
                print("!!! ALARM TRIGGERED !!! User needs to get up.")

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == '__main__' :
    main()