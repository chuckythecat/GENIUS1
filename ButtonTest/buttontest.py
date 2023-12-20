from RPi import GPIO

rows = [16, 19, 20, 21]
columns = [5, 6, 12, 13]

# объявляем массив для порядковых номеров нажатых кнопок
pressed = []

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

# делаем столбцы вводами
for column in columns:
    GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# бесконечный цикл:
while True:
    # проверяем нажатие кнопок
    # для каждой строки кнопок:
    for rownumber, row in enumerate(rows):
        # устанавливаем логический ноль на строке
        GPIO.output(row, GPIO.LOW)
        # для каждого столбца:
        for columnnumber, column in enumerate(columns):
            # если нажали кнопку и никакая больше кнопка не нажата:
            if GPIO.input(column) == 0:
                # добавляем порядковый номер кнопки в массив pressed
                pressed.append(f"{row}+{column} (KEY{columnnumber+1+((rownumber)*4)})")
        # устанавливаем логическую единицу на строке, чтобы при
        # нажатии кнопок на этой строке на столбце не появлялся
        # логический ноль
        GPIO.output(row, GPIO.HIGH)
    # выводим все нажатые кнопки на экран

    # параметр end с символом перевода строки \r
    # позволяет нам каждую итерацию цикла писать
    # нажатые кнопки на той же строке, вместо
    # того, чтобы плодить огромное количество строк
    print(pressed, end="                                                    \r")
    # очищаем массив нажатых кнопок
    pressed = []
