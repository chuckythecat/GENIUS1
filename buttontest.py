from RPi import GPIO

row1 = 16
row2 = 19
row3 = 20
row4 = 21

column1 = 5
column2 = 6
column3 = 12
column4 = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(row1, GPIO.OUT)
GPIO.setup(column1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(row1, GPIO.LOW)
while True:
    col1state = GPIO.input(column1)
    print(f"{col1state}", end="                 \r")