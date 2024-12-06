from dfplayermini import Player
from machine import Pin, PWM
from time import sleep, ticks_ms
import network
import socket
import urequests  # MicroPython HTTP library
import umqtt.simple as mqtt  # MicroPython MQTT library
import uasyncio as asyncio
from esp_secrets import WIFI_SSID, WIFI_PASSWORD
import json

# Network setup
static_ip_config = (
    "192.168.148.56",  # IP Address for ESP32
    "255.255.255.0", # Subnet mask
    "192.168.254.2",
    "192.168.254.2"
)

# Hardware setup
sensor_name = "sensorino_esp32"
pressure_mat = Pin(18, Pin.IN, Pin.PULL_DOWN)
led = PWM(Pin(2), freq=1000)
music = Player(pin_TX=17, pin_RX=16)

# chimes ids setup
sound_angry_alarm = 1
sound_normal_alarm = 2
sound_connection_ok = 4
sound_wait_mqtt = 5
sound_connection_complete = 3

# stops any previously running sounds on the player
music.stop()

# MQTT setup
MQTT_TOPIC_COMMAND = "iot_alarm/command"
MQTT_TOPIC_SENSOR = "iot_alarm/sensor_data"

music.volume(10)
is_playing = False

alarm_go = True
alarm_ringing = False

# running average
w_size = 10           # running avg window size
start_thresh = 0.7    # trigger alarm if average exceeds this
sensor_readings = []

# settings
use_http = True
http_async = False
angry_mode = False
sampling_rate = 1

# led fade code for the connection step
def led_fade():
    for duty_cycle in range(0, 1024, 10):
        led.duty(duty_cycle)
        sleep(0.01)
    for duty_cycle in range(1023, -1, -10):
        led.duty(duty_cycle)
        sleep(0.01)

def connect_wifi(static_ip=None, hostname='esp32_alarm'):
    wlan = network.WLAN(network.STA_IF) # esp32 in station mode
    wlan.active(True)

    # set hostname for dynamic connection
    wlan.config(dhcp_hostname = hostname)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # wait for wifi
    while not wlan.isconnected():
        led_fade()
        pass

    mac = wlan.config('mac').hex()
    # if connected play chime
    music.play(track_id=sound_connection_ok)
    host = wlan.config('dhcp_hostname')
    print(f"Connected to Wi-Fi\nMy MAC Address is: {mac}")
    print("Network config:", wlan.ifconfig(), 'hostname: ', host)
    sleep(3)
    return wlan.ifconfig()[0], mac

def start_server(listener_port=8080, buf_size=1024):
    '''
    Function to get the broker/server ip through TCP.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', listener_port))  # listen on all available network interfaces
    s.listen(1)
    print(f"Listening for broker IP on port {listener_port}...")

    conn, addr = s.accept()
    print(f"Connection from {addr}")

    broker_ip = None
    while True:
        data = conn.recv(buf_size)
        if not data:
            break

        broker_ip = data.decode().strip()
        print(f"Received broker IP: {broker_ip}")

        # confirm recv to the sender
        conn.send(b"ACK")
        break

    conn.close()
    s.close()

    return broker_ip

# MQTT client setup
def connect_mqtt(broker_ip):
    client = mqtt.MQTTClient("esp32_alarm", broker_ip)
    client.set_callback(mqtt_callback)
    client.connect()
    # if connected play chime
    client.subscribe(MQTT_TOPIC_COMMAND)
    print("Connected to MQTT broker")
    music.play(track_id=sound_connection_complete)
    return client

# handle incoming MQTT messages
def mqtt_callback(topic, msg):
    global use_http, http_async, angry_mode, sampling_rate, alarm_go, w_size

    msg = msg.decode("utf-8")
    print(f"Received message on topic {topic.decode('utf-8')}: {msg}")
    data = json.loads(msg)  # Parse the JSON data

    if "trigger_alarm" in msg:
        alarm_go = True
    elif "stop_alarm" in msg:
        stop_alarm()
        alarm_go = False
    elif "sampling_rate" in msg:
        try:
            val_to_clean = msg.split(":")[-1]
            number = ''.join(c for c in val_to_clean if c.isdigit() or c == '.')
            sampling_rate = float(number)
            print(f"Sampling rate set to {sampling_rate} seconds")
        except ValueError:
            print("Invalid sampling rate received", sampling_rate)
    else:
        # handling settings
        try:
            data = json.loads(msg)
            if 'use_mqtt' in data:
                use_http = not data['use_mqtt']
                print(f"Data trasnmission protocol set to: {'HTTP' if use_http else 'MQTT'}")

            if 'use_async_http' in data:
                http_async = data['use_async_http']
                print(f"HTTP mode set to: {'async' if http_async else 'normal'}")

            if 'angry_mode' in data:
                angry_mode = data['angry_mode']
                print(f"Angry mode {'enabled' if angry_mode else 'disabled'}")

            if 'samplingRate' in data:
                sampling_rate = float(data['samplingRate'])
                print(f"Sampling rate set to {sampling_rate}")

            if 'w_size' in data:
                w_size = int(data['w_size'])
                print(f"Window size set to {w_size}")
        except Exception as e:
            print(f"Error processing MQTT message: {e}")


async def async_http_post(url, data):
    global sampling_rate
    try:
        response = urequests.post(url, json=data)
        response.close()  # close the connection immediately
        print("POST request sent successfully.")
    except Exception as e:
        print(f"Error sending async POST request: {e}")


def publish_sensor_data(sensor_state, ip, mac, client=None, broker_ip=None):
    payload = {
        "sensor_name": sensor_name,
        "sensor_ip": ip,
        "sensor_mac": mac,
        "state": sensor_state,
    }
    if client is not None :
        client.publish(MQTT_TOPIC_SENSOR, json.dumps(payload))
        print(f"Published using MQTT: {payload}")
    else :
        try:
            if (http_async):
                print(f"Publishing payload using async HTTP... Payload: {payload}")
                asyncio.run(async_http_post(f"http://{broker_ip}:5000/recv_data", payload))
            else :
                print(f"Publishing payload using HTTP... Payload: {payload}")
                response = urequests.post(f"http://{broker_ip}:5000/recv_data", json=payload)
                response.close()
        except Exception as e:
            print(f"HTTP error: {e}")

# Start the alarm
def start_alarm():
    global is_playing
    if not is_playing:
        is_playing = True
        music.play(track_id=sound_normal_alarm)
        led.duty(1000)

# Stop the alarm
def stop_alarm():
    global is_playing
    if is_playing:
        is_playing = False
        music.stop()
        led.duty(0)

def check_pressure_mat():
    global is_playing, sensor_readings, alarm_go

    # update the sliding window
    if len(sensor_readings) >= w_size:
        sensor_readings.pop(0)  # Remove the oldest reading

    # add sensor state
    sensor_state = not pressure_mat.value()
    sensor_readings.append(sensor_state)

    # compute running average
    running_average = sum(sensor_readings) / len(sensor_readings)
    print(f"Running Average: {running_average:.2f}")

    # trigger alarm based on flags
    if running_average > start_thresh and alarm_go:
        start_alarm()
    elif running_average < (1-start_thresh) and is_playing:
        stop_alarm()
        alarm_go = False


# Main function
def main():
    ip, mac = connect_wifi(static_ip=None)

    music.play(track_id=sound_wait_mqtt)
    broker_ip = start_server()
    client = connect_mqtt(broker_ip=broker_ip)
    sleep(2)

    while True:
        try:
            client.check_msg()  # Check for incoming MQTT messages

            # send sensor state to HTTP or MQTT broker
            sensor_state = not pressure_mat.value()
            if use_http:
                # use http for sensor data
                publish_sensor_data(sensor_state=sensor_state, ip=ip, mac=mac, broker_ip=broker_ip)
            else:
                # use mqtt for sensor data
                publish_sensor_data(sensor_state=sensor_state, ip=ip, mac=mac, client=client)

            check_pressure_mat()
            print("TICK!")
            sleep(sampling_rate)
        except OSError as e:
            if not use_http:
                print(f"Error: {e}. Reconnecting...")
                client = connect_mqtt(broker_ip=broker_ip)  # Reconnect to the MQTT broker
            else:
                print(f"Error processing request: {e}.")

if __name__ == '__main__' :
    main()