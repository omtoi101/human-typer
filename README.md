# Human-like Typer

A Python-based desktop application that simulates human typing with realistic variations in speed, thinking pauses, and occasional typos with automatic corrections.

## Features

- **Realistic Typing Simulation**: Varies typing speed (WPM) and adds random pauses to mimic human behavior.
- **Natural Typo Generation**: Occasionally makes mistakes and corrects them, just like a real person.
- **Graphical User Interface**: Easy-to-use Tkinter-based interface for managing text and settings.
- **Customizable Settings**:
  - Adjust typing speed (Words Per Minute).
  - Configure typo frequency percentage.
  - Set custom hotkeys to start/pause typing.
- **Flexible Typing Modes**:
  - **Standard Mode**: Uses PyAutoGUI for broad compatibility.
  - **Direct Input Mode**: Uses the `keyboard` library for faster, more direct input.
- **Stay On Top**: Option to keep the application window above others.
- **Safe Operation**: Includes a 3-second countdown after triggering to allow you to switch to the target window.

## Prerequisites

- Python 3.x
- Windows (Recommended, as it uses `keyboard` and `pyautogui` which work best on Windows for this purpose)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/human-typer.git
   cd human-typer
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python human_typer.py
   ```

## Building an Executable

You can package the application into a standalone executable using PyInstaller:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller human_typer.spec
   ```

The resulting executable will be in the `dist/` directory.

## Usage

2. **Prepare your text**: Enter or paste the text you want to type into the main text area.
3. **Configure Settings**: Click the "Settings" button to adjust WPM, typo rate, or change the start/pause hotkey.
4. **Enable the Typer**: Click the "Enable" button. This activates the hotkey.
5. **Start Typing**:
   - Switch to the application where you want the text to be typed (e.g., a text editor, browser, etc.).
   - Press the configured hotkey (default is **F9**).
   - There will be a 3-second countdown displayed in the "Human-like Typer" window before typing begins.
6. **Pause/Resume**: Press the hotkey again while typing is in progress to pause or resume.
7. **Cancel**: Click the "Cancel" button in the GUI to stop typing immediately.

## Configuration

Settings are automatically saved to `typer_settings.json`:

- `hotkey`: The key combination used to toggle typing (e.g., `f9`, `ctrl+shift+t`).
- `wpm`: Words Per Minute (default: 50).
- `typo_rate`: Frequency of mistakes in percentage (default: 5.0%).

## Files

- `human_typer.py`: The main application script.
- `typer_settings.json`: Stores your custom configuration.
- `prompt.txt`: A sample text file containing writing guidelines.
- `requirements.txt`: List of Python dependencies.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
