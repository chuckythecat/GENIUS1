from RPi import GPIO

rows = [16, 19, 20, 21]
columns = [5, 6, 12, 13]

pressed = []

GPIO.setmode(GPIO.BCM)

# row output, column input
# for row in rows:
#     GPIO.setup(row, GPIO.OUT)

# for column in columns:
#     GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# while True:
#     for rownumber, row in enumerate(rows):
#         GPIO.output(row, GPIO.LOW)
#         for columnnumber, column in enumerate(columns):
#             if GPIO.input(column) == 0:
#                 pressed.append(f"{row}+{column} (KEY{columnnumber+1+((rownumber)*4)})")
#         GPIO.output(row, GPIO.HIGH)
#     print(pressed, end="                                                    \r")
#     pressed = []

# column output, row input

for row in rows:
    GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for column in columns:
    GPIO.setup(column, GPIO.OUT)

while True:
    for columnnumber, column in enumerate(columns):
        GPIO.output(column, GPIO.LOW)
        for rownumber, row in enumerate(rows):
            if GPIO.input(row) == 0:
                pressed.append(f"{row}+{column} (KEY{columnnumber+1+((rownumber)*4)})")
        GPIO.output(column, GPIO.HIGH)
    print(pressed, end="                                                    \r")
    pressed = []