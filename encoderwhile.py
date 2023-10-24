from RPi import GPIO
from time import sleep

clk = 18
dt = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

counter = 0

clkLastState = GPIO.input(clk)

while True:
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    print(f"{clkState} {dtState} {counter}", end="              \r")

    if clkLastState == 1 and clkState == 0:
        if dtState == 1: counter -= 1
        else: counter += 1

    clkLastState = clkState