from RPi import GPIO

rows = [16, 19, 20, 21]
columns = [5, 6, 12, 13]

GPIO.setmode(GPIO.BCM)
for row in rows:
    GPIO.setup(row, GPIO.OUT)

for column in columns:
    GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pressed = []

while True:
    for rownumber, row in enumerate(rows):
        GPIO.output(row, GPIO.LOW)
        for columnnumber, column in enumerate(columns):
            if GPIO.input(column) == 0:
                pressed.append(f"{row}+{column} (KEY{columnnumber+1+((rownumber)*4)})")
        GPIO.output(row, GPIO.HIGH)
    print(pressed, end="                                                    \r")
    pressed = []
