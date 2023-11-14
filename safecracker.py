# https://benjames171.itch.io/safe-cracker
from RPi import GPIO
from time import sleep
import threading
from luma.core.interface.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.core.bitmap_font import bitmap_font
from luma.core.legacy import font
from luma.oled.device import ssd1306

from PIL import ImageFont

import random

FontTemp = ImageFont.truetype("./FRM325x8.ttf", 10)

rows = [16, 19, 20]
columns = [5, 6, 12]

clk = 18
dt = 17
buzzerpin = 27

i2c_oled = i2c(port=1, address=0x3C)
oled = ssd1306(i2c_oled)

GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzerpin, GPIO.OUT)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

b = GPIO.PWM(buzzerpin, 100)
b.ChangeFrequency(2000)

counter = 0

clkLastState = GPIO.input(clk)

# with canvas(oled) as draw:
#     # code
#     draw.text((25, 0), "X X X X X", fill="white", font=FontTemp)
#     # tries left
#     draw.text((100, 0), "6", fill="white", font=FontTemp)

#     # current line
#     draw.text((0, 15), "5 4 8 2 6", fill="white", font=FontTemp)
#     draw.text((70, 15), "+ 4 8 - 6", fill="white", font=FontTemp)

#     # 2nd line
#     draw.text((0, 29), "5 4 8 2 6", fill="white", font=FontTemp)
#     draw.text((70, 29), "+ 4 8 - 6", fill="white", font=FontTemp)

#     # 3rd line
#     draw.text((0, 44), "5 4 8 2 6", fill="white", font=FontTemp)
#     draw.text((70, 44), "+ 4 8 - 6", fill="white", font=FontTemp)

def reset():
    code = []

    revealedNumbers = ["X", "X", "X", "X", "X"]

    for i in range(0, 5):
        code.append(random.randint(1, 9))

    tries = 6

    guesses = []

    guess = []

    return [code, revealedNumbers, tries, guesses, guess]

code, revealedNumbers, tries, guesses, guess = reset()

# row output, column input
for row in rows:
    GPIO.setup(row, GPIO.OUT)

for column in columns:
    GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pressed = []
waitForRelease = []

def beeper():
    b.ChangeFrequency(2000)
    b.start(1)
    sleep(0.2)
    b.stop()

beep = threading.Thread(target=beeper)

def wrongAnswerBeeper():
    for i in range(0, 3):
        sleep(0.1)
        b.start(1)
        b.ChangeFrequency(100)
        sleep(0.1)
        b.stop()

wrongAnswerBeep = threading.Thread(target=wrongAnswerBeeper)

with canvas(oled) as draw:
    draw.text((47, 0), "Взлом сейфа", fill="white", font=FontTemp)
    draw.text((0, 16), "Правила:", fill="white", font=FontTemp)
    draw.text((0, 26), "попытайся угадать", fill="white", font=FontTemp)
    draw.text((0, 36), "пароль от сейфа", fill="white", font=FontTemp)
    draw.text((0, 46), "+ увеличь цифру", fill="white", font=FontTemp)
    draw.text((0, 56), "- уменьши цифру", fill="white", font=FontTemp)

sleep(5)

while True:
    with canvas(oled) as draw:
        # code
        draw.text((25, 0), " ".join(revealedNumbers), fill="white", font=FontTemp)
        # tries left
        draw.text((100, 0), str(tries), fill="white", font=FontTemp)

        draw.text((0, 15), " ".join(str(number) for number in guess), fill="white", font=FontTemp)

        for index, a in enumerate(guesses):
            y = 15 + (index + 1) * 15
            draw.text((0, y), " ".join(str(number) for number in guesses[index]["guess"]), fill="white", font=FontTemp)
            draw.text((70, y), " ".join(str(number) for number in guesses[index]["answer"]), fill="white", font=FontTemp)

    for rownumber, row in enumerate(rows):
        GPIO.output(row, GPIO.LOW)
        for columnnumber, column in enumerate(columns):
            buttonnumber = columnnumber + 1 + ((rownumber) * 3)
            if GPIO.input(column) == 0:
                pressed.append(buttonnumber)
            elif buttonnumber in waitForRelease:
                waitForRelease.remove(buttonnumber)
        GPIO.output(row, GPIO.HIGH)
    # print(f"{pressed}", end="                                                    \r")

    for button in waitForRelease:
        if button in pressed: pressed.remove(button)

    if pressed:
        print(pressed[0])
        guess.append(pressed[0])
        for button in pressed:
            if not button in waitForRelease:
                waitForRelease.append(button)
        beep.start()
        beep = threading.Thread(target=beeper)

    if len(guess) > 4:
        if guess == code:
            print("WIN!")
            with canvas(oled) as draw:
                draw.text((15, 0), "Сейф взломан!", fill="white", font=FontTemp)
            sleep(5)
            code, revealedNumbers, tries, guesses, guess = reset()
            continue

        else:
            wrongAnswerBeep.start()
            wrongAnswerBeep = threading.Thread(target=wrongAnswerBeeper)
            temp = []
            for index, number in enumerate(code):
                if guess[index] == number:
                    revealedNumbers[index] = str(number)
                    temp.append(str(number))
                elif guess[index] > number:
                    temp.append("-")
                elif guess[index] < number:
                    temp.append("+")
            guesses.insert(0, {"guess": guess, "answer": temp})
            print(guess)
            print(code)
            print(guesses)
            print(revealedNumbers)
            guess = []
            tries -= 1

    if tries == 0:
        print("GAME OVER")
        with canvas(oled) as draw:
            draw.text((15, 0), "Игра окончена!", fill="white", font=FontTemp)
            draw.text((15, 30), "Тебя поймала", fill="white", font=FontTemp)
            draw.text((29, 41), "полиция!", fill="white", font=FontTemp)
        police = 0
        direction = 1
        freq = 400
        b.start(1)
        while police < 3:
            b.ChangeFrequency(freq)
            sleep(0.05)
            freq += direction * 10
            if freq > 700:
                direction = -1
                # sleep(0.5)
            elif freq < 400:
                direction = 1
                sleep(0.2)
                police += 1
        b.stop()
        exit(0)

    if len(guesses) > 2: del guesses[-1]

    pressed = []