# iot-smart-alarm

<p align="center">
  <img src="res//image.png" alt="Robot Alarm" width="400px"/>
</p>

## Setup instructions

> [!WARNING]
> Remember to add your user to the `uucp` or `dialout` group!! (Arch or Debian respectively).


> [!WARNING]
> You may need to change the permission of Grafana's data folder for it to work properly.
> To do that, simply run the command:
> `chown -R $USER grafana/data  && chmod -R 777 grafana/data`

## How to start
You can simply use the `docker-compose` file provided in the repository, and start the infrastructure with the following command:
```
docker-compose up --build
```

## Setup
- InfluxDB
- Grafana

## Tasks
- IMPORTANT!!!
 - [x] moving average/find alarm go substitute
 - [ ] TEST GRAFANA!!!!!!!!!
 - [ ] fix new sampling rate handling

- [ ] ESP32 alarm
  - [x] complete hardware
  - [x] write code that sends data to data proxy via CoAP or HTTP, while supporting MQTT. The MQTT commands are:
    - [x] sampling_rate: interval between sensor readings
    - [x] trigger_alarm (triggers alarm until user gets up)
    - [x] stop_alarm
  - [x] write alarm code
  - [x] write AI alarm prediction code?
  - [x] implement angry mode
  - [x] add repeat sound
  - [x] add second sound for mqtt connection

- [ ] data analysis
  - based on the sensor data collected, can determine the number of hours the user slept each day
- [ ] evaluation metrics
  1. Mean Latency of the data acquisition process (network latency to send data to the proxy).
  2. Accuracy to detect if a person is in bed or not

- [ ] Data proxy
  - [x] write server code, which receives data from the esp32 and sends it to influxdb
  - [x] integrate it with the webapp
  - [x] weather api integration
  - [x] add alarm code
  - [x] test start/stop alarm

- [x] influxdb
  - [x] setup influxdb instance to collect data

- [ ] grafana
  - [ ] develop a dashboard


- [ ] Frontend
  - [ ] volume slider

- [ ] Readme
  - [ ] make proper readme file

- [x] Telegram Bot
  - [x] Do bot


- TESTS:
  - [ ] test alarm logic (two alarms close to each other)
  - [x] test weather time
  - [ ] test grafana
  - [x] test stop alarm
  - [x] test angry mode
  - [ ] test http response time

- File transf
  - [x] add ringtones for differnet weathers
  - [x] increase ringtones length

### Resources
dfplayermini library here: https://github.com/lavron/micropython-dfplayermini