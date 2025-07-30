import json
import time
import threading
import argparse
from datetime import datetime
import os
import pkg_resources
from pynput import mouse, keyboard
from pynput.mouse import Button
from .utils import get_mouse_button, Logger, get_config_dir, get_data_dir

class InputRecorder:
    def __init__(self, mouse_tracking_period=0.1, output_file=None, history_dir=None):
        self.mouse_tracking_period = mouse_tracking_period
        
        if history_dir:
            self.history_dir = os.path.expanduser(history_dir)
            if not os.path.isabs(self.history_dir):
                self.history_dir = os.path.join(get_data_dir(), history_dir)
        else:
            self.history_dir = os.path.join(get_data_dir(), "history")
        
        if not os.path.exists(self.history_dir):
            try:
                os.makedirs(self.history_dir)
                Logger.info(f"Created history directory: {self.history_dir}")
            except Exception as e:
                Logger.warning(f"Could not create history directory: {e}")
                self.history_dir = os.path.dirname(os.path.abspath(__file__))
        if output_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")
            self.output_file = os.path.join(self.history_dir, f"recording_{timestamp}.json")
        else:
            if os.path.dirname(output_file) == '':
                self.output_file = os.path.join(self.history_dir, output_file)
            else:
                self.output_file = output_file
        
        self.actions = []
        self.start_time = None
        self.last_action_time = None
        self.recording = False
        self.paused = False
        self.pause_start_time = None
        self.total_pause_time = 0 
        self.ready_for_new_recording = True 
        
        self.last_mouse_pos = None
        self.mouse_timer = None
        
        self.mouse_listener = None
        self.keyboard_listener = None
        self.control_listener = None
        
        self.mouse_controller = mouse.Controller()
        Logger.info(f"Input Recorder initialized:")
        Logger.info(f"- Mouse tracking period: {mouse_tracking_period}s")
        Logger.info(f"- Output file: {self.output_file}")
        print("Press F9 to start/stop recording, F8 to pause/resume, ESC to quit")
    
    def get_current_time_ms(self):
        if self.start_time is None:
            return 0
        return int(((time.time() - self.start_time) * 1000) - self.total_pause_time)
    
    def add_wait_if_needed(self):
        if self.paused:
            return
            
        current_time = time.time()
        if self.last_action_time is not None:
            delta_t = int((current_time - self.last_action_time) * 1000)
            if delta_t > 10:
                wait_action = {
                    "type": "wait",
                    "delta_t": delta_t
                }
                self.actions.append(wait_action)
        self.last_action_time = current_time
    
    def add_action(self, action):
        if not self.recording or self.paused:
            return
        self.add_wait_if_needed()

        self.actions.append(action)
    
    def track_mouse_position(self):
        if not self.recording or self.paused:
            return
            
        try:
            from pynput.mouse import Listener
            controller = self.mouse_controller
            current_pos = controller.position
            if self.last_mouse_pos != current_pos:
                action = {
                    "type": "mouse_move",
                    "x": int(current_pos[0]),
                    "y": int(current_pos[1])
                }
                self.add_action(action)
                self.last_mouse_pos = current_pos
        except Exception as e:
            Logger.error(f"Error tracking mouse: {e}")
        if self.recording and not self.paused:
            self.mouse_timer = threading.Timer(self.mouse_tracking_period, self.track_mouse_position)
            self.mouse_timer.start()
    
    def on_mouse_click(self, x, y, button, pressed):
        if not self.recording or self.paused:
            return
        button_name = "left"
        if button == Button.left:
            button_name = "left"
        elif button == Button.right:
            button_name = "right"
        elif button == Button.middle:
            button_name = "middle"
        else:
            try:
                if hasattr(button, 'name'):
                    button_name = button.name
                elif hasattr(button, 'value'):
                    button_name = f"button_{button.value}"
                else:
                    button_name = str(button)
            except:
                button_name = "unknown"
        
        action_type = "mouse_down" if pressed else "mouse_up"
        action = {
            "type": action_type,
            "x": self.mouse_controller.position[0],
            "y": self.mouse_controller.position[1],
            "button": button_name
        }
        self.add_action(action)
    
    def on_mouse_scroll(self, x, y, dx, dy):
        if not self.recording or self.paused:
            return
        action = {
            "type": "mouse_scroll",
            "x": int(x),
            "y": int(y),
            "dx": int(dx),
            "dy": int(dy)
        }
        self.add_action(action)
    
    def on_key_press(self, key):
        if not self.recording or self.paused:
            return
        try:
            key_name = key.char if hasattr(key, 'char') and key.char else str(key).replace('Key.', '')
        except AttributeError:
            key_name = str(key).replace('Key.', '')
        action = {
            "type": "key_down",
            "key": key_name
        }
        self.add_action(action)
    
    def on_key_release(self, key):
        if not self.recording or self.paused:
            return
            
        try:
            key_name = key.char if hasattr(key, 'char') and key.char else str(key).replace('Key.', '')
        except AttributeError:
            key_name = str(key).replace('Key.', '')
        action = {
            "type": "key_up",
            "key": key_name
        }
        self.add_action(action)
    
    def on_control_key(self, key):
        try:
            if key == keyboard.Key.f9:
                self.toggle_recording()
            elif key == keyboard.Key.f8:
                self.toggle_pause()
            elif key == keyboard.Key.esc:
                Logger.info("\nExiting...")
                self.stop_recording()
                return False
        except AttributeError:
            pass
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
            if self.ready_for_new_recording:
                self.prompt_for_filename()
    
    def toggle_pause(self):
        if not self.recording:
            Logger.warning("Recording not active. Cannot pause.")
            return
        if self.paused:
            if self.pause_start_time:
                pause_duration_ms = int((time.time() - self.pause_start_time) * 1000)
                self.total_pause_time += pause_duration_ms
            
            self.paused = False
            self.pause_start_time = None
            
            self.last_action_time = time.time()
            
            Logger.record_status("[+] RECORDING RESUMED")
            
            self.track_mouse_position()
            
            if not self.mouse_listener or not self.mouse_listener.is_alive():
                self.mouse_listener = mouse.Listener(
                    on_click=self.on_mouse_click,
                    on_scroll=self.on_mouse_scroll
                )
                self.mouse_listener.start()
                
            if not self.keyboard_listener or not self.keyboard_listener.is_alive():
                self.keyboard_listener = keyboard.Listener(
                    on_press=self.on_key_press,
                    on_release=self.on_key_release
                )
                self.keyboard_listener.start()
        else:
            self.paused = True
            self.pause_start_time = time.time()
            Logger.record_status("[::] RECORDING PAUSED (Press F8 to resume)")
            
            if self.mouse_timer:
                self.mouse_timer.cancel()
                self.mouse_timer = None
    
    def start_recording(self):
        self.recording = True
        self.paused = False
        self.start_time = time.time()
        self.pause_start_time = None
        self.total_pause_time = 0
        self.last_action_time = None
        self.actions = []
        
        Logger.record_status("[>] RECORDING STARTED at " + time.strftime('%H:%M:%S'))
        Logger.info("Tracking all mouse and keyboard inputs...")
        Logger.info("Press F8 to pause/resume recording")
        self.track_mouse_position()
        
        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
    
    def stop_recording(self):
        if not self.recording:
            return
            
        self.recording = False
        self.paused = False
        
        if self.mouse_timer:
            self.mouse_timer.cancel()
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        if self.actions:
            self.save_to_file()
            
            Logger.record_status("[#] RECORDING STOPPED")
            Logger.info(f"Recorded {len(self.actions)} actions")
            Logger.info(f"Saved to: {self.output_file}")
            
            # Set flag to indicate we can record again
            self.ready_for_new_recording = True
            Logger.info("Ready to record another macro. Please specify a new filename.")
        else:
            Logger.record_status("[#] RECORDING STOPPED (No actions recorded)")
            self.ready_for_new_recording = True
    
    def save_to_file(self):
        """Save recorded actions to JSON file"""
        data = {
            "recording_info": {
                "total_actions": len(self.actions),
                "duration_ms": self.get_current_time_ms(),
                "mouse_tracking_period": self.mouse_tracking_period,
                "recorded_at": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "actions": self.actions
        }
        
        try:
            with open(self.output_file, 'w') as f:
                json.dump(data, f, indent=2)
            Logger.success(f"Successfully saved {len(self.actions)} actions to {self.output_file}")
        except Exception as e:
            Logger.error(f"Error saving file: {e}")
    
    def run(self):
        self.prompt_for_filename()
        
        self.control_listener = keyboard.Listener(on_press=self.on_control_key)
        self.control_listener.start()
        
        try:
            Logger.info("\nMulti-recording session ready!")
            Logger.info("Controls:")
            Logger.info("- F9: Start/Stop recording")
            Logger.info("- F8: Pause/Resume recording")
            Logger.info("- ESC: Exit program")
            Logger.info("After each recording, you'll be prompted for a new filename.")
            Logger.info(f"Current recording will be saved to: {self.output_file}")
            
            self.control_listener.join()
            
        except KeyboardInterrupt:
            Logger.warning("\nProgram interrupted")
        finally:
            self.stop_recording()
            if self.control_listener and self.control_listener.is_alive():
                self.control_listener.stop()
    
    def prompt_for_filename(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")
        default_filename = f"recording_{timestamp}.json"
        default_file = os.path.join(self.history_dir, default_filename)
        
        Logger.info("\n=== OUTPUT FILE SETUP ===")
        Logger.info(f"Files will be saved to: {self.history_dir}")
        try:
            existing_files = [f for f in os.listdir(self.history_dir) if f.endswith('.json')]
            if existing_files:
                Logger.info("\nExisting recordings:")
                for i, file in enumerate(existing_files[-5:], 1):  # Show last 5 files
                    Logger.info(f"  {i}. {file}")
                if len(existing_files) > 5:
                    Logger.info(f"  ... and {len(existing_files) - 5} more")
        except:
            pass
        Logger.info(f"\nDefault filename includes date and time: {default_filename}")
        custom_file = input(f"Enter output file name (default: {default_filename}): ").strip()
        
        if custom_file:
            if not custom_file.endswith('.json'):
                custom_file += '.json'
            self.output_file = os.path.join(self.history_dir, custom_file)
        else:
            self.output_file = default_file

        if os.path.exists(self.output_file):
            confirm = input(f"File {os.path.basename(self.output_file)} already exists. Overwrite? (y/n): ").strip().lower()
            if confirm != 'y':
                return self.prompt_for_filename()
        output_dir = os.path.dirname(self.output_file)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                Logger.info(f"Created directory: {output_dir}")
            except Exception as e:
                Logger.warning(f"Warning: Could not create directory {output_dir}: {e}")
                self.output_file = os.path.join(self.history_dir, os.path.basename(self.output_file))
                
        Logger.info(f"Next recording will be saved to: {os.path.abspath(self.output_file)}")
        Logger.info("Press F9 to start recording.")
        
        self.actions = []
        self.start_time = None
        self.last_action_time = None
        self.recording = False
        self.paused = False
        self.pause_start_time = None
        self.total_pause_time = 0
        self.last_mouse_pos = None