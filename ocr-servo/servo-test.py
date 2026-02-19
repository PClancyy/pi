from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio, time

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50

def set_angle(ch, angle):
    pulse = int(4096 * ((angle * 11) + 500) / 20000)
    pca.channels[ch].duty_cycle = pulse

while True:
    set_angle(0, 60)
    time.sleep(1)
    set_angle(0, 120)
    time.sleep(1)
