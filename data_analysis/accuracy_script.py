import argparse
from influxdb_client import InfluxDBClient, Point, WritePrecision
import numpy as np
import csv
import os
from analysis_secrets import influxdb_api_token

def get_sensor_sleep_data(client, bucket, org):
    """Retrieve total sleep time data from InfluxDB."""
    query_api = client.query_api()

    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -1d)
        |> filter(fn: (r) => r._measurement == "sensor_data" && r._field == "bed_state")
        |> mean()
    '''

    try:
        result = query_api.query(org=org, query=query)
        # Collect sensor data values
        sensor_sleep_data = [record.get_value() for table in result for record in table.records]

        if not sensor_sleep_data:
            print("No sleep data available from the sensor.")
            return None
        return np.mean(sensor_sleep_data)

    except Exception as e:
        print(f"Error in querying or processing data from InfluxDB: {e}")
        return None

def save_accuracy_to_csv(ground_truth, sensor_avg_sleep, accuracy):
    """Save the calculated accuracy to a CSV file."""


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Calculate the accuracy of the sleep sensor data.")
    parser.add_argument('ground_truth', type=float, help="Ground truth sleep time in hours, e.g., 8.0")
    args = parser.parse_args()

    # InfluxDB connection details
    url = 'http://localhost:8086'
    org = 'iot-org'
    bucket = 'iot-bucket'

    # Create InfluxDB client
    client = InfluxDBClient(url=url, token=influxdb_api_token, org=org)

    # Get sensor sleep data
    sensor_avg_sleep = get_sensor_sleep_data(client, bucket, org)

    if sensor_avg_sleep is not None:
        # Calculate accuracy
        accuracy = 100 - (np.abs(sensor_avg_sleep - args.ground_truth) / args.ground_truth * 100)
        print(f"Average Sensor Sleep Duration: {sensor_avg_sleep:.2f} hours")
        print(f"Accuracy of the sensor compared to ground truth: {accuracy:.2f}%")

        # Save accuracy data to CSV
        file_exists = os.path.exists('sensor_accuracy.csv')

        with open('sensor_accuracy.csv', 'a' if file_exists else 'w', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Sensor Name', 'Ground Truth (hours)', 'Measured Average (hours)', 'Accuracy (%)'])
            writer.writerow(['Sleep Sensor', ground_truth, sensor_avg_sleep, accuracy])

    # Close InfluxDB client
    client.close()

if __name__ == '__main__':
    main()
