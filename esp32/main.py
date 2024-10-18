import time
import machine
pwm = machine.PWM(machine.Pin(2))
pwm.freq(120)
while True:
    for i in range(1024):
        pwm.duty(i)
        time.sleep(0.001)
    for i in range(1023, -1, -1):
        pwm.duty(i)
        time.sleep(0.001)