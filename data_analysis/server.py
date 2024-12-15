from flask import Flask, jsonify
import json
import os
from flask_cors import CORS
import logging
from influxdb_client import InfluxDBClient, WriteOptions, Point
from flask_mqtt import Mqtt
from analysis_secrets import influxdb_api_token
from sleep_accuracy import get_total_sleep_time
import pickle
import pandas as pd
import csv
from threading import Thread
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO)
# flask config
app = Flask(__name__)
FLASK_APP_PORT = int(os.getenv("FLASK_APP_PORT", 5001))

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

# file in which the delay data is to be stored
delay_filename = "delay_data.csv"

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

# CumAvg of sleeping time
total_sleep_time_sum = 0


days_count = 0
current_day = datetime.now().date()

# Prophet configuration
MODEL_PATH = "bed_predictions_fake.pkl"
prophet_model = None

def load_prophet_model():
    global prophet_model
    try:
        with open(MODEL_PATH, 'rb') as f:
            prophet_model = pickle.load(f)
        logging.info("Prophet model loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading Prophet model: {e}")

def initialize_csv(file_path):
    """Initialize the CSV file. Create if it doesn't exist, otherwise open in append mode."""
    file_exists = os.path.exists(file_path)
    if not file_exists:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["time", "delay", "cum_avg"])
    return file_exists


def log_delay_to_csv(file_path, delay, cumulative_average):
    """Log the delay and cumulative average to the CSV file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, delay, cumulative_average])


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
                    # update the cumulative average
                    num_delays += 1
                    cumulative_average = ((cumulative_average * (num_delays - 1)) + delay) / num_delays
                    logging.info(f"Received delay: {delay} ms, Updated CA: {cumulative_average:.2f} ms")

                    # save delay info to data
                    log_delay_to_csv(delay_filename, delay, cumulative_average)
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

@app.route('/bed_state_pred', methods=['GET'])
def bed_state_pred():
    """
    Predicts the likelihood of the user being in bed at the current datetime using the Prophet model.
    """
    global prophet_model
    if not prophet_model:
        return jsonify({"error": "Prophet model is not loaded."}), 500

    try:
        # get the current datetime
        current_time = datetime.now()
        current_time_formatted = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # create a DataFrame for prediction
        future_df = pd.DataFrame({'ds': [current_time]})

        # forecasting
        forecast = prophet_model.predict(future_df)
        forecast['yhat'] = forecast['yhat'].clip(lower=0, upper=1)
        # clip so it does not show values higher than 1 or lower than 0
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0, upper=1)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0, upper=1)
        likelihood = forecast['yhat'].iloc[0]

        return jsonify({
            "current_time": current_time_formatted,  # return full datetime
            "likelihood": round(likelihood*100, 2)  # rounded to 2 decimals
        }), 200
    except Exception as e:
        logging.error(f"Error predicting bed state likelihood: {e}")
        return jsonify({"error": "Could not compute bed state likelihood."}), 500

@app.route('/sleep_time', methods=['GET'])
def sleep_time():
    try:
        sleep_time = get_total_sleep_time(client=influx_client, org=INFLUXDB_ORG, bucket=INFLUXDB_BUCKET, time='24h')
        return jsonify({"sleep": sleep_time}), 200
    except Exception as e:
        logging.error(f"Error computing sleep data: {e}")
        return "Could not compute sleep data", 500

def initialize_cumulative_average():
    '''
    Extract current sleep average data from InfluxDB.
    '''
    global total_sleep_time_sum, days_count

    try:
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: 0)  // Query all historical data
          |> filter(fn: (r) => r._measurement == "daily_sleep_average" and r._field == "average_sleep")
        '''
        result = influx_client.query_api().query(query, org=INFLUXDB_ORG)

        # Collect historical values
        for table in result:
            for record in table.records:
                total_sleep_time_sum += record.get_value()
                days_count += 1

        logging.info(f"Initialized cumulative average from past data: Total Sleep Time Sum = {total_sleep_time_sum}, Days Count = {days_count}")
    except Exception as e:
        logging.error(f"Error initializing cumulative average from past data: {e}")

def compute_daily_average_sleep():
    '''
    Computes the average sleeping time and sends it to influxdb.
    '''
    global total_sleep_time_sum, days_count, current_day
    initialize_cumulative_average()

    while True:
        now = datetime.now()
        # if day has ended...
        if now.date() > current_day:
            try:
                # get total sleeping time from prev day
                sleep_time = get_total_sleep_time(
                    client=influx_client,
                    org=INFLUXDB_ORG,
                    bucket=INFLUXDB_BUCKET,
                    time="24h"
                )
                if sleep_time:
                    total_sleep_time_sum += sleep_time
                    days_count += 1
                    cumulative_average_sleep = total_sleep_time_sum / days_count

                    logging.info(f"Daily Average Sleep: {cumulative_average_sleep:.2f} hours")
                    # send data to InfluxDB
                    point = Point("daily_sleep_average") \
                        .field("average_sleep", cumulative_average_sleep) \
                        .time(now - timedelta(days=1))
                    # as the data is the one for the previous day,
                    # we use the timestamp of the previous day
                    # (i.e. we still have to compute the data for today)
                    write_api.write(bucket=INFLUXDB_BUCKET, record=point)
                    logging.info("Daily average sleep written to InfluxDB.")
            except Exception as e:
                logging.error(f"Error computing or writing daily sleep average: {e}")

            # update the current day
            current_day = now.date()

        time.sleep(60)


if __name__ == '__main__':
    initialize_csv(delay_filename)

    # setup prediction system
    load_prophet_model()

    # compute compute_daily_average_sleep every minute in thread
    Thread(target=compute_daily_average_sleep, daemon=True).start()

    # Start MQTT app
    mqtt.init_app(app)

    # Start Flask app/backend server
    app.run(host="0.0.0.0", port=FLASK_APP_PORT)


