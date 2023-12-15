# TODO: переписать логику обработки кнопок с более понятным алгоритмом
# как в simon says
# TODO: добавить функцию удаления последней цифры если игрок ошибся
# TODO: переписать алгоритм полицейской сирены

# https://benjames171.itch.io/safe-cracker
from RPi import GPIO
from time import sleep
import threading
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

from PIL import ImageFont

import random

class SafeCrackerGame:
    # функция, которая будет асинхронно пищать в течении 0.2 секунд
    # при нажатии кнопки
    def beeper(self):
        # ставим частоту пищалки на 2000 гц
        self.buzzer.ChangeFrequency(2000)
        # начинаем пищать
        self.buzzer.start(1)
        # ждем 0.2 секунды
        sleep(0.2)
        # перестаем пищать
        self.buzzer.stop()

    # функция, которая будет асинхронно пищать 3 раза
    # при неверной введенной комбинации сейфа
    def wrongAnswerBeeper(self):
        # цикл, код в котором выполнится 3 раза
        # (эквивалент for(int i; i < 3; i++))
        for i in range(0, 3):
            # ставим частоту пищалки на 100 гц
            self.buzzer.ChangeFrequency(100)
            # начинаем пищать
            self.buzzer.start(1)
            # ждем 0.1 секунды
            sleep(0.1)
            # перестаем пищать
            self.buzzer.stop()
            # ждем еще 0.1 прежде чем пищать еще раз
            sleep(0.1)

    def __init__(self, buzzerPin, clkPin, dtPin, rowPins, columnPins):
        # настраиваем OLED экранчик
        i2c_oled = i2c(port=1, address=0x3C)
        self.oled = ssd1306(i2c_oled)

        # загружаем красивый шрифт, чтобы выводить текст с его помощью
        self.font = ImageFont.truetype("./FRM325x8.ttf", 10)

        # так как в этой игре нам нужно только 9 кнопок (матрица 3 на 3)
        # убираем одну строку и один столбец у матрицы кнопок
        self.rowPins = rowPins[:3]
        self.columnPins = columnPins[:3]

        # задаем режим нумерации контактов BCM
        GPIO.setmode(GPIO.BCM)

        # ставим режим контакта пищалки на вывод
        GPIO.setup(buzzerPin, GPIO.OUT)

        # задаем ШИМ для пищалки
        self.buzzer = GPIO.PWM(buzzerPin, 100)

        # ставим режим строк на вывод для правильной работы матрицы кнопок
        for row in rowPins:
            GPIO.setup(row, GPIO.OUT)

        # ставим режим столбцов на ввод с подтяжкой вверх
        # для правильной работы матрицы кнопок
        for column in columnPins:
            GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # создаем массив для нажатой кнопки
        self.pressed = []
        # массив для проверки удержания кнопки
        self.waitForRelease = []

        # сбрасываем все переменные (количество попыток, правильная комбинация,
        # отгаданные нами цифры, предыдущие попытки отгадать комбинацию)
        # перед началом игры
        self.reset()
        self.tries = 1

    def reset(self):
        # загадываем последовательность из 5 случайных цифр:
        # очищаем массив с правильной комбинацией
        self.code = []

        # добавляем в нее 5 случайных цифр
        # ( код в цикле выполнится 5 раз - эквивалент for(int i; i < 5; i++) )
        for i in range(0, 5):
            self.code.append(random.randint(1, 9))

        # скрываем все отгаданные цифры
        self.revealedNumbers = ["X", "X", "X", "X", "X"]

        # устанавливаем количество попыток на отгдаывание комбинации на 6
        self.tries = 6

        # очищаем массив с предыдущими попытками отгадать комбинацию
        self.guesses = []

        # очищаем массив с текущей попыткой отгадать комбинацию
        self.guess = []

    def play(self):
        # пишем на экране правила игры
        with canvas(self.oled) as draw:
            draw.text((47, 0), "Взлом сейфа", fill="white", font=self.font)
            draw.text((0, 16), "Правила:", fill="white", font=self.font)
            draw.text((0, 26), "попытайся угадать", fill="white", font=self.font)
            draw.text((0, 36), "пароль от сейфа", fill="white", font=self.font)
            draw.text((0, 46), "+ увеличь цифру", fill="white", font=self.font)
            draw.text((0, 56), "- уменьши цифру", fill="white", font=self.font)

        # ждем 5 секунд чтобы игрок успел прочитать правила
        sleep(5)

        # бесконечный цикл:
        while True:
            # рисуем на экране графику:
            with canvas(self.oled) as draw:
                # текущие отгаданные цифры
                draw.text((25, 0), " ".join(self.revealedNumbers), fill="white", font=self.font)

                # оставшееся количество попыток
                draw.text((100, 0), str(self.tries), fill="white", font=self.font)

                # цифры в текущей попытке отгадать комбинацию
                draw.text((0, 15), " ".join(str(number) for number in self.guess), fill="white", font=self.font)

                # предыдущие попытки отгадать комбинацию а также плюсы
                # и минусы, которые дают понять, как нужно изменить цифру,
                # чтобы она приблизилась к правильной цифре в комбинации
                for index, a in enumerate(self.guesses):
                    y = 15 + (index + 1) * 15
                    draw.text((0, y), " ".join(str(number) for number in self.guesses[index]["guess"]), fill="white", font=self.font)
                    draw.text((70, y), " ".join(str(number) for number in self.guesses[index]["answer"]), fill="white", font=self.font)

            # проверяем нажатие кнопок
            # для каждой строки кнопок:
            for rownumber, row in enumerate(self.rowPins):
                # устанавливаем логический ноль на строке
                GPIO.output(row, GPIO.LOW)
                # для каждого столбца:
                for columnnumber, column in enumerate(self.columnPins):
                    # считаем порядковый номер кнопки по формуле
                    buttonnumber = columnnumber + 1 + ((rownumber) * 3)
                    # если нажали кнопку:
                    if GPIO.input(column) == 0:
                        # добавляем порядковый номер
                        # нажатой кнопки в массив кнопок
                        self.pressed.append(buttonnumber)
                    # если кнопка отпущена, и мы ждали
                    # пока эту кнопку отпустят:
                    elif buttonnumber in self.waitForRelease:
                        # убираем эту кнопку из массива уже нажатых кнопок
                        self.waitForRelease.remove(buttonnumber)
                # устанавливаем логическую единицу на строке, чтобы при
                # нажатии кнопок на этой строке на столбце не появлялся
                # логический ноль
                GPIO.output(row, GPIO.HIGH)

            # если кнопка уже была нажата на прошлой итерации цикла:
            for button in self.waitForRelease:
                # убираем эту кнопку из списка нажатых кнопок
                # (таким образом нажатая кнопка будет обработана только один
                # раз, и будет игнорироваться, пока не будет отпущена)
                if button in self.pressed: self.pressed.remove(button)

            # если есть нажатая кнопка:
            if self.pressed:
                # добавляем номер нажатой кнопки в массив текущей попытки
                # отгадать комбинацию
                self.guess.append(self.pressed[0])
                # для каждой нажатой кнопки:
                for button in self.pressed:
                    # если этой кнопки еще нет в массиве удерживаемых кнопок
                    if not button in self.waitForRelease:
                        # добавить ее туда
                        self.waitForRelease.append(button)
                # если в массиве с текущей попыткой отгадать комбинацию
                # меньше 5 цифр:
                if (len(self.guess) != 5):
                    # создаем новый поток
                    self.beep = threading.Thread(target=self.beeper)
                    # запускаем поток, чтобы пропищать
                    self.beep.start()

            # если в массиве с текущей попыткой отгадать комбинацию 5 цифр:
            if len(self.guess) == 5:
                # если мы отгадали комбинацию:
                if self.guess == self.code:
                    # сообщить игроку о том, что он победил
                    with canvas(self.oled) as draw:
                        draw.text((15, 0), "Сейф взломан!", fill="white", font=self.font)
                    # ждем 5 секунд
                    sleep(5)
                    # сбрасываем все переменные, чтобы начать новую игру
                    self.reset()
                    # начинаем новую итерацию бесконечного цикла
                    continue

                # если мы НЕ отгадали комбинацию
                else:
                    # если игрок еще не использовал все попытки:
                    if self.tries != 1:
                        # создаем новый поток
                        self.wrongAnswerBeep = threading.Thread(target=self.wrongAnswerBeeper)
                        # запускаем поток, чтобы пропищать 3 раза, сигнализируя
                        # игроку о том, что попытка отгадать была неудачная
                        self.wrongAnswerBeep.start()
                    # создаем временный массив, в который будем записывать
                    # плюсы и минусы, чтобы игрок мог отгадать комбинацию
                    temp = []
                    # для каждой цифры в коде, и ее порядкового номера:
                    for index, number in enumerate(self.code):
                        # если цифра в массиве текущей попытки отгадать
                        # комбинацию равна цифре в правильной комбинации:
                        if self.guess[index] == number:
                            # записываем эту цифру в массив отгаданных цифр
                            self.revealedNumbers[index] = str(number)
                            # и во временный массив
                            temp.append(str(number))
                        # если цифра в массиве текущей попытки отгадать
                        # комбинацию больше цифры в правильной комбинации:
                        elif self.guess[index] > number:
                            # записываем во временный массив минус
                            temp.append("-")
                        # если цифра в массиве текущей попытки отгадать
                        # комбинацию меньше цифры в правильной комбинации:
                        elif self.guess[index] < number:
                            # записываем во временный массив плюс
                            temp.append("+")
                    # записываем в массив предыдущих попыток отгадать комбинацию
                    # последовательность цифр и то, как их нужно изменить
                    # чтобы приблизиться к правильной комбинации
                    self.guesses.insert(0, {"guess": self.guess, "answer": temp})
                    # очищаем массив с текущей попыткой отгадать комбинацию
                    self.guess = []
                    # отнимаем одну попытку отгадать комбинацию
                    self.tries -= 1

            # если кончилось количество попыток отгадать комбинацию:
            if self.tries == 0:
                # пишем на экране "игра окончана", сообщая игроку о том, что
                # он проиграл
                with canvas(self.oled) as draw:
                    draw.text((15, 0), "Игра окончена!", fill="white", font=self.font)
                    draw.text((15, 30), "Тебя поймала", fill="white", font=self.font)
                    draw.text((29, 41), "полиция!", fill="white", font=self.font)
                
                police = 0
                direction = 1
                freq = 400
                self.buzzer.start(1)
                while police < 3:
                    self.buzzer.ChangeFrequency(freq)
                    sleep(0.05)
                    freq += direction * 10
                    if freq > 700:
                        direction = -1
                        # sleep(0.5)
                    elif freq < 400:
                        direction = 1
                        sleep(0.2)
                        police += 1
                self.buzzer.stop()
                self.exit()
                break

            # если 
            if len(self.guesses) > 2: del self.guesses[-1]

            # очищаем массив нажатых кнопок
            self.pressed = []

    # функция выхода из игры
    def exit(self):
        # очищаем все настройки GPIO (типы контактов (вход/выход),
        # нумерации контактов (BCM/BOARD), и т. д.)
        GPIO.cleanup()
        # очищаем OLED экран
        self.oled.clear()

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
    game = SafeCrackerGame(buzzerpin, clk, dt, rows, columns)
    try:
        # запускаем игру
        game.play()
    # если нажата комбинация клавиш Ctrl+C:
    except KeyboardInterrupt:
        # закрываем игру
        game.exit()
        # завершаем выполнение файла
        exit(0)
