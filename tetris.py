from RPi import GPIO
from time import sleep

from luma.core.interface.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.oled.device import ssd1306
from time import sleep
from pprint import pprint
import random
import threading

rows = [16, 19, 20, 21]
column = 13

buzzerpin = 27
R = 0
C0= 16.35
CS0=17.32
D0= 18.35
DS0=19.45
E0= 20.60
F0= 21.83
FS0=23.12
G0= 24.50
GS0=25.96
A0= 27.50
AS0=29.14
B0= 30.87
C1= 32.70
CS1=34.65
D1= 36.71
DS1=38.89
E1= 41.20
F1= 43.65
FS1=46.25
G1= 49.00
GS1=51.91
A1= 55.00
AS1=58.27
B1= 61.74
C2= 65.41
CS2=69.30
D2= 73.42
DS2=77.78
E2= 82.41
F2= 87.31
FS2=92.50
G2= 98.00
GS2=103.83
A2= 110.00
AS2=116.54
B2= 123.47
C3= 130.81
CS3=138.59
D3= 146.83
DS3=155.56
E3= 164.81
F3= 174.61
FS3=185.00
G3= 196.00
GS3=207.65
A3= 220.00
AS3=233.08
B3= 246.94
C4= 261.63
CS4=277.18
D4= 293.66
DS4=311.13
E4= 329.63
F4= 349.23
FS4=369.99
G4= 392.00
GS4=415.30
A4= 440.00
AS4=466.16
B4= 493.88
C5= 523.25
CS5=554.37
D5= 587.33
DS5=622.25
E5= 659.25
F5= 698.46
FS5=739.99
G5= 783.99
GS5=830.61
A5= 880.00
AS5=932.33
B5= 987.77
C6= 1046.50
CS6=1108.73
D6= 1174.66
DS6=1244.51
E6= 1318.51
F6= 1396.91
FS6=1479.98
G6= 1567.98
GS6=1661.22
A6= 1760.00
AS6=1864.66
B6= 1975.53
C7= 2093.00
CS7=2217.46
D7= 2349.32
DS7=2489.02
E7= 2637.02
F7= 2793.83
FS7=2959.96
G7= 3135.96
GS7=3322.44
A7= 3520.00
AS7=3729.31
B7= 3951.07
C8= 4186.01
CS8=4434.92
D8= 4698.63
DS8=4978.03
E8= 5274.04
F8= 5587.65
FS8=5919.91
G8= 6271.93
GS8=6644.88
A8= 7040.00
AS8=7458.62
B8= 7902.13

BPM = 140

lead = [
    # part 1
    (E5, 1.0),
    (B4, 0.5),
    (C5, 0.5),
    (D5, 1.0),
    (C5, 0.5),
    (B4, 0.5),
    (A4, 1.0),
    (A4, 0.5),
    (C5, 0.5),
    (E5, 1.0),
    (D5, 0.5),
    (C5, 0.5),
    (B4, 1.0),
    (B4, 0.5),
    (C5, 0.5),
    (D5, 1.0),
    (E5, 1.0),
    (C5, 1.0),
    (A4, 1.0),
    (A4, 1.0),
    (R, 1.0),
    #
    (D5, 1.5),
    (F5, 0.5),
    (A5, 1.0),
    (G5, 0.5),
    (F5, 0.5),
    (E5, 1.5),
    (C5, 0.5),
    (E5, 1.0),
    (D5, 0.5),
    (C5, 0.5),
    (B4, 1.0),
    (B4, 0.5),
    (C5, 0.5),
    (D5, 1.0),
    (E5, 1.0),
    (C5, 1.0),
    (A4, 1.0),
    (A4, 1.0),
    (R, 1.0),
    # part 2
    (E4, 2.0),
    (C4, 2.0),
    (D4, 2.0),
    (B3, 2.0),
    (C4, 2.0),
    (A3, 2.0),
    (GS3, 2.0),
    (B3, 2.0),
    #
    (E4, 2.0),
    (C4, 2.0),
    (D4, 2.0),
    (B3, 2.0),
    (C4, 1.0),
    (E4, 1.0),
    (A4, 1.0),
    (A4, 1.0),
    (GS4, 3.0),
    (R, 1.0)
]

GPIO.setmode(GPIO.BCM)

def buttonHandler(pressed):
    global currX
    global currY
    global blockWidth
    global currentShape
    global tetris
    if pressed == 21 and not checkCollision(currentShape, tetris, currX, currY, side = 0): currX -= 1
    elif pressed == 19 and not checkCollision(currentShape, tetris, currX, currY, side = 2): currX += 1
    elif pressed == 20: currY += 1
    elif pressed == 22 and not checkCollision(rotateShape(currentShape), tetris, currX, currY, side = -1): currentShape = rotateShape(currentShape)
    elif pressed == 16: currY -= 1
    # blockWidth = len(currentShape[0])
    # if currX > 8 - blockWidth: currX = 8 - blockWidth
    # currX = 0 if currX < 0 else currX

for row in rows:
    GPIO.setup(row, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(row, GPIO.FALLING, buttonHandler, 200)

GPIO.setup(column, GPIO.OUT)
GPIO.setup(buzzerpin, GPIO.OUT)
b = GPIO.PWM(buzzerpin, 100)

GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.FALLING, buttonHandler, 200)

serial = i2c(port = 1, address = 0x3C)
device = ssd1306(serial, rotate = 3)

spi_matrix = spi(port = 0, device = 0, gpio = noop())
matrix = max7219(spi_matrix, rotate = 3)

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
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
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


currentState = {
    "x": 3,
    "y": 0,
    "shape": shapes[random.choice(list(shapes.keys()))],
    "nextShape": shapes[random.choice(list(shapes.keys()))]
    }

# currentShape = shapes[random.choice(list(shapes.keys()))]
currentShape = shapes["I"]
nextShape = shapes[random.choice(list(shapes.keys()))]

with canvas(matrix) as draw:
    for blockY, row in enumerate(nextShape):
        for blockX, isBlock in enumerate(row):
            if isBlock:
                draw.rectangle((blockX*2, blockY*2, blockX*2+1, blockY*2+1), fill = "white")

# currentPos = {"x": 0, "y": 0}

currX = 3
currY = 0

nextLogicCall = None

def checkCollision(shape, field, currentX, currentY, side = 1): # -1 - inside, 0 - left, 1 - bottom, 2 - right
    blockWidth = len(shape[0])
    fieldWidth = len(field[0])
    fieldHeight = len(field)

    if (currentY + len(shape) >= 16 and side == 1) \
    or (currentX - 1 < 0 and side == 0) \
    or (currentX + 1 > fieldWidth - blockWidth and side == 2): return True

    for blockY, row in enumerate(shape):
        for blockX, isBlock in enumerate(row):
            checkX = currentX + blockX
            checkY = currentY + blockY
            if side == -1 and (checkX > fieldWidth - 1 or checkY > fieldHeight - 1): return True
            elif side == 0:
                checkX = currentX - 1
                checkY = currentY + blockY
            elif side == 1:
                checkX = currentX + blockX
                checkY = currentY + blockY + 1
            elif side == 2:
                checkX = currentX + blockX + 1
                checkY = currentY + blockY

            # checkY = currentY + blockY + 1 if side == 1 else currentY + blockY
            # if side == 0: checkX = currentX - 1
            # elif side == 2: checkX = currentX + blockX + 1
            # else: checkX = currentX + blockX
            if isBlock and tetris[checkY][checkX]:
                return True
    return False

def logic():
    global currY
    global currX
    global currentShape
    global nextShape
    global nextLogicCall
    nextLogicCall = threading.Timer(0.3, logic)
    nextLogicCall.start()
    currY += 1

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline = "white", fill = "black")
        for y, line in enumerate(tetris):
            for x, block in enumerate(line):
                if block: draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline = "white", fill = "black")
        
        for y, line in enumerate(tetris):
            if min(line):
                for x in range(0, 8):
                    draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline = "white", fill = "white")
                del tetris[y]
                tetris.insert(0, [0, 0, 0, 0, 0, 0, 0, 0])

        # if currY + len(currentShape) == 15:
        #     breakflag = 1
        #     for changeBlockY, row in enumerate(currentShape):
        #         for changeBlockX, isBlock in enumerate(row):
        #             if isBlock: tetris[currY+changeBlockY][currX+changeBlockX] = 1

        for blockY, row in enumerate(currentShape):
            for blockX, isBlock in enumerate(row):
                if isBlock:
                    x = currX + blockX
                    y = currY + blockY
                    draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline = "white", fill = "black")

        # for blockY, row in enumerate(currentShape):
        #     if breakflag: break
        #     for blockX, isBlock in enumerate(row):
        #         if breakflag: break
        #         if isBlock and tetris[currY + blockY + 1][currX + blockX]:
        #             for changeBlockY, row in enumerate(currentShape):
        #                 for changeBlockX, isBlock in enumerate(row):
        #                     if isBlock: tetris[currY+changeBlockY][currX+changeBlockX] = 1
        #                     breakflag = 1

        if checkCollision(currentShape, tetris, currX, currY, side = 1):
            for changeBlockY, row in enumerate(currentShape):
                for changeBlockX, isBlock in enumerate(row):
                    if isBlock: tetris[currY+changeBlockY][currX+changeBlockX] = 1
            currX = 3
            currY = 0
            currentShape = nextShape
            nextShape = shapes[random.choice(list(shapes.keys()))]
            with canvas(matrix) as draw:
                for blockY, row in enumerate(nextShape):
                    for blockX, isBlock in enumerate(row):
                        if isBlock: draw.rectangle((blockX*2, blockY*2, blockX*2+1, blockY*2+1), fill = "white")

        # for blockY in range(len(currentShape) - 1, -1, -1):
        #     for blockX, isBlock in enumerate(currentShape[blockY]):
        #         if isBlock and tetris[collisioncheckY][collisioncheckX]:
        #             collisionCheckX = currX + blockX
        #             collisionCheckY = currY + blockY + 1
        #             draw.rectangle((collisioncheckX*8, collisioncheckY*8, collisioncheckX*8+7, collisioncheckY*8+7), outline="white", fill="white")

logic()

waitForRelease = []
pressed = False

GPIO.output(column, GPIO.LOW)

while True:
    try:
        for note in lead:
            if max(tetris[0]) == 1:
                draw.text((35, 28), "GAME OVER", fill="white")
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
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
                
            b.stop()
            b.start(1)
            freq = note[0]
            if freq == 0: b.stop()
            else: b.ChangeFrequency(freq)
            sleep(note[1]*(60.0/BPM))
    except KeyboardInterrupt:
        b.stop()
        GPIO.cleanup()
        nextLogicCall.cancel()
        exit(0)
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
