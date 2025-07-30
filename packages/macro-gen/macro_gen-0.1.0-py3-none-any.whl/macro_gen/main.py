#!/usr/bin/env python3
import argparse
import sys
import os
import configparser
import subprocess
from datetime import datetime
import pkg_resources
from .inputrecorder import InputRecorder
from .actiongenerator import ActionGenerator
from .utils import get_config_dir, get_data_dir, Logger

def load_config():
    config = {
        "mouse_trps": 50,
        "default_trigger_key": "f10",
        "default_pause_key": "f8",
        "history_dir": os.path.join(get_data_dir(), "history"),
        "macros_dir": os.path.join(get_data_dir(), "macros")
    }
    
    config_paths = [
        os.path.join(get_config_dir(), "config.conf"),  #XDG dir
        pkg_resources.resource_filename('macro_gen', 'macro_gen.conf')  #pkg default
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                parser = configparser.ConfigParser()
                parser.read(config_path)
                
                if 'recorder' in parser:
                    if 'mouse_trps' in parser['recorder']:
                        config['mouse_trps'] = parser.getint('recorder', 'mouse_trps')
                
                if 'playback' in parser:
                    if 'default_trigger_key' in parser['playback']:
                        config['default_trigger_key'] = parser['playback']['default_trigger_key']
                    if 'default_pause_key' in parser['playback']:
                        config['default_pause_key'] = parser['playback']['default_pause_key']
                        
                if 'paths' in parser:
                    if 'history_dir' in parser['paths']:
                        history_dir = parser['paths']['history_dir']
                        if not os.path.isabs(history_dir):
                            history_dir = os.path.join(get_data_dir(), history_dir)
                        config['history_dir'] = history_dir
                        
                    if 'macros_dir' in parser['paths']:
                        macros_dir = parser['paths']['macros_dir']
                        if not os.path.isabs(macros_dir):
                            macros_dir = os.path.join(get_data_dir(), macros_dir)
                        config['macros_dir'] = macros_dir
                        
                Logger.info(f"Loaded configuration from {config_path}")
                break  #use first valid config file
            except Exception as e:
                Logger.error(f"Error loading config file {config_path}: {e}")
    
    return config

def record_command(args, config):
    mouse_tracking_period = 1 / config['mouse_trps']
    
    recorder = InputRecorder(
        mouse_tracking_period=mouse_tracking_period,
        history_dir=config['history_dir']
    )
    recorder.run()

def generate_command(args, config):
    generator = ActionGenerator(
        input_file=args.file,
        history_dir=config['history_dir'],
        macros_dir=config['macros_dir'],
        default_trigger_key=config['default_trigger_key'],
        default_pause_key=config['default_pause_key']
    )
    generator.run()

def list_history_command(args, config):
    history_dir = os.path.join(get_data_dir(), "history")
    
    if not os.path.exists(history_dir):
        Logger.error(f"History directory does not exist: {history_dir}")
        return
    
    json_files = [f for f in os.listdir(history_dir) if f.endswith('.json')]
    
    if not json_files:
        Logger.info("No recordings found in history directory.")
        return
    
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(history_dir, x)), reverse=True)
    
    print("\nAvailable Recordings:")
    print(f"{'ID':<4} {'Recording Name':<40} {'Size':<10} {'Date':<20} {'Actions':<10}")
    print("-" * 84)
    
    for i, file in enumerate(json_files, 1):
        file_path = os.path.join(history_dir, file)
        file_size = os.path.getsize(file_path) / 1024  # size in KB
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')
        
        action_count = "Unknown"
        try:
            import json
            with open(file_path, 'r') as f:
                data = json.load(f)
                action_count = str(len(data.get('actions', [])))
        except:
            pass
            
        print(f"{i:<4} {file:<40} {file_size:.1f} KB   {mod_time:<20} {action_count:<10}")
        
    print(f"\nTotal recordings: {len(json_files)}")
    print(f"Location: {os.path.abspath(history_dir)}")

def list_macros_command(args, config):
    macros_dir = os.path.join(get_data_dir(), "macros")
    
    if not os.path.exists(macros_dir):
        Logger.error(f"Macros directory does not exist: {macros_dir}")
        return
    py_files = [f for f in os.listdir(macros_dir) if f.endswith('.py') and not f.startswith('__')]
    
    if not py_files:
        Logger.info("No macros found in macros directory.")
        return
    py_files.sort(key=lambda x: os.path.getmtime(os.path.join(macros_dir, x)), reverse=True)
    print("\nAvailable Macros:")
    print(f"{'ID':<4} {'Macro Name':<40} {'Size':<10} {'Date':<20} {'Type':<15}")
    print("-" * 89)
    
    for i, file in enumerate(py_files, 1):
        file_path = os.path.join(macros_dir, file)
        file_size = os.path.getsize(file_path) / 1024  # size in KB
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')
        
        macro_type = "Unknown"
        if "singlemacro" in file.lower():
            macro_type = "Single Execution"
        elif "loopmacro" in file.lower():
            macro_type = "Loop Execution"
        else:
            try:
                with open(file_path, 'r') as f:
                    content = f.read(500)
                    if "SingleExecution" in content:
                        macro_type = "Single Execution"
                    elif "LoopExecution" in content:
                        macro_type = "Loop Execution"
            except:
                pass
            
        print(f"{i:<4} {file:<40} {file_size:.1f} KB   {mod_time:<20} {macro_type:<15}")
        
    print(f"\nTotal macros: {len(py_files)}")
    print(f"Location: {os.path.abspath(macros_dir)}")
    print("To run a macro: macro-gen run MACRO_NAME")

def run_command(args, config):
    macro_name = args.macro
    macros_dir = os.path.join(get_data_dir(), "macros")
    
    if not macro_name.endswith('.py'):
        macro_name += '.py'
    
    macro_path = os.path.join(macros_dir, macro_name)
    if not os.path.exists(macro_path):
        available_macros = [f for f in os.listdir(macros_dir) if f.endswith('.py')]
        matches = [f for f in available_macros if macro_name.lower() in f.lower()]
        
        if matches:
            if len(matches) == 1:
                macro_path = os.path.join(macros_dir, matches[0])
                Logger.info(f"Found matching macro: {matches[0]}")
            else:
                Logger.error(f"Multiple matching macros found:")
                for match in matches:
                    Logger.info(f"  - {match}")
                Logger.info(f"Please specify the exact name.")
                return
        else:
            Logger.error(f"Macro file not found: {macro_name}")
            Logger.info(f"Use 'macro-gen list-macros' to see available macros.")
            return

    Logger.info(f"Running macro: {os.path.basename(macro_path)}")
    
    try:
        if not os.access(macro_path, os.X_OK):
            os.chmod(macro_path, os.stat(macro_path).st_mode | 0o755)
            
        subprocess.run(['python3', macro_path])
    except Exception as e:
        Logger.error(f"Error executing macro: {e}")

def rm_macro_command(args, config):
    macro_name = args.macro_name
    macros_dir = os.path.join(get_data_dir(), "macros")
    
    if not macro_name.endswith('.py'):
        macro_name += '.py'
    
    macro_path = os.path.join(macros_dir, macro_name)
    
    if not os.path.exists(macro_path):
        available_macros = [f for f in os.listdir(macros_dir) if f.endswith('.py')]
        matches = [f for f in available_macros if macro_name.lower().replace('.py', '') in f.lower()]
        if matches:
            if len(matches) == 1:
                macro_path = os.path.join(macros_dir, matches[0])
                macro_name = matches[0]
                Logger.info(f"Found matching macro: {matches[0]}")
            else:
                Logger.error("Multiple matching macros found:")
                for match in matches:
                    Logger.info(f"  - {match}")
                Logger.info("Please specify the exact macro name.")
                return
        else:
            Logger.error(f"Macro not found: {macro_name}")
            Logger.info("Use 'macro-gen list-macros' to see available macros.")
            return
    
    confirm = input(f"Are you sure you want to delete {macro_name}? (y/n): ").strip().lower()
    if confirm != 'y':
        Logger.info("Deletion cancelled.")
        return
    
    try:
        os.remove(macro_path)
        Logger.success(f"Successfully deleted macro: {macro_name}")
    except Exception as e:
        Logger.error(f"Error deleting macro: {e}")

def rm_recording_command(args, config):
    recording_name = args.recording_name
    history_dir = os.path.join(get_data_dir(), "history")
    
    if not recording_name.endswith('.json'):
        recording_name += '.json'
    
    recording_path = os.path.join(history_dir, recording_name)
    if not os.path.exists(recording_path):
        available_recordings = [f for f in os.listdir(history_dir) if f.endswith('.json')]
        matches = [f for f in available_recordings if recording_name.lower().replace('.json', '') in f.lower()]
        
        if matches:
            if len(matches) == 1:
                recording_path = os.path.join(history_dir, matches[0])
                recording_name = matches[0]
                Logger.info(f"Found matching recording: {matches[0]}")
            else:
                Logger.error("Multiple matching recordings found:")
                for match in matches:
                    Logger.info(f"  - {match}")
                Logger.info("Please specify the exact recording name.")
                return
        else:
            Logger.error(f"Recording not found: {recording_name}")
            Logger.info("Use 'macro-gen list-history' to see available recordings.")
            return
    confirm = input(f"Are you sure you want to delete {recording_name}? (y/n): ").strip().lower()
    if confirm != 'y':
        Logger.info("Deletion cancelled.")
        return
    try:
        os.remove(recording_path)
        Logger.success(f"Successfully deleted recording: {recording_name}")
    except Exception as e:
        Logger.error(f"Error deleting recording: {e}")

def main():
    config = load_config()
    parser = argparse.ArgumentParser(description='Record and replay mouse and keyboard actions')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    record_parser = subparsers.add_parser('record', help='Record mouse and keyboard actions')

    generate_parser = subparsers.add_parser('generate', help='Generate replay script from a recording')
    generate_parser.add_argument('file', nargs='?', help='Input JSON file with recorded actions')

    list_history_parser = subparsers.add_parser('list-history', help='List all recordings in history directory')

    list_macros_parser = subparsers.add_parser('list-macros', help='List all macros in macros directory')

    run_parser = subparsers.add_parser('run', help='Run a macro from the macros directory')
    run_parser.add_argument('macro', help='Name of the macro to run')

    rm_macro_parser = subparsers.add_parser('rm-macro', help='Remove a macro from the macros directory')
    rm_macro_parser.add_argument('macro_name', help='Name of the macro to remove')

    rm_recording_parser = subparsers.add_parser('rm-recording', help='Remove a recording from the history directory')
    rm_recording_parser.add_argument('recording_name', help='Name of the recording to remove')
    
    args = parser.parse_args()

    
    if args.command == 'record':
        record_command(args, config)
    elif args.command == 'generate':
        generate_command(args, config)
    elif args.command == 'list-history':
        list_history_command(args, config)
    elif args.command == 'list-macros':
        list_macros_command(args, config)
    elif args.command == 'run':
        run_command(args, config)
    elif args.command == 'rm-macro':
        rm_macro_command(args, config)
    elif args.command == 'rm-recording':
        rm_recording_command(args, config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()