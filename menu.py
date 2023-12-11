from RPi import GPIO

# games
from safecracker1 import SafeCrackerGame
from simonsays1 import SimonSaysGame

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

from PIL import ImageFont

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

# номера контактов энкодера, матрицы кнопок, пищалки
clk = 18
dt = 17
rows = [16, 19, 20, 21]
columns = [5, 6, 12, 13]
buzzerpin = 27

# настраиваем OLED экранчик
i2c_oled = i2c(port=1, address=0x3C)
oled = ssd1306(i2c_oled)
# настраиваем красивый шрифт, чтобы с его помощью выводить текст
font = ImageFont.truetype("./FRM325x8.ttf", 10)

# массив с объектами игр
games = [
    {
        "name": "Взлом сейфа",
        "init": SafeCrackerGame
    },
    {
        "name": "Комбинация",
        "init": SimonSaysGame
    }
]

# функция инициализации энкодера и матрицы кнопок
def init():
    global clkLastState
    global lastCounter
    global counter
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, GPIO.LOW)
    clkLastState = GPIO.input(clk)
    counter = 0
    lastCounter = 1

# инициализируем энкодер и матрицу кнопок перед входом
# в бесконечный цикл, чтобы ввод от игрока работал корректно
init()

# бесконечный цикл:
while True:
    # обновляем состояния кнопки и энкодера
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    btn = GPIO.input(5)

    # если на текущей итерации цикла игрок выбрал новую игру
    if lastCounter != counter:
        # перерисовать OLED экранчик:
        with canvas(oled) as draw:
            # написать названия всех игр по порядку
            for index, game in enumerate(games):
                draw.text((0, index * 15), game["name"], fill="white", font=font)
            # отобразить квадрат вокруг текущей выбранной игры
            draw.rectangle((0, counter * 15, 120, (counter+1) * 15), fill = "black", outline = "white")

    # переменная последней выбранной игры
    lastCounter = counter

    # обработка поворота энкодера
    if clkLastState == 1 and clkState == 0:
        if dtState == 1: counter -= 1
        else: counter += 1
        if counter < 0: counter = 0
        if counter > len(games) - 1: counter = len(games) - 1
    
    # переменная последнего состояния энкодера
    clkLastState = clkState

    # если нажали кнопку:
    if btn == 0:
        # сбрасываем настройки и очищаем OLED экранчик, чтобы не мешать игре
        GPIO.cleanup()
        oled.clear()
        # создаем объект игры и передаем ему номера контактов энкодера,
        # матрицы кнопок и пищалки
        game = games[counter]["init"](buzzerpin, clk, dt, rows, columns)

        try:
            # запускаем игру
            game.play()
        # если нажата комбинация клавиш Ctrl+C:
        except KeyboardInterrupt:
            # закрываем игру
            game.exit()
        # конструкция finally выполняется в любом случае: если мы сами закрыли
        # игру, или если игра закрыла сама себя (например, при проигрыше)
        # таким образом мы можем точно убедиться, что вне зависимости от того,
        # закрыла ли игра сама себя, или мы закрыли ее сами, функция init
        # точно вызовется, и меню продолжит корректно работать
        finally:
            init()
