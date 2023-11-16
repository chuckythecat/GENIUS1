# https://benjames171.itch.io/safe-cracker
from RPi import GPIO
from time import sleep
import threading
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

from PIL import ImageFont

import random

global games
games = 5

class SafeCrackerGame:
    def beeper(self):
        self.buzzer.ChangeFrequency(2000)
        self.buzzer.start(1)
        sleep(0.2)
        self.buzzer.stop()

    def wrongAnswerBeeper(self):
        for i in range(0, 3):
            self.buzzer.ChangeFrequency(100)
            sleep(0.1)
            self.buzzer.start(1)
            sleep(0.1)
            self.buzzer.stop()

    def __init__(self, buzzerPin, rowPins, columnPins):
        i2c_oled = i2c(port=1, address=0x3C)
        self.oled = ssd1306(i2c_oled)

        self.font = ImageFont.truetype("./FRM325x8.ttf", 10)

        self.rowPins = rowPins[:3]
        self.columnPins = columnPins[:3]

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(buzzerPin, GPIO.OUT)

        self.buzzer = GPIO.PWM(buzzerPin, 100)

        for row in rowPins:
            GPIO.setup(row, GPIO.OUT)

        for column in columnPins:
            GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.pressed = []
        self.waitForRelease = []

        self.reset()
        self.tries = 1

    def reset(self):
        self.code = []

        self.revealedNumbers = ["X", "X", "X", "X", "X"]

        for i in range(0, 5):
            self.code.append(random.randint(1, 9))

        self.tries = 6

        self.guesses = []

        self.guess = []

    def play(self):
        with canvas(self.oled) as draw:
            draw.text((47, 0), "Взлом сейфа", fill="white", font=self.font)
            draw.text((0, 16), "Правила:", fill="white", font=self.font)
            draw.text((0, 26), "попытайся угадать", fill="white", font=self.font)
            draw.text((0, 36), "пароль от сейфа", fill="white", font=self.font)
            draw.text((0, 46), "+ увеличь цифру", fill="white", font=self.font)
            draw.text((0, 56), "- уменьши цифру", fill="white", font=self.font)

        sleep(5)

        while True:
            with canvas(self.oled) as draw:
                # code
                draw.text((25, 0), " ".join(self.revealedNumbers), fill="white", font=self.font)
                # tries left
                draw.text((100, 0), str(self.tries), fill="white", font=self.font)

                draw.text((0, 15), " ".join(str(number) for number in self.guess), fill="white", font=self.font)

                for index, a in enumerate(self.guesses):
                    y = 15 + (index + 1) * 15
                    draw.text((0, y), " ".join(str(number) for number in self.guesses[index]["guess"]), fill="white", font=self.font)
                    draw.text((70, y), " ".join(str(number) for number in self.guesses[index]["answer"]), fill="white", font=self.font)

            for rownumber, row in enumerate(self.rowPins):
                GPIO.output(row, GPIO.LOW)
                for columnnumber, column in enumerate(self.columnPins):
                    buttonnumber = columnnumber + 1 + ((rownumber) * 3)
                    if GPIO.input(column) == 0:
                        self.pressed.append(buttonnumber)
                    elif buttonnumber in self.waitForRelease:
                        self.waitForRelease.remove(buttonnumber)
                GPIO.output(row, GPIO.HIGH)

            for button in self.waitForRelease:
                if button in self.pressed: self.pressed.remove(button)

            if self.pressed:
                self.guess.append(self.pressed[0])
                for button in self.pressed:
                    if not button in self.waitForRelease:
                        self.waitForRelease.append(button)
                if not (len(self.guess) > 4):
                    self.beep = threading.Thread(target=self.beeper)
                    self.beep.start()

            if len(self.guess) > 4:
                if self.guess == self.code:
                    with canvas(self.oled) as draw:
                        draw.text((15, 0), "Сейф взломан!", fill="white", font=self.font)
                    sleep(5)
                    self.reset()
                    continue

                else:
                    if self.tries != 1:
                        self.wrongAnswerBeep = threading.Thread(target=self.wrongAnswerBeeper)
                        self.wrongAnswerBeep.start()
                    temp = []
                    for index, number in enumerate(self.code):
                        if self.guess[index] == number:
                            self.revealedNumbers[index] = str(number)
                            temp.append(str(number))
                        elif self.guess[index] > number:
                            temp.append("-")
                        elif self.guess[index] < number:
                            temp.append("+")
                    self.guesses.insert(0, {"guess": self.guess, "answer": temp})
                    self.guess = []
                    self.tries -= 1

            if self.tries == 0:
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

            if len(self.guesses) > 2: del self.guesses[-1]

            self.pressed = []

    def exit(self):
        GPIO.cleanup()
        self.oled.clear()

if __name__ == '__main__':
    rows = [16, 19, 20, 21]
    columns = [5, 6, 12, 13]

    buzzerpin = 27
    game = SafeCrackerGame(buzzerpin, rows, columns)
    try:
        game.play()
    except KeyboardInterrupt:
        game.exit()
        exit(0)
