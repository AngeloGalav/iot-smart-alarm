from dfplayermini import Player
from machine import Pin, PWM
from time import sleep
import network
import umqtt.simple as mqtt  # MicroPython MQTT library
from secrets import WIFI_SSID, WIFI_PASSWORD

# Hardware setup
pressure_mat = Pin(18, Pin.IN, Pin.PULL_DOWN)
led = PWM(Pin(2), freq=1000)
music = Player(pin_TX=17, pin_RX=16)

# chimes ids setup
sound_connection_ok = 3
sound_angry_alarm = 1
sound_normal_alarm = 2

# stops any previously running sounds on the player
music.stop()

# MQTT setup
# MQTT_BROKER = ""
# MQTT_TOPIC_COMMAND = "iot_alarm/command"
# MQTT_TOPIC_SENSOR = "iot_alarm/sensor_data"

music.volume(20)
isPlaying = False
sampling_rate = 1

# led fade code for the connection step
def led_fade():
    for duty_cycle in range(0, 1024, 10):
        led.duty(duty_cycle)
        sleep(0.01)
    for duty_cycle in range(1023, -1, -10):
        led.duty(duty_cycle)
        sleep(0.01)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF) # esp32 in station mode
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # wait for wifi
    while not wlan.isconnected():
        led_fade()
        pass
    # if connected play chime
    music.play(track_id=sound_connection_ok)
    print("Connected to Wi-Fi")
    sleep(3)

# MQTT client setup
# def connect_mqtt():
#     client = mqtt.MQTTClient("esp32_alarm", MQTT_BROKER)
#     client.set_callback(mqtt_callback)
#     client.connect()
#     client.subscribe(MQTT_TOPIC_COMMAND)
#     print("Connected to MQTT broker")
#     return client

# Handle incoming MQTT messages
# def mqtt_callback(topic, msg):
#     global isPlaying, sampling_rate
#     msg = msg.decode("utf-8")
#     if "trigger_alarm" in msg:
#         start_alarm()
#     elif "stop_alarm" in msg:
#         stop_alarm()
#     elif "sampling_rate" in msg:
#         try:
#             sampling_rate = int(msg.split(":")[1])
#             print(f"Sampling rate set to {sampling_rate} seconds")
#         except ValueError:
#             print("Invalid sampling rate received")

# Start the alarm
def start_alarm():
    global isPlaying
    if not isPlaying:
        isPlaying = True
        music.play(track_id=sound_normal_alarm)
        led.duty(1000)
        print("Alarm triggered")

# Stop the alarm
def stop_alarm():
    global isPlaying
    if isPlaying:
        isPlaying = False
        music.stop()
        led.duty(0)
        print("Alarm stopped")

def check_pressure_mat():
    global isPlaying
    if pressure_mat.value(): # play only if user is in bed
        if isPlaying:
            stop_alarm()
    else:  #TODO: remove this after testing
        if not isPlaying:
            start_alarm()

# Main function
def main():
    connect_wifi()
    # client = connect_mqtt()

    while True:
        # client.check_msg()  # Check for incoming MQTT messages

        # send sensor state to mqtt broker
        # sensor_state = "in_bed" if pressure_mat.value() else "out_of_bed"
        # client.publish(MQTT_TOPIC_SENSOR, sensor_state)
        # print(f"Sensor state published: {sensor_state}")

        check_pressure_mat()
        sleep(sampling_rate)

main()
