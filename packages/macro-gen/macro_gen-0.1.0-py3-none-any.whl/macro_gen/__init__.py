import os
import sys
import shutil
import pkg_resources

__version__ = "0.1.0"

def get_config_dir():
    config_home = os.environ.get('XDG_CONFIG_HOME')
    if not config_home:
        config_home = os.path.join(os.path.expanduser('~'), '.config')
    return os.path.join(config_home, 'macro-gen')

def get_data_dir():
    data_home = os.environ.get('XDG_DATA_HOME')
    if not data_home:
        data_home = os.path.join(os.path.expanduser('~'), '.local', 'share')
    return os.path.join(data_home, 'macro-gen')

def ensure_basic_dirs_and_config():
    try:
        config_dir = get_config_dir()
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        data_dir = get_data_dir()
        for subdir in ['macros', 'history']:
            full_path = os.path.join(data_dir, subdir)
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
                
        config_file = os.path.join(config_dir, "config.conf")
        if not os.path.exists(config_file):
            try:
                default_config = pkg_resources.resource_filename('macro_gen', 'macro_gen.conf')
                if os.path.exists(default_config):
                    shutil.copy2(default_config, config_file)
                    with open(config_file, 'r') as f:
                        content = f.read()
                    content = content.replace(
                        "history_dir = history", 
                        f"history_dir = {os.path.join(get_data_dir(), 'history')}"
                    )
                    content = content.replace(
                        "macros_dir = macros", 
                        f"macros_dir = {os.path.join(get_data_dir(), 'macros')}"
                    )
                    with open(config_file, 'w') as f:
                        f.write(content)
                else:
                    basic_config = f"""[recorder]
mouse_trps = 50

[playback]
default_trigger_key = f10
default_pause_key = f8

[paths]
history_dir = {os.path.join(get_data_dir(), 'history')}
macros_dir = {os.path.join(get_data_dir(), 'macros')}
"""
                    with open(config_file, 'w') as f:
                        f.write(basic_config)
            except Exception as e:
                pass
    except Exception as e:
        pass

ensure_basic_dirs_and_config()

from .main import main
from .utils import get_config_dir, get_data_dir
