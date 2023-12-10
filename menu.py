from RPi import GPIO
from time import sleep

# games
from safecracker1 import SafeCrackerGame
from simonsays1 import SimonSaysGame

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

from PIL import ImageFont

clk = 18
dt = 17
rows = [16, 19, 20, 21]
columns = [5, 6, 12, 13]
buzzerpin = 27

i2c_oled = i2c(port=1, address=0x3C)
oled = ssd1306(i2c_oled)
font = ImageFont.truetype("./FRM325x8.ttf", 10)

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


init()

while True:
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    btn = GPIO.input(5)
    print(f"{clkState} {dtState} {btn} {counter}", end="              \r")

    if lastCounter != counter:
        with canvas(oled) as draw:
            draw.rectangle((0, counter * 15, 120, (counter+1) * 15), fill = "black", outline = "white")
            for index, game in enumerate(games):
                draw.text((0, index * 15), game["name"], fill="white", font=font)

    lastCounter = counter

    if clkLastState == 1 and clkState == 0:
        if dtState == 1: counter -= 1
        else: counter += 1
        if counter < 0: counter = 0
        if counter > len(games) - 1: counter = len(games) - 1
    
    clkLastState = clkState

    if btn == 0:
        GPIO.cleanup()
        oled.clear()
        game = games[counter]["init"](buzzerpin, clk, dt, rows, columns)
        try:
            game.play()
        except KeyboardInterrupt:
            game.exit()
        finally:
            init()
