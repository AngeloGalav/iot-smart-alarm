# alarm-thingy

<p align="center">
  <img src="res//image.png" alt="Robot Alarm" width="400px"/>
</p>

> "_AAAAAH!_" - this alarm if you won't get up

alarm-thingy is an ESP32-based Smart Alarm that tracks your sleep, and gets angry if you don't get up. Based on a pressure sensor, it can recognize if the user gets out of bed or is taking a snooze, and the alarm will stop if the user stops being lazy and starts their day.
Here are some of the features of this project:
- Beautiful Web App to interact easily with the alarm! Not feeling using the Web App? Check out the Telegram Bot.
- Based on your location and its weather condition, the alarm will play a different, soothing sound.
- Add as many alarms as you want, and decide their weekly pattern. Changed your mind? You can update the alarm on the fly, as soon as you change the values.
- AI-based user detection: through Prophet, you can check the likely-hood of the user being in bed at a certain time.
- View the current state of the sensor in real-time in the Web App through via a Grafana dashboard.
- Laziness-mitigation technology: if you won't be by 30 seconds since the start of the alarm, a high-volume metal soundtrack will play.
- Switch to HTTP or MQTT on the fly for sending sensor data. You can also take a look at the current delay average on the Web App.
- Lots of statistics in the Web App: View the total sleep time in the last 24h, view the current weather in your location, and more!
- No need to setup IPs: the Broker and server will find the alarm by themselves through mDNS.
- Having connection problems? The alarm will reconnect to the server as soon as the connection is available again.
- Easy feedback for the status of the ESP32: depending on its network status, the alarm will play a sound and blink the LED whenever it's successfully sending data to the server.
- And much, much more...

## Setup instructions

> [!WARNING]
> Remember to add your user to the `uucp` or `dialout` group!! (Arch or Debian respectively).


> [!WARNING]
> You may need to change the permission of Grafana's data folder for it to work properly.
> To do that, simply run the command:
> `chown -R $USER grafana/data  && chmod -R 777 grafana/data`

## Circuit schematics
Here are the schematics on how to setup the speaker and DFPlayer Mini module with to interface with the ESP32.
<p align="center">
  <img src="res//schematics.png" alt="Schematics" width="400px"/>
</p>
In addition, you need add a LED on pin 23 and the pressure mat on pin 18. However, those can be customized based on the user's preferences.

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
python sleep_accuracy.py [hours slept]
```
E.g. `python sleep_accuracy.py 8.0`


## Tasks
- IMPORTANT!!!
 - [ ] report

- [ ] Readme
  - [ ] make proper readme file

- [x] Telegram Bot
  - [x] Do bot

- TESTS:
  - [ ] test alarm logic (two alarms close to each other)


### Resources
dfplayermini library here: https://github.com/lavron/micropython-dfplayermini