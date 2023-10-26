import RPi.GPIO as GPIO
import time

clk = 18
dt = 17
GPIO_PWM_1 = 27
WORK_TIME = 10

GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_PWM_1, GPIO.OUT)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

clkLastState = GPIO.input(clk)

p = GPIO.PWM(GPIO_PWM_1, 100)

p.start(1)

for a in range(0, 15):
    freq = 100 + a * 100
    p.ChangeFrequency(freq)
    print(freq)
    time.sleep(0.5)

p.stop()

GPIO.cleanup()