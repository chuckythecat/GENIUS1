from RPi import GPIO

import time
import random

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import threading

from luma.core.interface.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.oled.device import ssd1306

class ArkanoidGame:
    def __init__(self, buzzerPin, clkPin, dtPin, rowPins, columnPins):
        # задаем режим нумерации контактов BCM
        GPIO.setmode(GPIO.BCM)

        # объявляем переменные контактов энкодера заново, чтобы они
        # принадлежали классу, а не функции, и к ним можно было
        # получить доступ из метода start
        self.clkPin = clkPin
        self.dtPin = dtPin

        # устанавливаем режим контактов энкодера на вход с подтяжкой вниз
        GPIO.setup(self.clkPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dtPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # объявляем переменные текущего состояния контактов энкодера
        self.clkState = GPIO.input(self.clkPin)
        self.dtState = GPIO.input(self.dtPin)
        self.clkLastState = GPIO.input(self.clkPin)

        # TODO: заставить кнопку энкодера работать

        # так как в этой игре нам нужна только одна кнопка
        # (для подачи мячика), устанавливаем только режим
        # первого контакта строки матрицы кнопок на вывод
        self.row1 = rowPins[0]
        GPIO.setup(self.row1, GPIO.OUT)
        # режим первого контакта столбца матрицы кнопок на вход с подтяжкой вверх
        self.column1 = columnPins[0]
        GPIO.setup(self.column1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # ставим режим контакта пищалки на вывод
        GPIO.setup(buzzerPin, GPIO.OUT)

        # задаем ШИМ для пищалки
        self.buzzer = GPIO.PWM(buzzerPin, 100)

        # настраиваем матрицу светодиодов
        spi_matrix = spi(port=0, device=0, gpio=noop())
        self.matrix = max7219(spi_matrix)

        # настраиваем OLED экранчик
        i2c_oled = i2c(port=1, address=0x3C)
        self.oled = ssd1306(i2c_oled)

        # устанавливаем константы ширины и высоты экрана, понадобятся позже
        # для некоторых рассчетов
        self.width = 128
        self.height = 64

        # объявляем массив кирпичиков, которые будем разбивать в игре
        self.bricks = [
            {"x1": 0, "y1": 0, "x2": 15, "y2": 3},
            {"x1": 17, "y1": 0, "x2": 32, "y2": 3},
            {"x1": 34, "y1": 0, "x2": 49, "y2": 3},
            {"x1": 51, "y1": 0, "x2": 66, "y2": 3},
            {"x1": 68, "y1": 0, "x2": 83, "y2": 3},
            {"x1": 85, "y1": 0, "x2": 100, "y2": 3},
            {"x1": 102, "y1": 0, "x2": 117, "y2": 3}
        ]

        # настраиваемая ширина ракетки
        self.paddleWidth = 20
        # настраиваемая высота ракетки
        self.paddleHeight = 3
        # чувствительность энкодера - на сколько пикселей будет сдвигаться
        # ракетка при повороте энкодера на одну ступень
        self.sensitivity = 3
        # включить заполнение ракетки
        self.solidPaddle = True
        # настраиваемое количество жизней
        self.lives = 3

        # флаг движения мячика (True - мяч двигается, False - нет)
        self.ballmoving = False
        # переменная текущей позиции ракетки
        # по умолчанию устанавливается посередине игрового поля
        self.paddlePos = int((self.width - 1 - self.paddleWidth) / 2)
        # перменная текущей позиции мячика по оси X
        # по умолчанию устанавливается посередине ракетки
        self.ballx = int(self.paddlePos + self.paddleWidth/2)
        # перменная текущей позиции мячика по оси X
        # по умолчанию устанавливается сразу же над ракеткой
        self.bally = self.height - 2 - self.paddleHeight
        # переменная текущего направления движения мячика по оси X
        # 1 - Вправо, -1 - Влево
        # по умолчанию устанавливается случайно
        self.balldirectionX = random.choice([1, -1])
        # переменная текущего направления движения мячика по оси Y
        # 1 - вниз, -1 - вверх
        # по умолчанию устанавливается вверх
        self.balldirectionY = -1
        # флаг пищалки (True - пищим, False - не пищим)
        self.buzz = False
        # флаг для корректного завершения метода перерисовки экрана redraw
        # устанавливается на True при завершении игры
        self.kill = False
        # начинаем игру
        self.start()

    # основной метод, обрабатывающая логику игры
    # (движение мячика, столкновение мячика с ракеткой/стенами игрового поля,
    # с кирпичиками, падение мячика вниз за пределы игрового поля,
    # если игрок не успел поймать мячик ракеткой, уничтожение кирпичиков)
    # вызывается каждые 50мс при помощи таймера nextLogicCall
    def balllogic(self):
        self.nextLogicCall = threading.Timer(0.05, self.balllogic)
        self.nextLogicCall.start()
        # global ballx
        # global bally
        # global balldirectionX
        # global balldirectionY
        # global ballmoving
        # global lives
        # global buzz
        collision = ""
        # если мяч двигается:
        if self.ballmoving:
            # прибавляем к координатам мячика по каждой из осей
            # текущее направление движения мячика
            self.ballx += self.balldirectionX
            self.bally += self.balldirectionY
        
        # TODO: переписать на создание асинхронных потоков(?)
        # если на прошлом вызове метода пищалка пищала, отключаем ее
        if self.buzz:
            self.buzz = False
            self.buzzer.stop()

        # проверка столкновения со стенами игрового поля:
        # правая
        if self.ballx >= 127:
            self.balldirectionX = -1
            self.buzz = 1
        # левая
        if self.ballx <= 0:
            self.balldirectionX = 1
            self.buzz = 1
        # верхняя
        if self.bally <= 0:
            self.balldirectionY = 1
            self.buzz = 1

        # проверка столкновения мячика с ракеткой:
        # если мячик ниже верхней грани ракетки:
        if self.bally >= self.height-self.paddleHeight-1:
            # если мячик не левее и не правее ракетки:
            if self.ballx >= self.paddlePos and self.ballx <= self.paddlePos+self.paddleWidth:
                self.balldirectionY = -1
                self.buzz = 1

        # проверка выхода мячика за игровое поле,
        # если не успели поймать его ракеткой:
        if self.bally >= 63:
            # отключить движение мячика по полю
            self.ballmoving = False
            # расположить мячик прямо над ракеткой
            self.bally = self.height - 2 - self.paddleHeight
            self.balldirectionX = random.choice([1, -1])
            self.balldirectionY = -1
            self.lives -= 1
            with canvas(self.matrix) as draw:
                draw.text((1, -2), str(self.lives), fill="white")

        # проверка столкновения с каждым из кирпичиков:
        for brick in self.bricks[:]:
            # с левой стороны
            if self.ballx == brick["x1"]-1 \
            and self.bally >= brick["y1"]-1 \
            and self.bally <= brick["y2"]+1 \
            and self.balldirectionX == 1:
                self.balldirectionX = -1
                collision += "left "
            # с правой стороны
            elif self.ballx == brick["x2"]+1 \
            and self.bally >= brick["y1"]-1 \
            and self.bally <= brick["y2"]+1 \
            and self.balldirectionX == -1:
                self.balldirectionX = 1
                collision += "right "
            # с верхней стороны
            if self.bally == brick["y1"]-1 \
            and self.ballx >= brick["x1"]-1 \
            and self.ballx <= brick["x2"]+1 \
            and self.balldirectionY == 1:
                self.balldirectionY = -1
                collision += "top "
            # с нижней стороны
            elif self.bally == brick["y2"]+1 \
            and self.ballx >= brick["x1"]-1 \
            and self.ballx <= brick["x2"]+1 \
            and self.balldirectionY == -1:
                self.balldirectionY = 1
                collision += "bottom "
            if collision != "":
                self.bricks.remove(brick)
                self.buzz = 1
                collision = ""

        # если где либо в коде игры флаг пищалки был установлен в True, пищим
        if self.buzz: self.buzzer.start(1)

    # метод, рисующий графику игры на OLED экранчике в бесконечном цикле
    def redraw(self):
        while True:
            if self.kill:
                break
            with canvas(self.oled) as draw:
                if self.lives == 0:
                    print("GAME OVER\n")
                    draw.text((35, 28), "GAME OVER", fill="white")
                    time.sleep(5)
                draw.rectangle((self.paddlePos, self.height-self.paddleHeight, self.paddlePos+self.paddleWidth, self.height), outline=255, fill=self.solidPaddle)
                draw.rectangle((self.ballx, self.bally, self.ballx, self.bally), outline=255, fill=1)

                for brick in self.bricks:
                    draw.rectangle((brick["x1"], brick["y1"], brick["x2"], brick["y2"]), outline=255, fill=1)

    # основной метод, который запускает поток с методом, отрисовывающим графику
    # игры, таймер логики игры; обрабатывает поворот энкодера игроком,
    # запускает движение мячика по нажатию кнопки,
    # обновляет позицию мячика по оси X, чтобы он всегда
    # был посередине ракетки, если мяч не двигается
    def start(self):
        # запускаем поток с методом, отрисовывающим графику игры на экранчике
        thread = threading.Thread(target = self.redraw)
        thread.start()

        # вызываем основной метод, обрабатывающий логику игры.
        # после первого вызова метода, в нем сразу же создастся таймер,
        # который будет автоматически вызывать этот же метод каждые 50 мс.
        self.balllogic()

        # ставим режим строки на вывод для правильной работы кнопки матрицы
        GPIO.output(self.row1, GPIO.LOW)
        self.matrix.contrast(1)
        # пишем на матрице светодиодов текущее количество оставшихся жизней
        with canvas(self.matrix) as draw:
            draw.text((1, -2), str(self.lives), fill="white")

        # бесконечный цикл:
        while True:
            # обновляем текущее состояние контактов энкодера
            self.clkState = GPIO.input(self.clkPin)
            self.dtState = GPIO.input(self.dtPin)
            self.col1state = GPIO.input(self.column1)

            # если кнопка нажата и мячик не двигается:
            # запускаем движение мячика
            if self.col1state == 0 and self.ballmoving == False: self.ballmoving = True

            # обрабатываем поворот энкодера: если последнее состояние
            # энкодера отличается от текущего, двигаем ракеткой
            # в ту же сторону, в которую поворачивается энкодер
            if self.clkLastState == 1 and self.clkState == 0:
                # при повороте энкодера двигаем ракеткой в соответствующую
                # сторону на количество пикселей, равное переменной sensitivity
                if self.dtState == 1: self.paddlePos -= self.sensitivity
                else: self.paddlePos += self.sensitivity
                # не даем ракетке выйти за пределы экрана
                if self.paddlePos > self.width - 1 - self.paddleWidth:
                    self.paddlePos = self.width - 1 - self.paddleWidth
                self.paddlePos = 0 if self.paddlePos < 0 else self.paddlePos
            
            # если мячик не двигается по игровому полю, постоянно обновляем
            # его позицию по оси X, чтобы он был посередине ракетки
            if not self.ballmoving:
                self.ballx = int(self.paddlePos + self.paddleWidth/2)

            # переменная, запоминающая последнее состояние энкодера
            self.clkLastState = self.clkState

    # функция выхода из игры
    def exit(self):
        self.nextLogicCall.cancel()
        self.kill = True
        # очищаем все настройки GPIO (типы контактов (вход/выход),
        # нумерации контактов (BCM/BOARD), и т. д.)
        GPIO.cleanup()
        # очищаем OLED экран
        self.oled.clear()
        # очищаем матрицу светодиодов
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
    game = ArkanoidGame(buzzerpin, clk, dt, rows, columns)
    try:
        # запускаем игру
        game.play()
    # если нажата комбинация клавиш Ctrl+C:
    except KeyboardInterrupt:
        # закрываем игру
        game.exit()
        # завершаем выполнение файла
        exit(0)
