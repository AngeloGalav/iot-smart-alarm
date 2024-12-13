# alarm-thingy

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
- Secrets

## Accuracy script
To run the accuracy script, make sure that the InfluxDB instance is up and running. Then, simply use the script in this way:
```
python accuracy_script.py [hours slept]
```
E.g. `python accuracy_script.py 8.0`


## Tasks
- IMPORTANT!!!
 - [x] running average on mqtt
 - [ ] sleep time, accuracy etc..
 - [ ] report
 - [ ] finish tests
 - [ ] fix sleep time

- [ ] data analysis
  - based on the sensor data collected, can determine the number of hours the user slept each day
- [ ] evaluation metrics
  1. Mean Latency of the data acquisition process (network latency to send data to the proxy).
  2. Accuracy to detect if a person is in bed or not

- [ ] Readme
  - [ ] make proper readme file

- [x] Telegram Bot
  - [x] Do bot

- TESTS:
  - [ ] test alarm logic (two alarms close to each other)
  - [x] test http response time
  - [ ] test volume slider
  - [ ] test analysis script/SLEEP TIME
  - [ ] retest esp32 functions (INCLUDING SWITCHING TO HTTP/MQTT)


### Resources
dfplayermini library here: https://github.com/lavron/micropython-dfplayermini