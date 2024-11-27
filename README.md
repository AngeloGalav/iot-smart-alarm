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

## Tasks

- [ ] ESP32 alarm
  - [x] complete hardware
  - [ ] write code that sends data to data proxy via CoAP or HTTP, while supporting MQTT. The MQTT commands are:
    - [ ] sampling_rate: interval between sensor readings
    - [ ] trigger_alarm (triggers alarm until user gets up)
    - [ ] stop_alarm
  - [ ] write alarm code
  - [ ] write AI alarm prediction code
  - [ ] implement angry mode
  - [ ] add repeat sound
  - [ ] add second sound for mqtt connection

- [ ] data analysis
  - based on the sensor data collected, can determine the number of hours the user slept each day

- [ ] Data proxy
  - [x] write server code, which receives data from the esp32 and sends it to influxdb
  - [ ] integrate it with the webapp
  - [x] weather api integration

- [ ] influxdb
  - [x] setup influxdb instance to collect data

- [ ] grafana
  - [ ] develop a dashboard

- [ ] evaluation metrics

- [ ] Frontend
  - [x] Fix footer and make it design coherent with the design of the app (and smaller)
  - [x] Fix logo and about button (navbar) to make it design compatible with the rest of the frontend
    - [x] move button to top left
  - [x] alarm periodicity (based on day of the week)
  - [ ] add toast notifications?
  - [ ] add options menu for some useful commands? (i.e. stop all commands, enable angry mode...)
  - [ ] add ability to change the ip within the app

- [ ] Telegram Bot
  - [ ] Do bot

### Resources
dfplayermini library here: https://github.com/lavron/micropython-dfplayermini