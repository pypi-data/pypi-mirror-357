import time
import threading
from pynput import keyboard
from .utils import ActionPerformer, Logger

class SingleExecutionController:
    
    def __init__(self, actions, trigger_key="f10", pause_key="f8"):
        self.running = True
        self.executing = False
        self.paused = False
        self.pause_event = threading.Event()
        self.trigger_key = trigger_key.lower()
        self.pause_key = pause_key.lower()
        self.performer = ActionPerformer(actions)
        
        action_keys = set()
        for action in actions:
            if action["type"] in ("key_down", "key_up") and "key" in action:
                action_keys.add(action["key"].lower())
                
        for key_name, purpose in [(self.trigger_key, "trigger"), (self.pause_key, "pause")]:
            if key_name in action_keys:
                Logger.warning(f"The {purpose} key '{key_name}' is also used in your recorded actions.")
                Logger.warning(f"This might cause unexpected behavior during playback.")
                
        if self.trigger_key == self.pause_key:
            Logger.warning(f"You've set the same key for both trigger and pause functions.")
            Logger.warning(f"This might cause unexpected behavior during playback.")
        
        Logger.info("Single Execution Mode:")
        Logger.info(f"- Press {self.trigger_key.upper()} to execute actions")
        Logger.info(f"- Press {self.pause_key.upper()} to pause/resume execution")
        Logger.info(f"- Press ESC to quit")

    def run_actions(self):
        try:
            self.paused = False
            self.pause_event.clear()
            self.performer.perform(pause_event=self.pause_event)
        finally:
            self.executing = False

    def toggle_pause(self):
        if not self.executing:
            Logger.warning("Not currently executing actions.")
            return
            
        if self.paused:
            Logger.info("[+] Resuming execution...")
            self.paused = False
            self.pause_event.clear()
        else:
            Logger.info("[::] Pausing execution...")
            self.paused = True
            self.pause_event.set()

    def on_key_press(self, key):
        try:
            key_pressed = None
            if hasattr(key, 'char') and key.char:
                key_pressed = key.char.lower()
            elif hasattr(key, 'name'):
                key_pressed = key.name.lower()

            if key_pressed == self.trigger_key:
                if not self.executing:
                    Logger.info("[>] Executing actions...")
                    self.executing = True
                    threading.Thread(target=self.run_actions, daemon=True).start()
                else:
                    Logger.warning("Already executing actions. Please wait...")
            elif key_pressed == self.pause_key:
                self.toggle_pause()
            elif key == keyboard.Key.esc:
                Logger.info("Exiting...")
                self.running = False
                return False
        except Exception as e:
            Logger.error(f"Key press error: {e}")

    def run(self):
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()


class LoopExecutionController:
    
    def __init__(self, actions, loop_trigger_key="f10", pause_key="f8"):
        self.running = True
        self.loop_active = False
        self.paused = False
        self.loop_thread = None
        self.stop_event = None
        self.pause_event = None
        self.loop_lock = threading.Lock()
        self.loop_trigger_key = loop_trigger_key.lower()
        self.pause_key = pause_key.lower()
        self.performer = ActionPerformer(actions)
        
        action_keys = set()
        for action in actions:
            if action["type"] in ("key_down", "key_up") and "key" in action:
                action_keys.add(action["key"].lower())

        for key_name, purpose in [(self.loop_trigger_key, "loop trigger"), (self.pause_key, "pause")]:
            if key_name in action_keys:
                Logger.warning(f"The {purpose} key '{key_name}' is also used in your recorded actions.")
                Logger.warning(f"This might cause unexpected behavior during playback.")

        if self.loop_trigger_key == self.pause_key:
            Logger.warning(f"You've set the same key for both loop trigger and pause functions.")
            Logger.warning(f"This might cause unexpected behavior during playback.")

        Logger.info("Loop Execution Mode:")
        Logger.info(f"- Press {self.loop_trigger_key.upper()} to start/stop loop")
        Logger.info(f"- Press {self.pause_key.upper()} to pause/resume execution")
        Logger.info(f"- Press ESC to quit")

    def execute_loop(self):
        while self.loop_active and self.running:
            try:
                self.performer.perform(stop_event=self.stop_event, pause_event=self.pause_event)
                if self.loop_active and not self.stop_event.is_set():
                    Logger.info("Loop iteration completed, starting next...")
            except Exception as e:
                Logger.error(f"Error in loop execution: {e}")
                time.sleep(1)

    def toggle_loop(self):
        with self.loop_lock:
            if not self.loop_active:
                self.loop_active = True
                self.stop_event = threading.Event()
                self.pause_event = threading.Event()
                self.paused = False
                Logger.info("[>>] LOOP STARTED - Actions will repeat continuously")
                self.loop_thread = threading.Thread(target=self.execute_loop, daemon=True)
                self.loop_thread.start()
            else:
                Logger.info("Stopping loop...")
                self.loop_active = False
                if self.stop_event:
                    self.stop_event.set()  # Interrupt current action
                if self.loop_thread and self.loop_thread.is_alive():
                    self.loop_thread.join(timeout=2)
                Logger.info("[#] LOOP STOPPED")
    
    def toggle_pause(self):
        if not self.loop_active:
            Logger.warning("Loop not active.")
            return
            
        if self.paused:
            Logger.info("[+] Resuming loop execution...")
            self.paused = False
            if self.pause_event:
                self.pause_event.clear()
        else:
            Logger.info("[::] Pausing loop execution...")
            self.paused = True
            if self.pause_event:
                self.pause_event.set()

    def on_key_press(self, key):
        try:
            key_pressed = None
            if hasattr(key, 'char') and key.char:
                key_pressed = key.char.lower()
            elif hasattr(key, 'name'):
                key_pressed = key.name.lower()

            if key_pressed == self.loop_trigger_key:
                self.toggle_loop()
            elif key_pressed == self.pause_key:
                self.toggle_pause()
            elif key == keyboard.Key.esc:
                Logger.info("Exiting...")
                self.running = False
                self.loop_active = False
                if self.stop_event:
                    self.stop_event.set()
                if self.loop_thread and self.loop_thread.is_alive():
                    self.loop_thread.join(timeout=2)
                return False
        except Exception as e:
            Logger.error(f"Key press error: {e}")

    def run(self):
        try:
            with keyboard.Listener(on_press=self.on_key_press) as listener:
                listener.join()
        except KeyboardInterrupt:
            Logger.info("Program interrupted")
        finally:
            self.loop_active = False
            if self.stop_event:
                self.stop_event.set()
            if self.loop_thread and self.loop_thread.is_alive():
                self.loop_thread.join(timeout=2)