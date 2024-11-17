# iot-smart-alarm

<p align="center">
  <img src="res//image.png" alt="Robot Alarm" width="400px"/>
</p>

## Installation instructions

> [!WARNING]
> Remember to add your user to the `uucp` or `dialout` group!! (Arch or Debian respectively).

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

- [ ] Data proxy
  - [ ] write server code, which receives data from the esp32 and sends it to influxdb
  - [ ] integrate it with the webapp
  - [x] weather api integration

- [ ] influxdb
  - [ ] setup influxdb instance to collect data

- [ ] grafana
  - [ ] develop a dashboard

- [ ] evaluation metrics

- [ ] Frontend
  - [x] Fix footer and make it design coherent with the design of the app (and smaller)
  - [x] Fix logo and about button (navbar) to make it design compatible with the rest of the frontend
    - [x] move button to top left
  - [ ] Add dashboard
  - [x] alarm periodicity (based on day of the week)

- [ ] Telegram Bot
  - [ ] Do bot

- [ ] Docker compose
  - [ ] all of this sounds like a job for a Docker compose.
  - [ ] You know what to do.