from dataclasses import dataclass
from ipcqueue import posixmq

led_msg_queue_path = "/led_msg"

def get_led_msg_queue():
    return posixmq.Queue(led_msg_queue_path)

@dataclass
class PulseMessage:
    speed: float = 200
    
@dataclass
class ColorMessage:
    r: float
    g: float
    b: float
    a: float

@dataclass
class BrightnessMessage:
    brightness: float

@dataclass
class PauseMessage:
    pause = True

@dataclass
class StopMessage:
    stop = True
