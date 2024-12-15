'''
Quick script to get the training data from INFLUXDB into a csv.
'''
import os
from influxdb_client import InfluxDBClient
import pandas as pd
from analysis_secrets import influxdb_api_token

# InfluxDB configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = influxdb_api_token
INFLUXDB_ORG = "iot-org"
INFLUXDB_BUCKET = "iot-bucket"

def query_influxdb_and_save_for_prophet(output_csv="bed_state_data_prophet.csv"):
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()

    # get the influxdb state of the last 30 days
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -24h)
      |> filter(fn: (r) => r._measurement == "sensor_data")
      |> filter(fn: (r) => r._field == "bed_state")
    '''
    result = query_api.query(query, org=INFLUXDB_ORG)

    records = []
    for table in result:
        for record in table.records:
            records.append((record.get_time(), record.get_value()))

    df = pd.DataFrame(records, columns=["timestamp", "bed_state"])

    # ensure timestamp is a datetime object and rename columns for Prophet
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.rename(columns={"timestamp": "ds", "bed_state": "y"})
    df = df[["ds", "y"]]

    # check if the file exists
    file_exists = os.path.isfile(output_csv)

    # if the file exists, append data to it, otherwise create a new one (and write the headers)
    mode = 'a' if file_exists else 'w'
    header = not file_exists
    df.to_csv(output_csv, index=False, mode=mode, header=header)

    print(f"Data {'appended to' if file_exists else 'saved to'} {output_csv}")

if __name__ == "__main__":
    query_influxdb_and_save_for_prophet("bed_state_data.csv")
