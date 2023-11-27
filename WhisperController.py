from pynput import mouse, keyboard
import threading
import pyperclip
import logging
from WhisperRecorder import WhisperRecorder
from WhisperUI import WhisperUI
import time
import sys
import json

class WhisperController:
    def __init__(self):     

        # Initialize UI with a reference to this controller and a callback for closing
        self.whisper_ui = WhisperUI(self.close_application, self)
        
        self.transcribed_text = "..."
        self.transcription_lock = threading.Lock()
        self.keyboard_controller = keyboard.Controller()

        # Initialize Recorder/Transcription
        self.recorder = WhisperRecorder(self.whisper_ui)
        
        # Start the mouse and keyboard listeners
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        # Keyboard listeners for closing
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.keyboard_listener.start()

        # Config key detection
        self.shortcut_detection_mode = None
        self.is_listening_for_shortcut = False

        # Initialize default values for shortcuts
        self.record_shortcut = {"type": "mouse", "key": "Button.x2"}
        self.paste_shortcut = {"type": "keyboard", "key": "v"}

        # Load the configuration
        self.load_configuration()


    def start_recording(self):
        if not self.recorder.is_recording:
        # Only start recording if it's not already happening
            with self.transcription_lock:
                try:
                    # Clear the previous transcribed text
                    self.transcribed_text = ""
                    # Start recording
                    self.transcribed_text = self.recorder.toggle_recording()
                    print("Recording started...")
                except Exception as e:
                    logging.error("Error starting recording: ", exc_info=e)

    def stop_recording_and_transcribe(self):
        if self.recorder.is_recording:
            # Only stop recording if it's currently active
            with self.transcription_lock:
                try:
                    # This will now also fetch the transcription
                    self.transcribed_text = self.recorder.toggle_recording()
                    logging.info("Transcribed text: %s", self.transcribed_text)
                    print("Recording stopped.")
                except Exception as e:
                    logging.error("Error stopping recording: ", exc_info=e)

    def perform_macro(self):
        # Retrieve text from the transcription box
        text = self.whisper_ui.transcription_box.get("1.0", "end-1c").strip()

        if self.transcription_lock.acquire(blocking=False):
            try:
                if not self.whisper_ui.chat_mode.get():
                    pyperclip.copy(text)
                    with self.keyboard_controller.pressed(keyboard.Key.ctrl):
                        self.keyboard_controller.press('v')
                        self.keyboard_controller.release('v')
                else:
                    # Non-admin mode
                    # Tap the 't' key first
                    self.keyboard_controller.tap(keyboard.KeyCode.from_char('t'))
                    time.sleep(0.1)  # Tiny pause

                    # Copy text to clipboard
                    pyperclip.copy(text)

                    # Paste using Ctrl+V
                    with self.keyboard_controller.pressed(keyboard.Key.ctrl):
                        self.keyboard_controller.press('v')
                        self.keyboard_controller.release('v')

                    time.sleep(0.1)  # Tiny pause
                    # Press Enter
                    self.keyboard_controller.tap(keyboard.Key.enter)
            finally:
                self.transcription_lock.release()
        else:
            logging.info("Transcription still in progress...")

    
    def on_click(self, x, y, button, pressed):
        if self.is_listening_for_shortcut and self.shortcut_detection_mode:
            if pressed:
                self.set_shortcut(button, self.shortcut_detection_mode)
            return  # Skip the normal logic when in shortcut detection mode
        if button == mouse.Button.x2:
            if pressed:
                threading.Thread(target=self.start_recording).start()
            else:
                threading.Thread(target=self.stop_recording_and_transcribe).start()
        elif button == mouse.Button.x1 and not pressed and self.transcribed_text:
            logging.info("Running Pasting macro text: %s", self.transcribed_text)
            self.perform_macro()
            
    
    def on_press(self, key):
        if key == keyboard.Key.esc:
            print("Exiting...")
            # Initiate the UI close
            self.whisper_ui.root.destroy()
            return False  # This will stop the listener
        if self.is_listening_for_shortcut and self.shortcut_detection_mode:
            self.set_shortcut(key, self.shortcut_detection_mode)
            self.stop_listening_for_shortcut()  # Stop listening after capturing the shortcut
            return  # Skip the normal logic when in shortcut detection mode
        else:
            self.trigger_recording_if_shortcut_matches(key)

    def set_shortcut(self, input, mode):
        # Determine the type of the input
        if isinstance(input, mouse.Button):
            input_type = "mouse"
            shortcut_key = input.name  # Get just the button name (e.g., 'x2', 'left', etc.)
        elif isinstance(input, keyboard.Key) or isinstance(input, keyboard.KeyCode):
            input_type = "keyboard"
            shortcut_key = str(input)  # Convert to string if necessary
        else:
            # Handle unexpected input type
            input_type = "unknown"
            shortcut_key = str(input)

        # Update the UI and save only the key
        shortcut_info = {"type": input_type, "key": shortcut_key}
        if mode == 'record':
            self.whisper_ui.set_record_shortcut(shortcut_info)
        elif mode == 'paste':
            self.whisper_ui.set_paste_shortcut(shortcut_info)

    def close_application(self):
        # Add cleanup code here
        print("Application closing...")
        self.recorder.terminate()  # Assuming terminate is a method to clean up the recorder
        self.mouse_listener.stop()  # Assuming you have a mouse listener to stop
        self.keyboard_listener.stop()  # Assuming you have a keyboard listener to stop
        self.whisper_ui.root.destroy()  # This will destroy the UI
        sys.exit()

    def run(self):
        try:
            self.whisper_ui.start()
        finally:
            self.recorder.terminate()
            self.mouse_listener.stop()
            self.keyboard_listener.stop()

    def load_configuration(self):
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                self.record_shortcut = config.get('record_shortcut', {"type": "mouse", "key": "Button.x2"})
                self.paste_shortcut = config.get('paste_shortcut', {"type": "keyboard", "key": "v"})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading configuration: {e}")
            # Set default values if configuration loading fails
            self.record_shortcut = {"type": "mouse", "key": "Button.x2"}
            self.paste_shortcut = {"type": "keyboard", "key": "v"}
    
    def start_listening_for_shortcut(self):
        self.is_listening_for_shortcut = True

    def stop_listening_for_shortcut(self):
        self.is_listening_for_shortcut = False
    
    def trigger_recording_if_shortcut_matches(self, key):
        # Load or keep track of the configured record shortcut
        record_shortcut = self.record_shortcut
        if record_shortcut['type'] == 'keyboard' and record_shortcut['key'] == str(key):
            if self.recorder.is_recording:
                # Stop recording if it's currently active
                self.stop_recording_and_transcribe()
            else:
                # Start recording if it's not currently active
                self.start_recording()

    def update_shortcuts_from_config(self):
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                self.record_shortcut = config.get('record_shortcut', {"type": "mouse", "key": "Button.x2"})
                self.paste_shortcut = config.get('paste_shortcut', {"type": "keyboard", "key": "v"})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error updating configuration: {e}")

    def update_model_in_recorder(self):
        selected_model = self.whisper_ui.model_combobox.get()
        self.recorder.update_model(selected_model)
