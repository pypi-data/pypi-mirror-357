import json
import os
import stat
import shutil
import argparse
import pkg_resources
from datetime import datetime
from .templates import generate_single_execution_script, generate_loop_execution_script
from .utils import Logger, get_config_dir, get_data_dir

class ActionGenerator:
    def __init__(self, input_file=None, history_dir=None, macros_dir=None, 
                default_trigger_key="f10", default_pause_key="f8"):
        if history_dir:
            self.history_dir = os.path.expanduser(history_dir)
            if not os.path.isabs(self.history_dir):
                self.history_dir = os.path.join(get_data_dir(), history_dir)
        else:
            self.history_dir = os.path.join(get_data_dir(), "history")
        
        if macros_dir:
            self.macros_dir = os.path.expanduser(macros_dir)
            if not os.path.isabs(self.macros_dir):
                self.macros_dir = os.path.join(get_data_dir(), macros_dir)
        else:
            self.macros_dir = os.path.join(get_data_dir(), "macros")
        
        for directory in [self.history_dir, self.macros_dir]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    Logger.success(f"Created directory: {directory}")
                except Exception as e:
                    Logger.warning(f"Warning: Could not create directory {directory}: {e}")
        
        if input_file is None:
            self.prompt_for_input_file()
        else:
            if os.path.dirname(input_file) == '':
                self.input_file = os.path.join(self.history_dir, input_file)
            else:
                self.input_file = input_file
            
        self.actions = []
        self.trigger_key = default_trigger_key
        self.loop_trigger_key = default_trigger_key
        self.pause_key = default_pause_key
        self.output_filename = ""
        self.input_basename = os.path.splitext(os.path.basename(self.input_file))[0]
        
        Logger.info(f"Action Generator initialized with file: {self.input_file}")
    
    def prompt_for_input_file(self):
        print("\n=== INPUT FILE SELECTION ===")
        print(f"Looking for recorded actions in: {self.history_dir}")
        
        try:
            json_files = [f for f in os.listdir(self.history_dir) if f.endswith('.json')]
        except:
            json_files = []
        
        if json_files:
            Logger.info("Available recorded actions:")
            for i, file in enumerate(json_files, 1):
                file_path = os.path.join(self.history_dir, file)
                file_size = os.path.getsize(file_path) / 1024  # size in KB
                mod_timestamp = os.path.getmtime(file_path)
                modify_time = datetime.fromtimestamp(mod_timestamp).strftime('%Y-%m-%d %H:%M')
                
                date_info = ""
                if "recording_" in file and "_" in file:
                    try:
                        date_part = file.split("recording_")[1].split(".json")[0]
                        if "-" in date_part:
                            date_info = f"(Recorded: {date_part}) "
                    except:
                        pass
                
                print(f"{i}. {file} {date_info}({file_size:.1f} KB, modified: {modify_time})")
            
            while True:
                choice = input(f"Enter file number, or full path to a JSON file: ").strip()
                
                if choice.isdigit() and 1 <= int(choice) <= len(json_files):
                    self.input_file = os.path.join(self.history_dir, json_files[int(choice) - 1])
                    break
                elif choice and os.path.isfile(choice):
                    self.input_file = choice
                    break
                elif choice and choice.endswith('.json'):
                    potential_path = os.path.join(self.history_dir, choice)
                    if os.path.isfile(potential_path):
                        self.input_file = potential_path
                        break
                    else:
                        Logger.error(f"File not found: {potential_path}")
                else:
                    Logger.info("Invalid selection. Please try again.")
        else:
            Logger.error(f"No JSON files found in {self.history_dir}.")
            fallback = input("Enter full path to JSON file or press Enter to use default: ").strip()
            if fallback:
                self.input_file = fallback
            else:
                self.input_file = os.path.join(self.history_dir, "recording.json")
                Logger.info(f"Using default: {self.input_file}")
    
    def load_actions(self):
        try:
            with open(self.input_file, 'r') as f:
                data = json.load(f)
                self.actions = data.get('actions', [])
                Logger.success(f"Loaded {len(self.actions)} actions from {self.input_file}")
                return True
        except FileNotFoundError:
            Logger.error(f"Error: File {self.input_file} not found!")
            return False
        except json.JSONDecodeError:
            Logger.error(f"Error: Invalid JSON in {self.input_file}")
            return False
        except Exception as e:
            Logger.error(f"Error loading file: {e}")
            return False
    
    def set_configuration(self):
        print("\n=== ACTION GENERATOR CONFIGURATION ===")

        trigger_key = input(f"Enter trigger key for single execution (default: {self.trigger_key}): ").strip()
        if trigger_key:
            self.trigger_key = trigger_key.lower()
        
        loop_trigger_key = input(f"Enter trigger key for loop mode (default: {self.loop_trigger_key}): ").strip()
        if loop_trigger_key:
            self.loop_trigger_key = loop_trigger_key.lower()
        
        pause_key = input(f"Enter key to pause/resume execution (default: {self.pause_key}): ").strip()
        if pause_key:
            self.pause_key = pause_key.lower()
        
        if self.trigger_key == self.pause_key:
            Logger.warning("\n WARNING: You've set the same key for both trigger and pause!")
            Logger.warning("This might cause unexpected behavior.")
            change = input("Would you like to change one of them? (y/n): ").strip().lower()
            if change == 'y':
                self.set_configuration() 
                return
        
        if self.loop_trigger_key == self.pause_key:
            Logger.warning("\n WARNING: You've set the same key for both loop trigger and pause!")
            Logger.warning("This might cause unexpected behavior.")
            change = input("Would you like to change one of them? (y/n): ").strip().lower()
            if change == 'y':
                self.set_configuration()
                return
        
        Logger.success(f"\nConfiguration set:")
        Logger.info(f"- Single execution trigger: {self.trigger_key}")
        Logger.info(f"- Loop mode trigger: {self.loop_trigger_key}")
        Logger.info(f"- Pause/resume key: {self.pause_key}")
    
    def choose_execution_mode(self):
        print("\n=== EXECUTION MODE SELECTION ===")
        print("1. Single Execution - Execute actions once per key press")
        print("2. Loop Execution - Toggle continuous loop on/off")
        
        while True:
            choice = input("Choose execution mode (1 or 2): ").strip()
            if choice == "1":
                return "single"
            elif choice == "2":
                return "loop"
            else:
                Logger.info("Invalid choice. Please enter 1 or 2.")
    
    def get_output_filename(self, mode):
        input_base = self.input_basename
        if mode == "single":
            default_filename = f"singlemacro_{input_base}.py"
        else:
            default_filename = f"loopmacro_{input_base}.py"
        default_path = os.path.join(self.macros_dir, default_filename)
        print("\n=== OUTPUT FILE SETUP ===")
        Logger.info(f"Macro scripts will be saved to: {self.macros_dir}")
        filename = input(f"Enter output script filename (default: {default_filename}): ").strip()
        if not filename:
            return default_path
        if not filename.endswith('.py'):
            filename += '.py'
        if os.path.dirname(filename) == '':
            return os.path.join(self.macros_dir, filename)
        else:
            return filename
    
    def generate_main_script(self, mode):
        self.output_filename = self.get_output_filename(mode)
        output_dir = os.path.dirname(self.output_filename)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                Logger.success(f"Created directory: {output_dir}")
            except Exception as e:
                Logger.warning(f"Warning: Could not create directory {output_dir}: {e}")
                self.output_filename = os.path.join(self.macros_dir, os.path.basename(self.output_filename))
        if mode == "single":
            script_content = generate_single_execution_script(
                "replay_actions", 
                self.trigger_key, 
                self.actions,
                self.pause_key
            )
        else:
            script_content = generate_loop_execution_script(
                "replay_actions", 
                self.loop_trigger_key, 
                self.actions,
                self.pause_key
            )

        try:
            with open(self.output_filename, 'w', encoding='utf-8') as f:
                f.write(script_content)
            try:
                os.chmod(self.output_filename, os.stat(self.output_filename).st_mode | stat.S_IEXEC)
            except:
                pass
            
            Logger.success(f"\nGenerated {os.path.basename(self.output_filename)} successfully!")
            Logger.info(f"File location: {os.path.abspath(self.output_filename)}")
            
            if mode == "single":
                print(f"Usage: Run the script and press {self.trigger_key.upper()} to execute actions")
            else:
                print(f"Usage: Run the script and press {self.loop_trigger_key.upper()} to start/stop loop")
            
            print(f"Press {self.pause_key.upper()} to pause/resume execution")
            print("Press ESC to exit the script")
            print("\nNote: The macro-gen package must be installed to run this script.")
            
            return self.output_filename
            
        except Exception as e:
            Logger.error(f"Error writing script file: {e}")
            return None
    
    def run(self):
        print("\nACTION GENERATOR")
        print("=" * 50)
        if not self.load_actions():
            return
        
        if len(self.actions) == 0:
            Logger.info("No actions found in the file!")
            return
        self.set_configuration()
        mode = self.choose_execution_mode()
        generated_file = self.generate_main_script(mode)
        if generated_file:
            Logger.success("\nSetup complete! Your action replay script is ready to use.")
        else:
            Logger.error("\nFailed to generate script.")
