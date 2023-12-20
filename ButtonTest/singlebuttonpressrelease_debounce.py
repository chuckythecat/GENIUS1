from RPi import GPIO
import threading

# массив с номерами пинов строк и столбцов
rows = [16, 19, 20, 21]
columns = [5, 6, 12, 13]

# переменная текущей нажатой кнопки
pressed = -1
# переменная для номера удерживаемой кнопки
waitForRelease = -1
debounce = True

# режим нумерации пинов BCM
GPIO.setmode(GPIO.BCM)
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

# делаем строки выводами
for row in rows:
    GPIO.setup(row, GPIO.OUT)

# делаем столбцы выводами с подтяжкой вверх
for column in columns:
    GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def release():
    global debounce
    debounce = True

while True:
    # проверяем нажатие кнопок
    # для каждой строки кнопок:
    for rownumber, row in enumerate(rows):
        # устанавливаем логический ноль на строке
        GPIO.output(row, GPIO.LOW)
        # для каждого столбца:
        for colNumber, column in enumerate(columns):
            # считаем порядковый номер кнопки по формуле
            buttonnumber = colNumber + 1 + (rownumber * 4)
            # если нажали кнопку и никакая больше кнопка не нажата:
            if GPIO.input(column) == 0 \
            and waitForRelease == -1 \
            and debounce:
                debounce = False
                # записываем порядковый номер кнопки в переменную
                pressed = buttonnumber
                # записываем номер кнопки в переменную,
                # чтобы проверять, что эта кнопка уже нажата
                waitForRelease = buttonnumber
                
                threading.Timer(1, release).start()
                # пишем на экран, что кнопка была нажата
                print(f"Pressed {buttonnumber}")

            # если мы ждем, пока кнопку отпустят,
            # и эту кнопку отпустили:
            elif GPIO.input(column) == 1 \
            and waitForRelease == buttonnumber \
            and debounce:
                debounce = False
                # очищаем переменную, чтобы можно
                # было нажать следующую кнопку
                waitForRelease = -1

                threading.Timer(1, release).start()
                # пишем на экран, что кнопка была отпущена
                print(f"Released {buttonnumber}")
        # устанавливаем логическую единицу на строке, чтобы при
        # нажатии кнопок на этой строке на столбце не появлялся
        # логический ноль
        GPIO.output(row, GPIO.HIGH)
    pressed = -1