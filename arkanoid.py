from RPi import GPIO

import time
import random

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import threading

from luma.core.interface.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.oled.device import ssd1306

clk = 18
dt = 17
sw = 22
buzzer = 27

row1 = 16
column1 = 5

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

spi_matrix = spi(port=0, device=0, gpio=noop())
matrix = max7219(spi_matrix)

i2c_oled = i2c(port=1, address=0x3C)
oled = ssd1306(i2c_oled)

# 128x64 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
# y 0-15 yellow

# Initialize library.
# disp.begin()

# Clear display.
# disp.clear()
# disp.display()

# width = disp.width
# height = disp.height
# image = Image.new('1', (width, height))

width = 128
height = 64

# Get drawing object to draw on image.
# draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
# draw.rectangle((0,0,width,height), outline=0, fill=0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(row1, GPIO.OUT)
GPIO.setup(column1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buzzer, GPIO.OUT)

b = GPIO.PWM(buzzer, 100)

#########################TESTS#############################
################top right collision (x2, y1)###############
# bricks = [{"x1": 30, "y1": 24, "x2": 36, "y2": 50}]

# ballx = 40 #-
# bally = 20 #+

# balldirectionX = -1 # 1 - right, -1 - left
# balldirectionY = 1 # 1 - down, -1 - up

##############top left collision (x1, y1)##################
# bricks = [{"x1": 44, "y1": 24, "x2": 50, "y2": 30}]

# ballx = 40 #+
# bally = 20 #+

# balldirectionX = 1 # 1 - right, -1 - left
# balldirectionY = 1 # 1 - down, -1 - up

#############bottom right (x2, y2) collision###############
# bricks = [{"x1": 32, "y1": 12, "x2": 36, "y2": 16}]

# ballx = 40 #-
# bally = 20 #-

# balldirectionX = -1 # 1 - right, -1 - left
# balldirectionY = -1 # 1 - down, -1 - up

###############bottom left (x1, y2) collision##############
# bricks = [{"x1": 44, "y1": 12, "x2": 48, "y2": 16}]

# ballx = 40 #+
# bally = 20 #-

# balldirectionX = 1 # 1 - right, -1 - left
# balldirectionY = -1 # 1 - down, -1 - up
############################################################

bricks = []

bricks = [
    {"x1": 0, "y1": 0, "x2": 15, "y2": 3},
    {"x1": 17, "y1": 0, "x2": 32, "y2": 3},
    {"x1": 34, "y1": 0, "x2": 49, "y2": 3},
    {"x1": 51, "y1": 0, "x2": 66, "y2": 3},
    {"x1": 68, "y1": 0, "x2": 83, "y2": 3},
    {"x1": 85, "y1": 0, "x2": 100, "y2": 3},
    {"x1": 102, "y1": 0, "x2": 117, "y2": 3}
]

# bricks = [
#     {"x1": 0, "y1": 8, "x2": 17, "y2": 15},
# ]

paddleWidth = 20
paddleHeight = 3
sensitivity = 3
solidPaddle = 1
lives = 3


ballmoving = 0
paddlePos = int((width - 1 - paddleWidth) / 2)
ballx = int(paddlePos + paddleWidth/2)
bally = height - 2 - paddleHeight
balldirectionX = random.choice([1, -1])
balldirectionY = -1
buzz = 0

clkState = GPIO.input(clk)
dtState = GPIO.input(dt)
clkLastState = GPIO.input(clk)

def balllogic():
    threading.Timer(0.05, balllogic).start()
    global ballx
    global bally
    global balldirectionX
    global balldirectionY
    global ballmoving
    global lives
    global buzz
    collision = ""
    if ballmoving == 1:
        ballx += balldirectionX
        bally += balldirectionY
    
    if buzz:
        buzz = 0
        b.stop()

    # walls collision
    # right
    if ballx >= 127:
        balldirectionX = -1
        buzz = 1
    # left
    if ballx <= 0:
        balldirectionX = 1
        buzz = 1
    # top
    if bally <= 0:
        balldirectionY = 1
        buzz = 1

    # paddle collision
    if bally >= height-paddleHeight-1:
        if ballx >= paddlePos and ballx <= paddlePos+paddleWidth:
            balldirectionY = -1
            buzz = 1
    
    # missed ball
    # bottom
    if bally >= 63:
        ballmoving = 0
        balldirectionX = random.choice([1, -1]) # 1 - right, -1 - left
        balldirectionY = -1 # 1 - down, -1 - up
        lives -= 1
        with canvas(matrix) as draw:
            draw.text((1, -2), str(lives), fill="white")

    # bricks collision
    for brick in bricks[:]:
        # left wall
        if ballx == brick["x1"]-1 and bally >= brick["y1"]-1 and bally <= brick["y2"]+1 and balldirectionX == 1:
            balldirectionX = -1
            collision += "left "
        # right wall
        elif ballx == brick["x2"]+1 and bally >= brick["y1"]-1 and bally <= brick["y2"]+1 and balldirectionX == -1:
            balldirectionX = 1
            collision += "right "
        # top wall
        if bally == brick["y1"]-1 and ballx >= brick["x1"]-1 and ballx <= brick["x2"]+1 and balldirectionY == 1:
            balldirectionY = -1
            collision += "top "
        # bottom wall
        elif bally == brick["y2"]+1 and ballx >= brick["x1"]-1 and ballx <= brick["x2"]+1 and balldirectionY == -1:
            balldirectionY = 1
            collision += "bottom "
        if collision != "":
            bricks.remove(brick)
            buzz = 1
            # print(f"\n{collision} x1:{brick['x1']} x2:{brick['x2']} y1:{brick['y1']} y2:{brick['y2']}\n")
            collision = ""
    
    if buzz: b.start(1)
    # print(f"ballx:{ballx} bally:{bally}")


def redraw():
    # while True:
    #     draw.rectangle((0, 0, width, height), outline = 0, fill = 0)
    #     draw.rectangle((paddlePos, height-paddleHeight, paddlePos+paddleWidth, height), outline=255, fill=solidPaddle)
    #     draw.rectangle((ballx, bally, ballx, bally), outline=255, fill=1)

    #     for brick in bricks:
    #         draw.rectangle((brick["x1"], brick["y1"], brick["x2"], brick["y2"]), outline=255, fill=1)

    #     disp.image(image)
    #     disp.display()

    global lives
    while True:
        with canvas(oled) as draw:
            if lives == 0:
                print("GAME OVER\n")
                draw.text((35, 28), "GAME OVER", fill="white")
                break
            draw.rectangle((paddlePos, height-paddleHeight, paddlePos+paddleWidth, height), outline=255, fill=solidPaddle)
            draw.rectangle((ballx, bally, ballx, bally), outline=255, fill=1)

            for brick in bricks:
                draw.rectangle((brick["x1"], brick["y1"], brick["x2"], brick["y2"]), outline=255, fill=1)


thread = threading.Thread(target = redraw)
thread.start()

balllogic()

print("Управление ракеткой энкодером, левая верхняя кнопка (KEY1) - запустить шарик")

GPIO.output(row1, GPIO.LOW)
matrix.contrast(1)
with canvas(matrix) as draw:
    draw.text((1, -2), str(lives), fill="white")
while True:
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    col1state = GPIO.input(column1)
    # print(f"debug: clk:{clkState} dt:{dtState} sw:{col1state} paddle:{paddlePos} ballmoving:{ballmoving} ballx:{ballx} bally:{bally}", end="              \r")

    if col1state == 0 and ballmoving == 0: ballmoving = 1

    if clkLastState == 1 and clkState == 0:
        if dtState == 1: paddlePos -= sensitivity
        else: paddlePos += sensitivity
        if paddlePos > width - 1 - paddleWidth: paddlePos = width - 1 - paddleWidth
        paddlePos = 0 if paddlePos < 0 else paddlePos
        
    if ballmoving == 0:
        ballx = int(paddlePos + paddleWidth/2)
        bally = height - 2 - paddleHeight

    clkLastState = clkState