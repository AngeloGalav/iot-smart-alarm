import argparse
from influxdb_client import InfluxDBClient, Point, WritePrecision
import numpy as np
import csv
import os
from datetime import datetime
from analysis_secrets import influxdb_api_token
import logging

logging.basicConfig(level=logging.INFO)

def get_total_sleep_time(client, bucket, org):
    """Retrieve total sleep time data from InfluxDB."""
    query_api = client.query_api()

    # Query raw bed_state data over the last day
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -1d)
        |> filter(fn: (r) => r._measurement == "sensor_data")
        |> filter(fn: (r) => r._field == "bed_state")
        |> sort(columns: ["_time"])
    '''

    try:
        result = query_api.query(org=org, query=query)

        # collect all timestamps and bed states in last 24h
        timestamps = []
        bed_states = []
        for table in result:
            for record in table.records:
                timestamps.append(str(record.get_time()))
                bed_states.append(record.get_value())

        if not timestamps or not bed_states:
            logging.error("No sleep data available from the sensor.")
            return None

        # compute total sleep time
        total_sleep_time = 0
        for i in range(1, len(timestamps)):
            # we sum all the timestep differences where state was 1
            if bed_states[i - 1] == 1:
                start_time = datetime.fromisoformat(timestamps[i - 1])
                end_time = datetime.fromisoformat(timestamps[i])
                total_sleep_time += (end_time - start_time).total_seconds()
        # Convert total sleep time to hours
        return total_sleep_time / 3600

    except Exception as e:
        logging.error(f"Error in querying or processing data from InfluxDB: {e}")
        return None

def save_accuracy_to_csv(ground_truth, sensor_total_sleep, accuracy):
    """
    Save computed accuracy to a CSV file. In this case, if the file is present, the accuracy is appended.
    Otherwise, the accuracy is written in the new file.
    """
    file_exists = os.path.exists('sensor_accuracy.csv')

    with open('sensor_accuracy.csv', 'a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Sensor Name', 'Ground Truth (hours)', 'Measured Total (hours)', 'Accuracy (%)'])
        writer.writerow(['Sleep Sensor', ground_truth, sensor_total_sleep, accuracy])

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Calculate the accuracy of the sleep sensor data.")
    parser.add_argument('ground_truth', type=float, help="Ground truth sleep time in hours, e.g., 8.0")
    args = parser.parse_args()

    # influxdb hostname and port
    host = os.getenv('INFLUXDB_HOST', 'localhost')
    port = int(os.getenv('INFLUXDB_PORT', 8086))

    # bucket and org for influxdb
    org = 'iot-org'
    bucket = 'iot-bucket'

    client = InfluxDBClient(url=f"http://{host}:{port}", token=influxdb_api_token, org=org)

    sensor_total_sleep = get_total_sleep_time(client, bucket, org)

    if sensor_total_sleep is not None:
        accuracy = 100 - (np.abs(sensor_total_sleep - args.ground_truth) / args.ground_truth * 100)
        print(f"Total Sensor Sleep Duration: {sensor_total_sleep:.2f} hours")
        print(f"Accuracy of the sensor compared to ground truth: {accuracy:.2f}%")

        save_accuracy_to_csv(args.ground_truth, sensor_total_sleep, accuracy)

    client.close()

if __name__ == '__main__':
    main()
