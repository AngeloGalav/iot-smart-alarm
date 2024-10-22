from dfplayermini import Player

from time import sleep

music = Player(pin_TX=17, pin_RX=16)

music.volume(20)
music.play(track_id=1)
