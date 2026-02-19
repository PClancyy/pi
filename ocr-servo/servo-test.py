from gpiozero import Servo
from time import sleep

print("GPIO servo test starting on GPIO18 (Pin 12). Ctrl+C to stop.")

servo = Servo(18)  # GPIO18

try:
    while True:
        print("min")
        servo.min()
        sleep(1)

        print("mid")
        servo.mid()
        sleep(1)

        print("max")
        servo.max()
        sleep(1)

except KeyboardInterrupt:
    print("Stopping")
