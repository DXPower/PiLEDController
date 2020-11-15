from threading import Thread
import time
import pigpio
import colorsys
import typing
import logging
import traceback

class LEDController:
    def __init__(self):
        self.pulseThread = None

        print("Starting pi")
        self.pi = pigpio.pi()
        print("Started")

        self.pi.set_mode(3, pigpio.INPUT) # Cycle button

        # self.pi.set_mode(12, pigpio.OUTPUT) # Blue
        # self.pi.set_mode(19, pigpio.OUTPUT) # Red
        self.pi.set_mode(2, pigpio.OUTPUT) # Green

        # self.pi.set_PWM_range(12, 40000)
        # self.pi.set_PWM_range(19, 40000)

        self.pi.set_PWM_frequency(2, 1000)

        self.hard_range = self.pi.get_PWM_range(12) # Range for hardware PWM
        self.soft_range = self.pi.get_PWM_range(2) # Range for software PWM
        
        self.set_color(0.6, 1, 1, 1)
        print("init done")

    def __del__(self):
        self.stop_pulse()

    def read_cycle_btn(self):
        return not bool(self.pi.read(3))

    # r, g, b, a in range 0-1
    def set_color(self, r: float, g: float, b: float, a = None):
        self.current_color = (r, g, b)

        if a is not None:
            self.brightness = a

        r *= self.brightness 
        g *= self.brightness 
        b *= self.brightness 

        self.pi.hardware_PWM(12, 1000, int(b * self.hard_range)) # blue
        self.pi.hardware_PWM(19, 1000, int(r * self.hard_range)) # red
        
        self.pi.set_PWM_dutycycle(2, int(g * self.soft_range)) # green

    def set_brightness(self, brightness):
        self.set_color(self.current_color[0], self.current_color[1], self.current_color[2], brightness)

    # inv_speed -> Higher = Slower
    def start_pulse(self, inv_speed = 200):
        try:
            self.doPulse = True
            self.pulseThread = Thread(target = self.__pulse, args = [inv_speed])
            self.pulseThread.start()
        except Exception as e:
            print("Caught")
            logging.error(traceback.format_exc())

    def stop_pulse(self):
        self.doPulse = False

        if hasattr(self, "pulseThread") and self.pulseThread is not None:
            self.pulseThread.join()
            self.pulseThread = None

    # inv_speed -> Higher = Slower
    def __pulse(self, inv_speed):
        hue = 0
        time_step = 1 / inv_speed

        print("In pulse")

        while self.doPulse:
            hue += time_step

            if (hue > 1):
                hue = 0

            rgb = colorsys.hsv_to_rgb(hue, 1, 1)
            self.set_color(rgb[0] / 1.75, rgb[1], rgb[2])

            time.sleep (.01)
