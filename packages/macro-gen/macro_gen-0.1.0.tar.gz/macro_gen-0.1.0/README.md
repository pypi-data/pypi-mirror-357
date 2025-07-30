# Macro Generator

A tool for recording and replaying mouse and keyboard actions.

## Features

- Record mouse movements, clicks, and keyboard inputs
- Pause and resume recording
- Generate macros to replay recorded actions
- Single execution mode (triggered by keypress)
- Loop execution mode (continuous replay)
- Pause/resume during playback
- Manage recordings and macros (list, run, remove)

## Installation

### From source

1. Clone the repository:
   ```bash
   git clone https://github.com/0xTristo/macro-gen.git
   cd macro-gen
   ```

2. Install with pip:
   ```bash
   pip install .
   ```

3. System-wide installation (requires root privileges):
   ```bash
   sudo pip install .
   ```

### Dependencies

Macro-Gen requires the following Python packages that will be automatically installed:
- pynput: For capturing and simulating keyboard and mouse inputs
- configparser: For reading configuration files

### System Requirements

- Python 3.6 or higher
- X Window System (on Linux) for mouse and keyboard control
- Administrator privileges may be required on Windows
- For Mac, accessibility permissions will need to be granted

## Quick Start

### Recording

To start recording mouse and keyboard actions:

```bash
macro-gen record
```

Controls:
- **F9**: Start/stop recording
- **F8**: Pause/resume recording
- **ESC**: Exit program

### Generating Replay Script

To generate a replay script from a recording:

```bash
macro-gen generate
```

You'll be prompted to select a recording file, choose execution mode, and configure trigger keys.

### Managing Recordings and Macros

List all recorded action files:
```bash
macro-gen list-history
```

List all generated macro scripts:
```bash
macro-gen list-macros
```

Run a specific macro:
```bash
macro-gen run macro_name
```

Remove a specific macro:
```bash
macro-gen rm-macro macro_name
```

Remove a specific recording:
```bash
macro-gen rm-recording recording_name
```

### File Locations

- Configuration: `~/.config/macro-gen/config.conf`
- Macros: `~/.local/share/macro-gen/macros/`
- Recordings: `~/.local/share/macro-gen/history/`

### Example Configuration File

```ini
[recorder]
mouse_trps = 50

[playback]
default_trigger_key = f10
default_pause_key = f8

[paths]
history_dir = history
macros_dir = macros
```

## License

MIT
