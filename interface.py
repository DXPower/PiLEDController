# from gpiozero.pins.pigpio import PiGPIOFactory
# from gpiozero import Device, PWMLED


import logging
import os
import sys
import time
from led_messages import *
from ipcqueue import posixmq 

from led_daemon import LED_Daemon
from led_colors import colors

from optparse import OptionParser
import inspect

if __name__ == '__main__':
    action = sys.argv[1]
    logfile = os.path.join(os.getcwd(), "sleepy.log")
    pidfile = os.path.join(os.getcwd(), "sleepy.pid")

    logging.basicConfig(filename=logfile, level=logging.DEBUG)

    msg_queue = get_led_msg_queue()

    if action == "start" or action == "on":
        dae = LED_Daemon(pidfile=pidfile)
        dae.start()
    elif action == "stop" or action == "off":
        msg_queue.put(StopMessage())

        # Wait for the daemon to gracefully shut its threads down
        while msg_queue.qsize() > 0:
            time.sleep(0.1)

        dae = LED_Daemon(pidfile=pidfile)
        dae.stop()

    elif action == "restart":
        dae = LED_Daemon(pidfile=pidfile)
        dae.restart()

    elif action == "pulse":
        msg_queue.put(PulseMessage(speed = 200))
    elif action == "pause":
        msg_queue.put(PauseMessage())
    elif action == "color":
        if sys.argv[2] in colors: # Check if the provided argument is the name of a color
            color = colors[sys.argv[2]]
            msg_queue.put(ColorMessage(color[0], color[1], color[2], -1))
        elif len(sys.argv) == 5:
            try:
                r = float(sys.argv[2])
                g = float(sys.argv[3])
                b = float(sys.argv[4])

                r = min(max(r, 0), 1)
                g = min(max(g, 0), 1)
                b = min(max(b, 0), 1)

                print("r, g, b:", r, g, b)

                msg_queue.put(ColorMessage(r, g, b, -1))
            except:
                print("Provided RGB values must be numbers between 0 and 1. For example, ledc 0 0.7 1")
        else:
            print("Invalid color. Must give either color name or 3-value RGB between 0 and 1. For example, ledc teal, or ledc 0 0.7 1")

    elif action == "brightness" or action == "alpha":
        try:
            brightness = float(sys.argv[2])

            if brightness < 0:
                brightness = 0
            elif brightness > 1:
                brightness = 1
            
            msg_queue.put(BrightnessMessage(brightness))
        except:
            print("Must provide brightness as number between 0 and 1. For example, for 70% brightness: ledb 0.7")

    # Shut down queue connection
    # Don't unlink the queue because the daemon will do that once it shuts down.
    msg_queue.close()
        