import time
import pigpio
from gpiozero import PWMLED
from signal import pause

pi = pigpio.pi('127.0.0.1', 8888)
pi.set_mode(18, pigpio.ALT5)
r = pi.get_PWM_range(18)


print("Range: ", r)

while True:
    pi.hardware_PWM(18, 1000, int(0.8 * r)) # blue


    time.sleep(1)