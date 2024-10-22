from dfplayermini import Player

from time import sleep

music = Player(pin_TX=32, pin_RX=26)

music.volume(50)
music.play(1)
sleep(10)

music.module_sleep()