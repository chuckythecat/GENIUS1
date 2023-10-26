from RPi import GPIO

import time
import random
from pprint import pprint

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219

import threading

buzzerpin = 27
rows = [16, 19, 20, 21]
columns = [5, 6, 12, 13]

GPIO.setmode(GPIO.BCM)

for row in rows:
    GPIO.setup(row, GPIO.OUT)

for column in columns:
    GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(buzzerpin, GPIO.OUT)

b = GPIO.PWM(buzzerpin, 100)


buttons = []

for rownumber, row in enumerate(rows):
    for columnnumber, column in enumerate(columns):
        buttons.append({"buttonnumber": columnnumber+1+((rownumber)*4), "ledrow": columnnumber * 2, "ledcol": rownumber * 2})

# pprint(buttons)

spi_matrix = spi(port=0, device=0, gpio=noop())
matrix = max7219(spi_matrix)

# test all buttons
# for button in buttons:
#     with canvas(matrix) as draw:
#         draw.rectangle((button["ledrow"], button["ledcol"], button["ledrow"]+1, button["ledcol"]+1), outline=255, fill=1)
#     time.sleep(1)
# time.sleep(1)

def stopbuzzing():
    b.stop()
    buzz = False

sequence = []
sequencecurrent = 0
pressbuttons = 0
pressed = -1

buzz = False

# sequence.append({'buttonnumber': 13, 'ledcol': 6, 'ledrow': 0})
# sequence.append({'buttonnumber': 13, 'ledcol': 6, 'ledrow': 0})

while True:
    if pressbuttons == 0:
        sequence.append(random.choice(buttons))
        pprint(sequence)

        for button in sequence:
            b.stop()
            time.sleep(0.1)
            with canvas(matrix) as draw:
                draw.rectangle((button["ledrow"], button["ledcol"], button["ledrow"]+1, button["ledcol"]+1), outline=255, fill=1)
            b.start(1)
            freq = 100 + button["buttonnumber"] * 100
            b.ChangeFrequency(freq)
            time.sleep(0.4)

        b.stop()
        matrix.clear()
        pressed = -1
        pressbuttons = 1
    
    else:
        for rownumber, row in enumerate(rows):
            GPIO.output(row, GPIO.LOW)
            for columnnumber, column in enumerate(columns):
                if GPIO.input(column) == 0:
                    pressed = columnnumber+1+((rownumber)*4)
            GPIO.output(row, GPIO.HIGH)
        
        if pressed != -1:
            print(f"pressed: {pressed} should press: {sequence[sequencecurrent]['buttonnumber']}")
            if pressed == sequence[sequencecurrent]["buttonnumber"]:
                pressed = -1
                b.start(1)
                freq = 100 + sequence[sequencecurrent]["buttonnumber"] * 100
                b.ChangeFrequency(freq)
                with canvas(matrix) as draw:
                    draw.rectangle((sequence[sequencecurrent]["ledrow"], sequence[sequencecurrent]["ledcol"], sequence[sequencecurrent]["ledrow"]+1, sequence[sequencecurrent]["ledcol"]+1), outline=255, fill=1)
                time.sleep(0.5)
                b.stop()
                matrix.clear()
                # if buzz: buzz.cancel()
                # buzz = threading.Timer(0.3, stopbuzzing)
                # buzz.start()
                sequencecurrent += 1
                print(f"sq:{sequencecurrent} sl:{len(sequence)}")
                if sequencecurrent == len(sequence):
                    print("sq=0")
                    sequencecurrent = 0
                    pressbuttons = 0
                    pressed = -1
                    continue
            else:
                with canvas(matrix) as draw:
                    draw.line((0, 0, 7, 7), fill=1)
                    draw.line((7, 0, 0, 7), fill=1)
                for i in range(0, 3):
                    time.sleep(0.1)
                    b.start(1)
                    freq = 100
                    b.ChangeFrequency(freq)
                    time.sleep(0.4)
                    b.stop()
                matrix.clear()
                time.sleep(2)

                sequencecurrent = 0
                pressbuttons = 0
                pressed = -1
                sequence = []
                continue