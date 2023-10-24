from RPi import GPIO

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

clk = 18
dt = 17

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

paddleWidth = 20
paddleHeight = 3
paddlePos = int((width - 1 - paddleWidth) / 2)
sensitivity = 5
solidPaddle = 1

clkLastState = GPIO.input(clk)

while True:
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    print(f"{clkState} {dtState} {paddlePos}", end="              \r")

    if clkLastState == 1 and clkState == 0:
        if dtState == 1: paddlePos -= sensitivity
        else: paddlePos += sensitivity
        if paddlePos > width - 1 - paddleWidth: paddlePos = width - 1 - paddleWidth
        paddlePos = 0 if paddlePos < 0 else paddlePos
        
        draw.rectangle((0, height-1-paddleHeight, width - 1, height-1), outline=0, fill=0)
        draw.rectangle((paddlePos, height-1-paddleHeight, paddlePos+paddleWidth, height-1), outline=255, fill=solidPaddle)

        disp.image(image)
        disp.display()

    clkLastState = clkState