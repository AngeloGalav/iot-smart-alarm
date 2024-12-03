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
To enable mDNS on the ESP32 alarm, you'll need to instal the import `micropython-mdns` package through `mip`.
To do so, you'll first need to connect the ESP32 to the network. Then, open the `micropython` console on the ESP32 and install the package with these commands:
```
>>> import mip
>>> mip.install("github:cbrand/micropython-mdns")
``` 

## Tasks
- IMPORTANT!!!
 - [ ] moving average/find alarm go substitute
 - [ ] sampling rate in another thread?
 - [ ] TEST GRAFANA!!!!!!!!!

- [ ] ESP32 alarm
  - [x] complete hardware
  - [x] write code that sends data to data proxy via CoAP or HTTP, while supporting MQTT. The MQTT commands are:
    - [x] sampling_rate: interval between sensor readings
    - [x] trigger_alarm (triggers alarm until user gets up)
    - [x] stop_alarm
  - [x] write alarm code
  - [ ] write AI alarm prediction code?
  - [ ] implement angry mode
  - [ ] add repeat sound
  - [x] add second sound for mqtt connection

- [ ] data analysis
  - based on the sensor data collected, can determine the number of hours the user slept each day

- [ ] Data proxy
  - [x] write server code, which receives data from the esp32 and sends it to influxdb
  - [x] integrate it with the webapp
  - [x] weather api integration
  - [x] add alarm code
  - [ ] test start/stop alarm

- [ ] influxdb
  - [x] setup influxdb instance to collect data

- [ ] grafana
  - [ ] develop a dashboard

- [ ] evaluation metrics
  1. Mean Latency of the data acquisition process (network latency to send data to the proxy).
  2. Accuracy to detect if a person is in bed or not

- [ ] Frontend
  - [x] Fix footer and make it design coherent with the design of the app (and smaller)
  - [x] Fix logo and about button (navbar) to make it design compatible with the rest of the frontend
    - [x] move button to top left
  - [x] alarm periodicity (based on day of the week)
  - [x] add options menu for some useful commands? (i.e. stop all commands, enable angry mode...)
  - [x] make options menu

- [ ] Readme
  - [ ] make proper readme file

- [x] Telegram Bot
  - [x] Do bot

### Resources
dfplayermini library here: https://github.com/lavron/micropython-dfplayermini