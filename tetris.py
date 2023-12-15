from RPi import GPIO
import time

from luma.core.interface.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.oled.device import ssd1306
from pprint import pprint
import random
import threading
from PIL import ImageFont

class TetrisGame:
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

    def defineTetrisMelody(self):
    # https://github.com/lukecyca/TetrisThemeArduino/blob/master/TetrisThemeArduino.ino
        self.lead = [
            # part 1
            (self.E5, 1.0),
            (self.B4, 0.5),
            (self.C5, 0.5),
            (self.D5, 1.0),
            (self.C5, 0.5),
            (self.B4, 0.5),
            (self.A4, 1.0),
            (self.A4, 0.5),
            (self.C5, 0.5),
            (self.E5, 1.0),
            (self.D5, 0.5),
            (self.C5, 0.5),
            (self.B4, 1.0),
            (self.B4, 0.5),
            (self.C5, 0.5),
            (self.D5, 1.0),
            (self.E5, 1.0),
            (self.C5, 1.0),
            (self.A4, 1.0),
            (self.A4, 1.0),
            (self.R, 1.0),
            #
            (self.D5, 1.5),
            (self.F5, 0.5),
            (self.A5, 1.0),
            (self.G5, 0.5),
            (self.F5, 0.5),
            (self.E5, 1.5),
            (self.C5, 0.5),
            (self.E5, 1.0),
            (self.D5, 0.5),
            (self.C5, 0.5),
            (self.B4, 1.0),
            (self.B4, 0.5),
            (self.C5, 0.5),
            (self.D5, 1.0),
            (self.E5, 1.0),
            (self.C5, 1.0),
            (self.A4, 1.0),
            (self.A4, 1.0),
            (self.R, 1.0),
            # part 2
            (self.E4, 2.0),
            (self.C4, 2.0),
            (self.D4, 2.0),
            (self.B3, 2.0),
            (self.C4, 2.0),
            (self.A3, 2.0),
            (self.GS3, 2.0),
            (self.B3, 2.0),
            #
            (self.E4, 2.0),
            (self.C4, 2.0),
            (self.D4, 2.0),
            (self.B3, 2.0),
            (self.C4, 1.0),
            (self.E4, 1.0),
            (self.A4, 1.0),
            (self.A4, 1.0),
            (self.GS4, 3.0),
            (self.R, 1.0)
        ]

    def buttonHandler(self, pressed):
        if pressed == 21 and not self.checkCollision(self.currentShape, self.tetris, self.currX, self.currY, side = 0): self.currX -= 1
        elif pressed == 20 and not self.checkCollision(self.currentShape, self.tetris, self.currX, self.currY, side = 2): self.currX += 1
        rotatedShape = self.rotateShape(self.currentShape)
        if pressed == 16 and not self.checkCollision(rotatedShape, self.tetris, self.currX, self.currY, side = -1):
            self.currentShape = rotatedShape

    def rotateShape(self, shape, clockwise = True):
        rotatedShape = []
        for index, isBlock in enumerate(shape[0]):
            row = []
            for block in shape:
                row.append(block[index])
            rotatedShape.append(row)

        if clockwise:
            for row in rotatedShape:
                row.reverse()
        else:
            rotatedShape.reverse()

        return rotatedShape

    def checkCollision(self, shape, field, currentX, currentY, side = 1): # -1 - inside, 0 - left, 1 - bottom, 2 - right
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

                if isBlock and self.tetris[checkY][checkX]:
                    return True
        return False

    def logic(self):
        # создаем переменную, чтобы было с чем сравнивать в первой итерации цикла
        self.currentTime = time.time() - 2 * self.every
        # бесконечный цикл
        while True:
            # если установлен флаг закрытия игры, выходим из цикла
            if self.kill: break
            # считаем время выполнения одной итерации бесконечного цикла:
            # отнимаем от текущего времени время начала выполнения прошлой
            # итерации цикла
            timePerLogic = time.time() - self.currentTime
            # если цикл выполнился быстрее, чем за время, указанное в
            # переменной self.every, остальное время ничего не делаем
            # и просто ждем, чтобы логика не выполнялась слишком быстро
            if timePerLogic < self.every:
                time.sleep(self.every - timePerLogic)
            # записываем время начала выполнения текущей итерации
            # бесконечного цикла, чтобы на следующей итерации цикла узнать
            # сколько времени заняло выполнение кода
            self.currentTime = time.time()

            self.currY += 1

            with canvas(self.oled) as draw:
                draw.rectangle(self.oled.bounding_box, outline = "white", fill = "black")
                
                for y, line in enumerate(self.tetris):
                    for x, block in enumerate(line):
                        if block: draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline = "white", fill = "black")
                
                for y, line in enumerate(self.tetris):
                    if min(line):
                        for x in range(0, 8):
                            draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline = "white", fill = "white")
                        del self.tetris[y]
                        self.tetris.insert(0, [0, 0, 0, 0, 0, 0, 0, 0])

                for blockY, row in enumerate(self.currentShape):
                    for blockX, isBlock in enumerate(row):
                        if isBlock:
                            x = self.currX + blockX
                            y = self.currY + blockY
                            draw.rectangle((x*8, y*8, x*8+7, y*8+7), outline = "white", fill = "black")

                if self.checkCollision(self.currentShape, self.tetris, self.currX, self.currY, side = 1):
                    for changeBlockY, row in enumerate(self.currentShape):
                        for changeBlockX, isBlock in enumerate(row):
                            if isBlock: self.tetris[self.currY+changeBlockY][self.currX+changeBlockX] = 1
                    self.currX = 3
                    self.currY = 0
                    self.currentShape = self.nextShape
                    self.nextShape = self.shapes[random.choice(list(self.shapes.keys()))]
                    if self.checkCollision(self.currentShape, self.tetris, self.currX, self.currY, side = -1):
                        print("GAME OVER")
                        draw.rectangle(self.oled.bounding_box, outline = "black", fill = "black")
                        draw.text((0, 28), "Вы", fill="white", font = self.font)
                        draw.text((0, 38), "проиграли!", fill="white", font = self.font)
                        self.kill = True
                        break
                    with canvas(self.matrix) as draw:
                        for blockY, row in enumerate(self.nextShape):
                            for blockX, isBlock in enumerate(row):
                                if isBlock: draw.rectangle((blockX*2, blockY*2, blockX*2+1, blockY*2+1), fill = "white")
    

    def resetTetris(self):
        self.tetris = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
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

        self.currentShape = self.shapes[random.choice(list(self.shapes.keys()))]
        self.nextShape = self.shapes[random.choice(list(self.shapes.keys()))]
        self.currX = 3
        self.currY = 0


    def __init__(self, buzzerPin, clkPin, dtPin, rowPins, columnPins):
        self.rowPins = rowPins
        self.columnPin = columnPins[-1]

        GPIO.setmode(GPIO.BCM)

        for row in self.rowPins:
            GPIO.setup(row, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(row, GPIO.FALLING, self.buttonHandler, 200)

        GPIO.setup(self.columnPin, GPIO.OUT)
        GPIO.setup(buzzerPin, GPIO.OUT)
        self.buzzer = GPIO.PWM(buzzerPin, 100)

        serial = i2c(port = 1, address = 0x3C)
        self.oled = ssd1306(serial, rotate = 3)

        spi_matrix = spi(port = 0, device = 0, gpio = noop())
        self.matrix = max7219(spi_matrix, rotate = 3)

        self.defineTetrisMelody()

        # загружаем красивый шрифт, чтобы выводить текст с его помощью
        self.font = ImageFont.truetype("./FRM325x8.ttf", 9)

        self.shapes = {
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

        self.resetTetris()

        self.nextLogicCall = None

        self.gameover = False

        self.waitForRelease = []
        self.pressed = False

        GPIO.output(self.columnPin, GPIO.LOW)

        self.BPM = 140

        self.kill = False

        self.every = 0.3

    def play(self):
        with canvas(self.matrix) as draw:
            for blockY, row in enumerate(self.nextShape):
                for blockX, isBlock in enumerate(row):
                    if isBlock:
                        draw.rectangle((blockX*2, blockY*2, blockX*2+1, blockY*2+1), fill = "white")

        logic_thread = threading.Thread(target = self.logic)
        logic_thread.start()

        while True:
            if self.kill: break
            for note in self.lead:
                if self.kill: break
                self.buzzer.stop()
                self.buzzer.start(1)
                freq = note[0]
                if freq == 0: self.buzzer.stop()
                else: self.buzzer.ChangeFrequency(freq)
                time.sleep(note[1]*(60.0/self.BPM))
        
        logic_thread.join()
        time.sleep(5)
        self.exit()

    def exit(self):
        self.kill = True
        self.buzzer.stop()
        GPIO.cleanup()
        self.oled.clear()
        self.matrix.clear()

# если файл запущен напрямую (не импортирован в качестве модуля)
if __name__ == '__main__':
    # задаем контакты пищалки, энкодера, строки и столбцы кнопок по схеме BCM
    # (контакты энкодера в этой игре не нужны, но мы все равно оставим их для
    # совместимости с меню)
    rows = [16, 19, 20, 21]
    columns = [5, 6, 12, 13]
    buzzerpin = 27
    clk = 18
    dt = 17

    # режимы нумерации контактов Raspberry Pi (для справки):
    # BOARD  BCM  BOARD
    #   3V3 1   2 5V
    # GPIO2 3   4 5V
    # GPIO3 5   6 GND
    # GPIO4 7   8 GPIO14
    #   GND 9  10 GPIO15
    #GPIO17 11 12 GPIO18
    #GPIO27 13 14 GND
    #GPIO22 15 16 GPIO23
    #   3V3 17 18 GPIO24
    #GPIO10 19 20 GND
    # GPIO9 21 22 GPIO25
    #GPIO11 23 24 GPIO8
    #   GND 25 26 GPIO7
    # ID_SD 27 28 ID_SC
    # GPIO5 29 30 GND
    # GPIO6 31 32 GPIO12
    #GPIO13 33 34 GND
    #GPIO19 35 36 GPIO16
    #GPIO26 37 38 GPIO20
    #   GND 39 40 GPIO21

    # создать объект игры
    game = TetrisGame(buzzerpin, clk, dt, rows, columns)
    try:
        # запускаем игру
        game.play()
    # если нажата комбинация клавиш Ctrl+C:
    except KeyboardInterrupt:
        # закрываем игру
        game.exit()
        # завершаем выполнение файла
        exit(0)
