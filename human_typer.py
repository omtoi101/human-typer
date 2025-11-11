"""
Human-like Typing Script with GUI
Windows version with Tkinter interface and customizable settings
"""

import pyautogui
import keyboard
import time
import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os

# CRITICAL: Disable PyAutoGUI's built-in delays
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0


class HumanTyper:
    def __init__(self, text, wpm=50, typo_rate=0.05, use_direct_input=False):
        self.text = text
        self.wpm = wpm
        self.typo_rate = typo_rate
        self.should_stop = False
        self.is_paused = False
        self.use_direct_input = use_direct_input
        
        chars_per_minute = wpm * 5
        self.base_delay = 60 / chars_per_minute
        
    def get_random_delay(self):
        variation = random.uniform(0.6, 1.4)
        return self.base_delay * variation
    
    def add_thinking_pause(self):
        # Scale thinking pauses with WPM - faster typing = shorter pauses
        # Most pauses are short (0.05-0.2s), occasionally longer (up to 0.5s)
        if random.random() < 0.15:  # 15% chance of pause
            # 80% chance of short pause, 20% chance of longer pause
            if random.random() < 0.8:
                pause_duration = random.uniform(0.05, 0.2) * (50 / self.wpm)
            else:
                pause_duration = random.uniform(0.3, 0.5) * (50 / self.wpm)
            self.wait_with_pause_check(pause_duration)
    
    def wait_with_pause_check(self, duration):
        """Wait with ability to pause"""
        elapsed = 0
        step = 0.05
        while elapsed < duration:
            if self.should_stop:
                return
            while self.is_paused:
                time.sleep(0.1)
                if self.should_stop:
                    return
            time.sleep(step)
            elapsed += step
    
    def make_typo(self, char):
        qwerty = {
            'a': 'qwsz', 'b': 'vghn', 'c': 'xdfv', 'd': 'erfcsx', 'e': 'rwd',
            'f': 'rtgvcd', 'g': 'tyhbvf', 'h': 'yujnbg', 'i': 'uok', 'j': 'uikmnh',
            'k': 'iolmj', 'l': 'opk', 'm': 'njk', 'n': 'bhjm', 'o': 'ipkl',
            'p': 'ol', 'q': 'wa', 'r': 'etfd', 's': 'wedxza', 't': 'ryfg',
            'u': 'yihj', 'v': 'cfgb', 'w': 'qeas', 'x': 'zsdc', 'y': 'tugh',
            'z': 'asx'
        }
        
        char_lower = char.lower()
        if char_lower in qwerty:
            typo = random.choice(qwerty[char_lower])
            return typo.upper() if char.isupper() else typo
        return char
    
    def type_key(self, key):
        """Type a key using the selected method"""
        if self.use_direct_input:
            # Use keyboard library for direct input (faster)
            if key == 'backspace':
                keyboard.press_and_release('backspace')
            else:
                keyboard.write(key)
        else:
            # Use pyautogui (more compatible but slower)
            pyautogui.press(key)
    
    def type_with_corrections(self, char):
        if self.should_stop:
            return False
            
        if char.isalpha() and random.random() < self.typo_rate:
            # Make typo
            typo_char = self.make_typo(char)
            self.type_key(typo_char)
            self.wait_with_pause_check(self.get_random_delay())
            if self.should_stop:
                return False
            
            # Scale "realization" delay with WPM
            realization_delay = random.uniform(0.05, 0.15) * (50 / self.wpm)
            self.wait_with_pause_check(realization_delay)
            if self.should_stop:
                return False
            
            # Backspace
            self.type_key('backspace')
            self.wait_with_pause_check(self.get_random_delay())
            if self.should_stop:
                return False
            self.type_key(char)
        else:
            self.type_key(char)
        return True
    
    def stop(self):
        """Stop typing immediately"""
        self.should_stop = True
        self.is_paused = False
    
    def pause(self):
        """Pause typing"""
        self.is_paused = True
    
    def resume(self):
        """Resume typing"""
        self.is_paused = False
    
    def type_text(self, callback=None, countdown_callback=None):
        # Countdown with updates
        for i in range(3, 0, -1):
            if self.should_stop:
                return
            if countdown_callback:
                countdown_callback(i)
            time.sleep(1)
        
        if countdown_callback:
            countdown_callback(0)
        
        for i, char in enumerate(self.text):
            if self.should_stop:
                if callback:
                    callback(i, len(self.text), cancelled=True)
                return
            
            # Check for pause
            while self.is_paused:
                time.sleep(0.1)
                if self.should_stop:
                    if callback:
                        callback(i, len(self.text), cancelled=True)
                    return
            
            if char == ' ' or char in '.,!?;:':
                self.add_thinking_pause()
            
            if not self.type_with_corrections(char):
                if callback:
                    callback(i, len(self.text), cancelled=True)
                return
            
            self.wait_with_pause_check(self.get_random_delay())
            
            if callback and (i + 1) % 10 == 0:
                callback(i + 1, len(self.text))
        
        if callback:
            callback(len(self.text), len(self.text), done=True)


class TypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Human-like Typer")
        self.root.geometry("700x640")
        self.root.resizable(False, False)
        
        # Settings
        self.settings_file = "typer_settings.json"
        self.load_settings()
        
        # State
        self.enabled = False
        self.typing_in_progress = False
        self.is_paused = False
        self.hotkey_registered = False
        self.typer = None
        self.stay_on_top = False
        self.use_direct_input = False
        
        # Create UI
        self.create_widgets()
        self.register_hotkey()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_settings(self):
        """Load settings from file or use defaults"""
        default_settings = {
            'hotkey': 'f9',
            'wpm': 50,
            'typo_rate': 5.0
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except:
            return False
    
    def create_widgets(self):
        """Create the main UI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Human-like Typer", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Text input
        text_label = ttk.Label(main_frame, text="Text to Type:")
        text_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.text_input = scrolledtext.ScrolledText(main_frame, width=80, height=12,
                                                     wrap=tk.WORD, font=('Arial', 10))
        self.text_input.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        try:
            with open("prompt.txt", "r", encoding="utf-8") as f:
                self.text_input.insert('1.0', f.read())
        except FileNotFoundError:
            self.text_input.insert('1.0', "prompt.txt not found. Please create the file.")
        except Exception as e:
            self.text_input.insert('1.0', f"An error occurred while reading prompt.txt: {e}")
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Status: Disabled", 
                                       font=('Arial', 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.hotkey_label = ttk.Label(status_frame, 
                                       text=f"Hotkey: {self.settings['hotkey'].upper()}", 
                                       font=('Arial', 10))
        self.hotkey_label.grid(row=1, column=0, sticky=tk.W)
        
        self.progress_label = ttk.Label(status_frame, text="Ready", 
                                        font=('Arial', 9), foreground='gray')
        self.progress_label.grid(row=2, column=0, sticky=tk.W)
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # First row of buttons
        self.toggle_button = ttk.Button(button_frame, text="Enable", 
                                        command=self.toggle_enabled, width=12)
        self.toggle_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", 
                                       command=self.toggle_pause, width=12, state='disabled')
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                        command=self.cancel_typing, width=12, state='disabled')
        self.cancel_button.grid(row=0, column=2, padx=5)
        
        settings_button = ttk.Button(button_frame, text="Settings", 
                                     command=self.open_settings, width=12)
        settings_button.grid(row=0, column=3, padx=5)
        
        # Second row of buttons
        self.topmost_button = ttk.Button(button_frame, text="Stay On Top: OFF", 
                                         command=self.toggle_stay_on_top, width=15)
        self.topmost_button.grid(row=1, column=0, columnspan=1, padx=5, pady=(5, 0))

        self.copy_button = ttk.Button(button_frame, text="Copy Prompt",
                                      command=self.copy_to_clipboard, width=15)
        self.copy_button.grid(row=1, column=1, columnspan=2, padx=5, pady=(5, 0))
        
        # Direct input toggle (faster typing)
        self.direct_input_button = ttk.Button(button_frame, text="Direct Input: OFF", 
                                              command=self.toggle_direct_input, width=15)
        self.direct_input_button.grid(row=1, column=3, columnspan=1, padx=5, pady=(5, 0))
        
        # Info label
        info_text = f"Press {self.settings['hotkey'].upper()} to start/pause typing (3 second countdown to switch windows)"
        self.info_label = ttk.Label(main_frame, text=info_text, 
                                    font=('Arial', 9), foreground='blue')
        self.info_label.grid(row=5, column=0, columnspan=2)

    def copy_to_clipboard(self):
        """Copy the text from the text input to the clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text_input.get('1.0', tk.END))
        self.progress_label.config(text="Prompt copied to clipboard!", foreground='green')

    def toggle_stay_on_top(self):
        """Toggle the stay on top feature"""
        self.stay_on_top = not self.stay_on_top
        self.root.attributes('-topmost', self.stay_on_top)
        
        if self.stay_on_top:
            self.topmost_button.config(text="Stay On Top: ON")
        else:
            self.topmost_button.config(text="Stay On Top: OFF")
    
    def toggle_direct_input(self):
        """Toggle direct input mode"""
        self.use_direct_input = not self.use_direct_input
        
        if self.use_direct_input:
            self.direct_input_button.config(text="Direct Input: ON")
        else:
            self.direct_input_button.config(text="Direct Input: OFF")
    
    def toggle_enabled(self):
        """Toggle the enabled state"""
        self.enabled = not self.enabled
        
        if self.enabled:
            self.toggle_button.config(text="Disable")
            self.status_label.config(text="Status: Enabled ✓", foreground='green')
            self.update_info_label()
        else:
            self.toggle_button.config(text="Enable")
            self.status_label.config(text="Status: Disabled", foreground='red')
            self.progress_label.config(text="Ready")
            # Cancel any ongoing typing
            if self.typing_in_progress:
                self.cancel_typing()
    
    def toggle_pause(self):
        """Toggle pause state"""
        if not self.typing_in_progress or not self.typer:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.typer.pause()
            self.pause_button.config(text="Resume")
            self.progress_label.config(text="PAUSED", foreground='orange')
        else:
            self.typer.resume()
            self.pause_button.config(text="Pause")
            # Progress will be updated by typing thread
    
    def cancel_typing(self):
        """Cancel the current typing operation"""
        if self.typer:
            self.typer.stop()
        self.typing_in_progress = False
        self.is_paused = False
        self.pause_button.config(state='disabled', text="Pause")
        self.cancel_button.config(state='disabled')
        self.progress_label.config(text="Cancelled", foreground='red')
    
    def update_info_label(self):
        """Update the info label with current hotkey"""
        info_text = f"Press {self.settings['hotkey'].upper()} to start/pause typing (3 second countdown to switch windows)"
        self.info_label.config(text=info_text)
    
    def register_hotkey(self):
        """Register the hotkey"""
        if self.hotkey_registered:
            keyboard.remove_hotkey(self.settings['hotkey'])
        
        try:
            keyboard.add_hotkey(self.settings['hotkey'], self.on_hotkey_pressed)
            self.hotkey_registered = True
            self.hotkey_label.config(text=f"Hotkey: {self.settings['hotkey'].upper()}")
        except:
            messagebox.showerror("Error", f"Could not register hotkey: {self.settings['hotkey']}")
    
    def on_hotkey_pressed(self):
        """Called when hotkey is pressed"""
        if not self.enabled:
            return
        
        # If typing is in progress, toggle pause
        if self.typing_in_progress:
            self.toggle_pause()
            return
        
        # Start new typing session
        text = self.text_input.get('1.0', tk.END).strip()
        if not text:
            return
        
        self.typing_in_progress = True
        self.is_paused = False
        self.pause_button.config(state='normal', text="Pause")
        self.cancel_button.config(state='normal')
        
        # Run typing in separate thread
        thread = threading.Thread(target=self.type_text_thread, args=(text,))
        thread.daemon = True
        thread.start()
    
    def type_text_thread(self, text):
        """Thread function to type text"""
        self.typer = HumanTyper(text, 
                               wpm=self.settings['wpm'], 
                               typo_rate=self.settings['typo_rate'] / 100.0,
                               use_direct_input=self.use_direct_input)
        self.typer.type_text(
            callback=self.update_progress,
            countdown_callback=self.update_countdown
        )
        
        self.typing_in_progress = False
        self.is_paused = False
        self.root.after(0, lambda: self.pause_button.config(state='disabled', text="Pause"))
        self.root.after(0, lambda: self.cancel_button.config(state='disabled'))
    
    def update_countdown(self, seconds):
        """Update countdown display"""
        if seconds > 0:
            self.progress_label.config(text=f"Starting in {seconds}...", foreground='orange')
        else:
            self.progress_label.config(text="Typing...", foreground='blue')
    
    def update_progress(self, current, total, done=False, cancelled=False):
        """Update progress label"""
        if cancelled:
            self.progress_label.config(text="Cancelled", foreground='red')
        elif done:
            self.progress_label.config(text="Typing complete!", foreground='green')
        else:
            if not self.is_paused:
                self.progress_label.config(text=f"Typing: {current}/{total} characters", 
                                          foreground='blue')
    
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Hotkey setting
        ttk.Label(frame, text="Hotkey:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        hotkey_frame = ttk.Frame(frame)
        hotkey_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        hotkey_var = tk.StringVar(value=self.settings['hotkey'])
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=hotkey_var, width=20)
        hotkey_entry.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(hotkey_frame, text="(e.g., f9, ctrl+shift+t, f8)", 
                 foreground='gray').grid(row=0, column=1)
        
        # WPM setting
        ttk.Label(frame, text="Typing Speed (WPM):", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        wpm_frame = ttk.Frame(frame)
        wpm_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        wpm_var = tk.IntVar(value=self.settings['wpm'])
        wpm_spinbox = ttk.Spinbox(wpm_frame, from_=10, to=150, textvariable=wpm_var, width=10)
        wpm_spinbox.grid(row=0, column=0, padx=(0, 10))
        
        wpm_label = ttk.Label(wpm_frame, text=f"{self.settings['wpm']} words/minute")
        wpm_label.grid(row=0, column=1)
        
        def update_wpm_label(*args):
            wpm_label.config(text=f"{wpm_var.get()} words/minute")
        wpm_var.trace('w', update_wpm_label)
        
        # Typo rate setting
        ttk.Label(frame, text="Typo Frequency (%):", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        typo_frame = ttk.Frame(frame)
        typo_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        typo_var = tk.DoubleVar(value=self.settings['typo_rate'])
        typo_scale = ttk.Scale(typo_frame, from_=0, to=20, variable=typo_var, 
                              orient=tk.HORIZONTAL, length=200)
        typo_scale.grid(row=0, column=0, padx=(0, 10))
        
        typo_label = ttk.Label(typo_frame, text=f"{self.settings['typo_rate']:.1f}%")
        typo_label.grid(row=0, column=1)
        
        def update_typo_label(*args):
            typo_label.config(text=f"{typo_var.get():.1f}%")
        typo_var.trace('w', update_typo_label)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, pady=(20, 0))
        
        def save_settings():
            old_hotkey = self.settings['hotkey']
            self.settings['hotkey'] = hotkey_var.get().lower()
            self.settings['wpm'] = wpm_var.get()
            self.settings['typo_rate'] = typo_var.get()
            
            if self.save_settings():
                if old_hotkey != self.settings['hotkey']:
                    self.register_hotkey()
                self.update_info_label()
                messagebox.showinfo("Settings", "Settings saved successfully!", parent=settings_window)
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings!", parent=settings_window)
        
        ttk.Button(button_frame, text="Save", command=save_settings, width=12).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy, width=12).grid(row=0, column=1, padx=5)
    
    def on_closing(self):
        """Handle window close"""
        if self.typer:
            self.typer.stop()
        if self.hotkey_registered:
            keyboard.unhook_all()
        self.root.destroy()


def main():
    """Main function"""
    try:
        import pyautogui
        import keyboard
    except ImportError:
        print("Required libraries not found!")
        print("Please install them with:")
        print("  pip install pyautogui keyboard")
        return
    
    root = tk.Tk()
    app = TypingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()