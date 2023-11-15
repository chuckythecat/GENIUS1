from RPi import GPIO

import time
import random

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219

import threading

# режимы нумерации контактов
# Raspberry Pi:
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

# задаем контакты пищалки, строки и столбцы кнопок по схеме BCM
buzzerpin = 27
rows = [16, 19, 20, 21]
columns = [5, 6, 12, 13]

class SimonSaysGame:
    def __init__(self, buzzerPin, rowPins, columnPins):
        # создаем массив для текущей последовательности
        self.sequence = []
        # переменную для текущей кнопки в последовательности
        self.sequencecurrent = 0
        # переменную для хода игрока
        self.playing = False
        # переменную для нажатой кнопки
        self.pressed = -1

        self.buzzerPin = buzzerPin
        self.rowPins = rowPins
        self.columnPins = columnPins

        # создаем массив всех кнопок для того, чтобы добавлять
        # случайную кнопку в последовательность
        self.buttons = []

        for rownumber, row in enumerate(self.rowPins):
            for columnnumber, column in enumerate(self.columnPins):
                buttonnumber = columnnumber+1+((rownumber)*4)
                ledrow = columnnumber * 2
                ledcol = rownumber * 2
                self.buttons.append(
                    {"buttonnumber": buttonnumber,
                    "ledrow": ledrow,
                    "ledcol": ledcol})

        # задаем режим нумерации контактов BCM
        GPIO.setmode(GPIO.BCM)

        # ставим режим строк на вывод
        for row in self.rowPins:
            GPIO.setup(row, GPIO.OUT)

        # ставим режим столбцов на ввод с подтяжкой вверх
        for column in self.columnPins:
            GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # ставим режим контакта пищалки на вывод
        GPIO.setup(buzzerpin, GPIO.OUT)

        # задаем ШИМ для пищалки
        self.buzzer = GPIO.PWM(buzzerpin, 100)

        # настраиваем матрицу светодиодов
        spi_matrix = spi(port=0, device=0, gpio=noop())
        self.matrix = max7219(spi_matrix)

    def play(self):
        while True:
            # если НЕ ход игрока:
            if self.playing == False:
                # добавляем случайную цифру в последовательность
                self.sequence.append(random.choice(self.buttons))

                # показываем все цифры на матрице и пищим
                for button in self.sequence:
                    self.buzzer.stop()
                    time.sleep(0.1)
                    with canvas(self.matrix) as draw:
                        draw.rectangle(
                            (button["ledrow"],
                            button["ledcol"],
                            button["ledrow"]+1,
                            button["ledcol"]+1),
                            outline=255, fill=1)
                    self.buzzer.start(1)
                    freq = 100 + button["buttonnumber"] * 100
                    self.buzzer.ChangeFrequency(freq)
                    time.sleep(0.4)

                # перестаем пищать, очищаем матрицу
                self.buzzer.stop()
                self.matrix.clear()
                # даем игроку сходить
                self.pressed = -1
                self.playing = True
            # если ход игрока:
            else:
                # проверяем нажатие кнопок
                for rownumber, row in enumerate(rows):
                    GPIO.output(row, GPIO.LOW)
                    for columnnumber, column in enumerate(columns):
                        if GPIO.input(column) == 0:
                            self.pressed = columnnumber+1+((rownumber)*4)
                    GPIO.output(row, GPIO.HIGH)
                
                # если кнопка нажата:
                if self.pressed != -1:
                    # если нажатая кнопка соответствует текущей цифре в последовательности:
                    if self.pressed == self.sequence[self.sequencecurrent]["buttonnumber"]:
                        self.pressed = -1
                        # показываем цифру на матрице и пищим
                        self.buzzer.start(1)
                        freq = 100 + self.sequence[self.sequencecurrent]["buttonnumber"] * 100
                        self.buzzer.ChangeFrequency(freq)
                        with canvas(self.matrix) as draw:
                            draw.rectangle(
                                (self.sequence[self.sequencecurrent]["ledrow"],
                                self.sequence[self.sequencecurrent]["ledcol"],
                                self.sequence[self.sequencecurrent]["ledrow"]+1,
                                self.sequence[self.sequencecurrent]["ledcol"]+1),
                                outline=255, fill=1)
                        time.sleep(0.5)
                        self.buzzer.stop()
                        self.matrix.clear()

                        self.sequencecurrent += 1
                        # если последняя цифра:
                        if self.sequencecurrent == len(self.sequence):
                            # сбрасываем текущую цифру
                            self.sequencecurrent = 0
                            # ход игрока = нет
                            self.playing = False
                            # сбрасываем нажатие кнопок
                            self.pressed = -1
                            # следующая итерация цикла
                            continue
                    # если нажатая кнопка НЕ соответствует текущей цифре в последовательности:
                    else:
                        # рисуем крестик на матрице
                        with canvas(self.matrix) as draw:
                            draw.line((0, 0, 7, 7), fill=1)
                            draw.line((7, 0, 0, 7), fill=1)
                        # угрожающе пищим три раза
                        for i in range(0, 3):
                            time.sleep(0.1)
                            self.buzzer.start(1)
                            freq = 100
                            self.buzzer.ChangeFrequency(freq)
                            time.sleep(0.4)
                            self.buzzer.stop()
                        self.matrix.clear()
                        time.sleep(2)

                        # перезапускаем игру:
                        # текущая цифра в последовательности = 0 (первая)
                        self.sequencecurrent = 0
                        # ход игрока = нет
                        self.playing = False
                        # сбрасываем нажатие кнопок
                        self.pressed = -1
                        # очищаем последовательность
                        self.sequence = []
                        # следующая итерация цикла
                        continue

    def exit(self):
        GPIO.cleanup()

if __name__ == '__main__':
    game = SimonSaysGame(buzzerpin, rows, columns)
    try:
        game.play()
    except KeyboardInterrupt:
        game.exit()
        exit(0)