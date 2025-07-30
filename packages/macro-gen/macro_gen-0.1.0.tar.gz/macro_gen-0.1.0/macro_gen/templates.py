from datetime import datetime
import os
from .utils import get_config_dir, get_data_dir

def generate_single_execution_script(function_name, trigger_key, actions, pause_key="f8"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return f'''#!/usr/bin/env python3
"""
Generated Action Replay Script - Single Execution Mode
Generated on: {timestamp}
Trigger Key: {trigger_key.upper()}
Pause Key: {pause_key.upper()}
Total Actions: {len(actions)}
"""

try:
    from macro_gen.executioncontroller import SingleExecutionController
    from macro_gen.utils import ActionPerformer, Logger
except ImportError:
    print("Error: Required modules not found.")
    print("Please install the macro-gen package with:")
    print("  pip install macro-gen")
    print("or run this script from the same directory as executioncontroller.py and utils.py")
    import sys
    sys.exit(1)

if __name__ == "__main__":
    controller = SingleExecutionController(
        actions={actions}, 
        trigger_key="{trigger_key}",
        pause_key="{pause_key}"
    )
    
    controller.run()
'''

def generate_loop_execution_script(function_name, loop_trigger_key, actions, pause_key="f8"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return f'''#!/usr/bin/env python3
"""
Generated Action Replay Script - Loop Execution Mode
Generated on: {timestamp}
Toggle Key: {loop_trigger_key.upper()}
Pause Key: {pause_key.upper()}
Total Actions: {len(actions)}
"""

try:
    from macro_gen.executioncontroller import LoopExecutionController
    from macro_gen.utils import ActionPerformer, Logger
except ImportError:
    print("Error: Required modules not found.")
    print("Please install the macro-gen package with:")
    print("  pip install macro-gen")
    print("or run this script from the same directory as executioncontroller.py and utils.py")
    import sys
    sys.exit(1)

if __name__ == "__main__":
    controller = LoopExecutionController(
        actions={actions}, 
        loop_trigger_key="{loop_trigger_key}",
        pause_key="{pause_key}"
    )
    
    controller.run()
'''
