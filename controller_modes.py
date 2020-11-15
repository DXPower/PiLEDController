from led_colors import *

def stop_pulse_set_color(controller, color):
    print("Stopping pulse!")
    controller.stop_pulse()
    controller.set_color(color[0], color[1], color[2])

def controller_mode():
    mode_action = 0 # Mode action will become a lambda
    color_pos = 0
    clist = list(colors.values())
    do_pulse = False

    while True:
        if color_pos < len(clist):
            c = clist[color_pos]

            # Create a lambda to set the color controller of the controller
            if color_pos == 0: # If this is right after pulsing we need to turn that off
                mode_action = lambda controller: stop_pulse_set_color(controller, c)
            else:
                mode_action = lambda controller: controller.set_color(c[0], c[1], c[2])

            color_pos += 1
        else:
            color_pos = 0
            mode_action = lambda controller: controller.start_pulse() # Create a lambda to start pulsing

        yield mode_action