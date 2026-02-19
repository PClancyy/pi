import time
import board
import busio
from adafruit_pca9685 import PCA9685

SERVO_CH = 0

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

print("Starting servo test on channel", SERVO_CH)

def set_pulse(us):
    period_us = 20000
    duty = int(us / period_us * 65535)
    pca.channels[SERVO_CH].duty_cycle = duty
    print(f"Pulse: {us}us  Duty: {duty}")

try:
    while True:
        print("Center")
        set_pulse(1500)
        time.sleep(1)

        print("Left")
        set_pulse(1000)
        time.sleep(1)

        print("Right")
        set_pulse(2000)
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping")
    pca.channels[SERVO_CH].duty_cycle = 0
