import time
from led_messages import *
from controller import *
from controller_modes import *
from threading import Thread
from ipcqueue import posixmq 
from daemons.prefab import geventd

import os

class LED_Daemon(geventd.GeventDaemon):
    def __init__(self, pidfile):
        super().__init__(pidfile=pidfile)

        self.controller = None
        self.current_mode = controller_mode()
        self.msg_queue = get_led_msg_queue()

        self.is_cycle_btn_pressed = False

        print("Constructor!")

    def run(self):
        self.controller = LEDController()
        self.active = True
        
        self.loop_thread = Thread(target = self.__work_loop, args = ())
        self.loop_thread.start()

    def __work_loop(self):
        while self.active:
            message = self.get_message()

            if message is not None:
                self.handle_message(message)
                
            if not self.is_cycle_btn_pressed and self.controller.read_cycle_btn():
                self.is_cycle_btn_pressed = True
                print("Press!")
                # (self.current_mode)(self.controller) # Current mode is a lambda of how to change the controller
                
                next(self.current_mode)(self.controller)
            elif self.is_cycle_btn_pressed and not self.controller.read_cycle_btn():
                self.is_cycle_btn_pressed = False
                print("Unpress!")

            self.sleep(0.05)

    def get_message(self):
        if self.msg_queue.qsize() > 0:
            return self.msg_queue.get()

    def handle_message(self, message):
        print("Message ", message)

        if isinstance(message, PulseMessage):
            print("Got pulse message!")
            self.controller.start_pulse(message.speed)
        elif isinstance(message, PauseMessage):
            print("Got pause message!")
            self.controller.stop_pulse()
        elif isinstance(message, ColorMessage):
            print("Got color message!")
            self.controller.stop_pulse()

            if message.a < 0:
                brightness = None
                print("Keep brightness! a: ", message.a)
            else:
                print("New brightness: ", message.a)
                brightness = message.a

            self.controller.set_color(message.r, message.g, message.b, brightness) # Convert from string to float (even though it is float in dataclass)
        elif isinstance(message, BrightnessMessage):
            print("Got brightness message!")
            self.controller.set_brightness(message.brightness)
        elif isinstance(message, StopMessage):
            print("Got stop message!")
            self.controller.stop_pulse()
            self.controller.set_color(0, 0, 0, 0)

            self.active = False

            self.msg_queue.close()
            self.msg_queue.unlink()

if __name__ == '__main__':
    controller = LEDController()
    controller.start_pulse(200)

