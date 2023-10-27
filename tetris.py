from RPi import GPIO
from time import sleep

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from time import sleep
from pprint import pprint
import random
import threading

rows = [16, 19, 20, 21]
column = 13

GPIO.setmode(GPIO.BCM)

def buttonHandler(pressed):
    global currX
    global currY
    global blockWidth
    global currentShape
    if pressed == 21: currX -= 1
    elif pressed == 19: currX += 1
    elif pressed == 20: currY += 1
    elif pressed == 22: currentShape = rotateShape(currentShape)
    elif pressed == 16: currY -= 1
    blockWidth = len(currentShape[0])
    if currX > 8 - blockWidth: currX = 8 - blockWidth
    currX = 0 if currX < 0 else currX

for row in rows:
    GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(row, GPIO.FALLING, buttonHandler, 200)

GPIO.setup(column, GPIO.OUT)

GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.FALLING, buttonHandler, 200)

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=3)

tetris = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 0],
]

shapes = {
    "I": [
        [1, 1, 1, 1]
    ],
    "J": [
        [1, 0, 0],
        [1, 1, 1]
    ],
    "L": [
        [0, 0, 1],
        [1, 1, 1]
    ],
    "O": [
        [1, 1],
        [1, 1]
    ],
    "S": [
        [0, 1, 1],
        [1, 1, 0],
    ],
    "T": [
        [0, 1, 0],
        [1, 1, 1]
    ],
    "Z": [
        [1, 1, 0],
        [0, 1, 1]
    ]
}

# shapes = {
#     "skew": [
#         {"x":0, "y":0},
#         {"x":0, "y":1},
#         {"x":1, "y":1},
#         {"x":1, "y":2},
#     ],
# }

# swap x and y coordinates
# {"x":0, "y":0},
# {"x":1, "y":0},
# {"x":1, "y":1},
# {"x":2, "y":1},

# rotate 90 degrees clockwise - reverse x order

# x2 = | x1 - x max|
# x = 0, x max = 2 -> x = | 0 - 2 | = | -2 | = 2

# {"x":2, "y":0},
# {"x":1, "y":0},
# {"x":1, "y":1},
# {"x":0, "y":1},

# rotate 90 degrees counterclockwise - reverse y order
# y2 = | y1 - y max|
# y = 0, y max = 1 -> y = | 0 - 1 | = | -1 | = 1

# {"x":0, "y":1},
# {"x":1, "y":1},
# {"x":1, "y":0},
# {"x":2, "y":0},

# def rotateShape(shape, clockwise = True):
#     transposedShape = []
#     rotatedShape = []
#     reverseOrder = "x" if clockwise else "y"
#     for block in shape:
#         transposedShape.append({"x": block["y"], "y": block["x"]})

#     for block in transposedShape:
#         rotatedShape.append()

#     return rotatedShape

def rotateShape(shape, clockwise = True):
    rotatedShape = []
    for index, isBlock in enumerate(shape[0]):
        row = []
        for b in shape:
            row.append(b[index])
        rotatedShape.append(row)

    if clockwise:
        for row in rotatedShape:
            row.reverse()
    else:
        rotatedShape.reverse()

    return rotatedShape

def draw_block(x, y):
    with canvas(device) as draw:
        draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline="white", fill="black")

currentShape = shapes[random.choice(list(shapes.keys()))]

currX = 0
currY = 0

def logic():
    global currY
    threading.Timer(0.3, logic).start()
    # currY += 1
    with canvas(device) as draw:
        for y, row in enumerate(tetris):
            for x, block in enumerate(row):
                if block: draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline="white", fill="black")

        for blockY, row in enumerate(currentShape):
            for blockX, isBlock in enumerate(row):
                if isBlock:
                    x = currX + blockX
                    y = currY + blockY
                    draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline="white", fill="black")
            
        for blockY in range(len(currentShape) - 1, -1, -1):
            for blockX, isBlock in enumerate(currentShape[blockY]):
                if isBlock and tetris[currY + blockY + 1][currX + blockX]:
                    draw.rectangle(((currX + blockX)*8, (currY + blockY + 1)*8, (currX + blockX)*8+7, (currY + blockY + 1)*8+7), outline="white", fill="white")

logic()

waitForRelease = []
pressed = False

GPIO.output(column, GPIO.LOW)

while True:
    pass
    # pressed = False
    # for rownumber, row in enumerate(rows):
    #     GPIO.output(row, GPIO.LOW)
    #     for columnnumber, column in enumerate(columns):
    #         buttonNumber = columnnumber + 1 + ((rownumber) * 4)
    #         if GPIO.input(column) == 0 and buttonNumber not in waitForRelease: pressed = buttonNumber
    #         elif GPIO.input(column) == 1 and buttonNumber in waitForRelease: waitForRelease.remove(buttonNumber)
    #     GPIO.output(row, GPIO.HIGH)

    # pressed = False
    # GPIO.output(column, GPIO.LOW)
    # for columnnumber, column in enumerate(columns):
    #     buttonNumber = columnnumber + 1 + ((rownumber) * 4)
    #     if GPIO.input(column) == 0 and buttonNumber not in waitForRelease: pressed = buttonNumber
    #     elif GPIO.input(column) == 1 and buttonNumber in waitForRelease: waitForRelease.remove(buttonNumber)

    # if pressed:
    #     if pressed == 16: currX -= 1
    #     elif pressed == 8: currX += 1
    #     elif pressed == 12: currY += 1
    #     blockWidth = 0
    #     for block in currentShape: blockWidth = max(blockWidth, block["y"])
    #     if currX > 8 - blockWidth: currX = 8 - blockWidth
    #     currX = 0 if currX < 0 else currX
    #     waitForRelease.append(pressed)
        # print(f"x: {currX} bw:{blockWidth}", end="\r")
