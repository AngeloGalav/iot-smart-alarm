from dfplayermini import Player
from machine import Pin, PWM
from time import sleep, ticks_ms, ticks_diff
import network
import socket
import urequests  # MicroPython HTTP library
import umqtt.simple as mqtt  # MicroPython MQTT library
import uasyncio as asyncio
from esp_secrets import WIFI_SSID, WIFI_PASSWORD
import json

# Hardware setup
sensor_name = "esp32_alarm"
pressure_mat = Pin(18, Pin.IN, Pin.PULL_DOWN)
led = PWM(Pin(23), freq=1000)
music = Player(pin_TX=17, pin_RX=16)

# angry mode configs
alarm_start_time = None  # To track when the alarm started
angry_timeout = 30000    # Timeout for angry mode in milliseconds (30 seconds)
SECOND = 1000 # a second in milliseconds

tick_time = 0.5 # sensor reading time

# chimes ids setup
sound_angry_alarm = 2
sound_connection_ok = 1
sound_wait_mqtt = 5
sound_connection_complete = 3

sound_alarm_rainy = 7
sound_alarm_cloudy = 4
sound_alarm_sunny = 6

ringtones = {
    'sunny' : sound_alarm_sunny,
    'rainy' : sound_alarm_rainy,
    'cloudy' : sound_alarm_cloudy
}

current_alarm_song = ringtones['sunny']

# stops any previously running sounds on the player
music.stop()

# MQTT setup
MQTT_TOPIC_COMMAND = "iot_alarm/command"
MQTT_TOPIC_SENSOR = "iot_alarm/sensor_data"
MQTT_TOPIC_WEATHER = "iot_alarm/weather"
MQTT_TOPIC_DELAY = "iot_alarm/delay"

is_playing = False
is_angry_playing = False

alarm_go = False
alarm_ringing = False

# running average
w_size = 10           # running avg window size
start_thresh = 0.7    # trigger alarm if average exceeds this
running_average = 0.0
sensor_readings = []

# settings
use_http = True
http_async = False
angry_mode = False
get_delay = True
sampling_rate = 1
alarm_volume = 20
music.volume(alarm_volume)

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

    print("Looking for WiFi...")

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
    client.subscribe(MQTT_TOPIC_WEATHER)
    print("Connected to MQTT broker")
    music.play(track_id=sound_connection_complete)
    return client

# handle incoming MQTT messages
def mqtt_callback(topic, msg):
    global use_http, http_async, angry_mode, sampling_rate, alarm_go, w_size, current_alarm_song, tick_time

    msg = msg.decode("utf-8")
    topic = topic.decode('utf-8')
    print(f"Received message on topic {topic}: {msg}")

    if topic == MQTT_TOPIC_COMMAND :
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

                if 'vol' in data:
                    alarm_volume = int(data['vol'])
                    music.volume(alarm_volume)
                    print(f"Volume set to {alarm_volume}")

                if 'tick' in data:
                    tick_time = float(data['tick'])
                    print(f"Tickrate set to {tick_time}")

            except Exception as e:
                print(f"Error processing MQTT message: {e}")
    elif topic == MQTT_TOPIC_WEATHER:
        try:
            data = json.loads(msg)  # Assuming the message is JSON-formatted
            if "weather" in data:
                weather = data["weather"]
                current_alarm_song = ringtones.get(weather, current_alarm_song)
            else:
                print("Weather condition key not found in the message")
        except Exception as e:
            print(f"Error processing MQTT weather message: {e}")

async def async_http_post(url, data):
    global sampling_rate
    try:
        start = ticks_ms()
        response = urequests.post(url, json=data)
        response.close()  # close the connection immediately
        end = ticks_ms()
        print("POST request sent successfully.")
        if (get_delay) :
            ...
    except Exception as e:
        print(f"Error sending async POST request: {e}")


def publish_sensor_data(sensor_state, ip, mac, client, server_ip=None, c_type="http"):
    payload = {
        "sensor_name": sensor_name,
        "sensor_ip": ip,
        "sensor_mac": mac,
        "state": sensor_state,
        "state_avg" : running_average
    }
    if c_type != "http" :
        # mqtt transmission
        client.publish(MQTT_TOPIC_SENSOR, json.dumps(payload))
        print(f"Published using MQTT: {payload}")
    else :
        # http transmission
        try:
            if (http_async):
                print(f"Publishing payload using async HTTP... Payload: {payload}")
                asyncio.run(async_http_post(f"http://{server_ip}:5000/recv_data", payload))
            else :
                start = ticks_ms()
                print(f"Publishing payload using HTTP... Payload: {payload}")
                response = urequests.post(f"http://{server_ip}:5000/recv_data", json=payload)
                response.close()
                delay = ticks_diff(ticks_ms(), start)
                if (get_delay) :
                    client.publish(MQTT_TOPIC_DELAY, json.dumps({"delay": delay}))
        except Exception as e:
            print(f"HTTP error: {e}")


# Start the alarm
def start_alarm():
    global is_playing, alarm_start_time, is_angry_playing
    if not is_playing:
        is_playing = True
        alarm_start_time = ticks_ms()
        music.play(track_id=current_alarm_song)
        led.duty(1000)
    else:
        if angry_mode and ticks_diff(ticks_ms(), alarm_start_time) > angry_timeout and not is_angry_playing:
            music.play(track_id=sound_angry_alarm)  # Play angry alarm
            print("Angry mode activated! Playing angry alarm.")
            is_angry_playing = True

# Stop the alarm
def stop_alarm():
    global is_playing, alarm_start_time, is_angry_playing
    if is_playing:
        is_playing = False
        is_angry_playing = False
        alarm_start_time = None
        music.stop()
        led.duty(0)

def check_pressure_mat():
    global is_playing, sensor_readings, alarm_go, running_average
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


def main():
    ip, mac = connect_wifi(static_ip=None)

    music.play(track_id=sound_wait_mqtt)
    broker_ip = start_server()
    client = connect_mqtt(broker_ip=broker_ip)
    sleep(2)

    start_time = ticks_ms()
    while True:
        try:
            if ticks_diff(ticks_ms(), start_time) >= sampling_rate*SECOND :
                client.check_msg()  # Check for incoming MQTT messages

                # send sensor state to HTTP or MQTT broker
                sensor_state = int(not pressure_mat.value())

                # led blinks at each request made
                led.duty(1023)
                if use_http:
                    # use http for sensor data
                    publish_sensor_data(sensor_state=sensor_state,
                            ip=ip, mac=mac, client=client, server_ip=broker_ip,
                            c_type="http")
                else:
                    # use mqtt for sensor data
                    publish_sensor_data(sensor_state=sensor_state,
                            ip=ip, mac=mac, client=client, c_type="mqtt")
                led.duty(0)

                # restart sampling rate timer
                start_time = ticks_ms()
            sleep(tick_time)
            check_pressure_mat()
        except OSError as e:
            print(f"OSError occurred: {e}")
            # Fallback for connection issues
            # Attempt to reconnect to Wi-Fi
            try:
                print("Reconnecting to Wi-Fi...")
                ip, mac = connect_wifi(static_ip=None)
                print("Wi-Fi reconnected successfully.")
            except Exception as wifi_error:
                print(f"Failed to reconnect to Wi-Fi: {wifi_error}")
                continue

            # Attempt to reconnect to MQTT broker
            try:
                print("Reconnecting to MQTT broker...")
                client = connect_mqtt(broker_ip=broker_ip)
                print("MQTT broker reconnected successfully.")
            except Exception as mqtt_error:
                print(f"Failed to reconnect to MQTT broker: {mqtt_error}")
                continue

            # restart sampling rate timer
            start_time = ticks_ms()

if __name__ == '__main__' :
    main()