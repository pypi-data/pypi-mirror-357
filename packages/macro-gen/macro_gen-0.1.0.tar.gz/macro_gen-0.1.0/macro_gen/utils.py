import time
import os
from pynput.keyboard import Key
from pynput.mouse import Button
from pynput import mouse, keyboard

def get_config_dir():
    """get config dir based on XDG std"""
    config_home = os.environ.get('XDG_CONFIG_HOME')
    if not config_home:
        config_home = os.path.join(os.path.expanduser('~'), '.config')
    return os.path.join(config_home, 'macro-gen')

def get_data_dir():
    """get data dir based on XDG std"""
    data_home = os.environ.get('XDG_DATA_HOME')
    if not data_home:
        data_home = os.path.join(os.path.expanduser('~'), '.local', 'share')
    return os.path.join(data_home, 'macro-gen')

def ensure_xdg_dirs_exist():
    """XDG dirs exist"""
    for directory in [
        get_config_dir(),
        os.path.join(get_data_dir(), "history"),
        os.path.join(get_data_dir(), "macros")
    ]:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception:
                pass

class Logger:

    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
    }
    
    @staticmethod
    def statement(message):
        print(f"{message}")
    
    @staticmethod
    def error(message):
        print(f"{Logger.COLORS['red']}[ERROR] {message}{Logger.COLORS['reset']}")
    
    @staticmethod
    def warning(message):
        print(f"{Logger.COLORS['yellow']}[WARNING] {message}{Logger.COLORS['reset']}")
    
    @staticmethod
    def success(message):
        print(f"{Logger.COLORS['green']}[SUCCESS] {message}{Logger.COLORS['reset']}")
    
    @staticmethod
    def info(message):
        print(f"[INFO] {message}")
    
    @staticmethod
    def debug(message):
        print(f"{Logger.COLORS['magenta']}[DEBUG] {message}{Logger.COLORS['reset']}")
    
    @staticmethod
    def record_status(message):
        print(f"{Logger.COLORS['cyan']}[RECORD] {message}{Logger.COLORS['reset']}")

def get_mouse_button(button_name):
    if button_name == "left":
        return Button.left
    elif button_name == "right":
        return Button.right
    elif button_name == "middle":
        return Button.middle
    else:
        try:
            if button_name.startswith("button_"):
                return Button.x1 if "4" in button_name else Button.x2
            return Button.left
        except:
            return Button.left

def get_keyboard_key(key_name):
    special_keys = {
        'space': Key.space, 'enter': Key.enter, 'tab': Key.tab,
        'shift': Key.shift, 'shift_l': Key.shift_l, 'shift_r': Key.shift_r,
        'ctrl': Key.ctrl, 'ctrl_l': Key.ctrl_l, 'ctrl_r': Key.ctrl_r,
        'alt': Key.alt, 'alt_l': Key.alt_l, 'alt_r': Key.alt_r,
        'cmd': Key.cmd, 'esc': Key.esc, 'backspace': Key.backspace,
        'delete': Key.delete, 'up': Key.up, 'down': Key.down,
        'left': Key.left, 'right': Key.right,
        'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
        'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
        'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12
    }
    return special_keys.get(key_name, key_name)

def smooth_mouse_move(mouse_controller, x, y, speed=743):
    import math
    start_x, start_y = mouse_controller.position
    distance = math.hypot(x - start_x, y - start_y)  # Euclidean distance
    density = 0.03
    steps = max(1, int(distance * density))
    duration = distance/speed

    for i in range(1, steps + 1):
        new_x = start_x + (x - start_x) * i / steps
        new_y = start_y + (y - start_y) * i / steps
        mouse_controller.position = (int(new_x), int(new_y))
        time.sleep(duration / steps)

class ActionPerformer:
    
    def __init__(self, actions):
        self.actions = actions
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
    
    def perform(self, stop_event=None, pause_event=None):
        for action in self.actions:
            if stop_event and stop_event.is_set():
                Logger.info("Action execution interrupted.")
                return
            
            if pause_event and pause_event.is_set():
                Logger.info("Execution paused. Waiting for resume...")
                while pause_event.is_set():
                    time.sleep(0.1)
                    if stop_event and stop_event.is_set():
                        Logger.info("Action execution interrupted while paused.")
                        return
                Logger.info("Execution resumed.")
            
            try:
                if action["type"] == "wait":
                    total_sleep = action["delta_t"] / 1000.0
                    interval = 0.05
                    slept = 0
                    while slept < total_sleep:
                        if stop_event and stop_event.is_set():
                            Logger.info("Wait interrupted.")
                            return
                        if pause_event and pause_event.is_set():
                            Logger.info("Wait paused.")
                            while pause_event.is_set():
                                time.sleep(0.1)
                                if stop_event and stop_event.is_set():
                                    Logger.info("Wait interrupted while paused.")
                                    return
                            Logger.info("Wait resumed.")

                        time.sleep(min(interval, total_sleep - slept))
                        slept += interval

                elif action["type"] == "mouse_move":
                    smooth_mouse_move(self.mouse_controller, action["x"], action["y"])

                elif action["type"] == "mouse_down":
                    smooth_mouse_move(self.mouse_controller, action["x"], action["y"])
                    button = get_mouse_button(action["button"])
                    self.mouse_controller.press(button)

                elif action["type"] == "mouse_up":
                    smooth_mouse_move(self.mouse_controller, action["x"], action["y"])
                    button = get_mouse_button(action["button"])
                    self.mouse_controller.release(button)

                elif action["type"] == "mouse_scroll":
                    smooth_mouse_move(self.mouse_controller, action["x"], action["y"])
                    self.mouse_controller.scroll(action["dx"], action["dy"])

                elif action["type"] == "key_down":
                    key = get_keyboard_key(action["key"])
                    self.keyboard_controller.press(key)

                elif action["type"] == "key_up":
                    key = get_keyboard_key(action["key"])
                    self.keyboard_controller.release(key)

            except Exception as e:
                Logger.error(f"Error executing action {action}: {e}")
                continue

        Logger.success("Action sequence completed!")