from dfplayermini import Player
from machine import Pin
from time import sleep

button = Pin(18, Pin.IN, Pin.PULL_DOWN) 
led = Pin(2, Pin.OUT)

music = Player(pin_TX=17, pin_RX=16)

music.volume(20)
music.play(track_id=1)

isPlaying1=False
isPlaying2=False

while True:
    if button.value():
        isPlaying2=False
        print("No reaction")
        led.value(0)
        sleep(0.1) # wait 1/10th of a second)
        if not isPlaying1:
            isPlaying1 = True
            music.play(track_id=1)
    else:
        isPlaying1=False
        print("Button pressed")
        led.value(1)
        sleep(0.1)
        if not isPlaying2:
            isPlaying2 = True
            music.play(track_id=2)