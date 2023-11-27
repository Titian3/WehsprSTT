import threading
import wave
import pyaudio
import whisper
import os
import logging
import time
import json
from pynput import keyboard

class WhisperRecorder:
    def __init__(self, ui, keyboard_controller, model_name="tiny"):
        # Transcription Config
        self.ui = ui
        self.keyboard_controller = keyboard_controller
        self.is_recording = False
        self.stream = None
        self.audio_frames = []
        self.model = whisper.load_model(model_name)
        self.audio = pyaudio.PyAudio()
        self.temp_wav_file = "recording.wav"

        # Audio recording config
        self.chunk_size = 4096
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 16000

        # Recording history
        self.recordings_history = []
        self.max_history_size = 3
        self.recordings_folder = "recordings"
        self.ensure_recordings_folder()

        # Model config
        self.model_name = model_name
        self.model = whisper.load_model(self.model_name)

        self.load_model_from_config()

        logging.info("Whisper model loaded")

    def start_recording(self):
        logging.info('Recording started...')
        self.stream = self.audio.open(format=self.audio_format, channels=self.channels, rate=self.sample_rate, input=True, frames_per_buffer=self.chunk_size)
        self.is_recording = True
        self.audio_frames = []

        # Start a separate thread for simulating keystrokes
        self.keystroke_thread = threading.Thread(target=self.simulate_keystrokes)
        self.keystroke_thread.start()

        while self.is_recording:
            data = self.stream.read(self.chunk_size)
            self.audio_frames.append(data)

    def stop_recording_and_transcribe(self):
        logging.info('Halting Recording...')
        self.ui.change_state_indicator("yellow", text="Recording Ending")
        
        # Close the stream
        logging.info('Close Stream.')
        self.stream.stop_stream()
        self.stream.close()
        self.ui.change_state_indicator("yellow", text="Recording Complete")
        
        # Open/save the audio file
        logging.info('Open/save file.')
        self.ui.change_state_indicator("Orange", text="Preparing Audio...")

        # Generate a unique file name for this recording
        unique_file_name = self.get_unique_file_name()
        recording_file_name = self.get_recording_file_path(unique_file_name)
        wavefile = wave.open(recording_file_name, 'wb')
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self.audio.get_sample_size(self.audio_format))
        wavefile.setframerate(self.sample_rate)
        wavefile.writeframes(b''.join(self.audio_frames))
        wavefile.close()
        self.ui.change_state_indicator("Orange", text="Audio Prepared...")

        # Add the new recording to the history
        self.update_recordings_history(unique_file_name)

        # Starting Transcription
        logging.info('Starting Transcription')
        self.ui.change_state_indicator("purple", text="Transcription Starting...")

        result = self.model.transcribe(recording_file_name, task="translate")  # Use full path here

        self.ui.change_state_indicator("green", text="Transcription Complete!")

        self.is_recording = False
        self.keystroke_thread.join()
    
        self.ui.change_state_indicator("green", text="Complete!")

        return result['text']


    def toggle_recording(self):
        if not self.is_recording:
            self.ui.change_state_indicator("yellow", text="Recording Starting...")
            # Start a new recording thread
            self.recording_thread = threading.Thread(target=self.start_recording)
            self.recording_thread.start()
            return ""  # No transcription when starting
        else:
            # Stop recording and wait for the thread to finish
            self.is_recording = False
            self.recording_thread.join()
            transcription = self.stop_recording_and_transcribe()
            self.ui.change_state_indicator("grey", text="Ready")  # Use UI method
            self.ui.flash_indicator()  # Use UI method
            self.ui.update_transcription_box(transcription)  # Use UI method to update the transcription box
            return transcription  # Return the transcription text after stopping

    def terminate(self):
        self.audio.terminate()

    def update_recordings_history(self, unique_file_name):
        full_path = self.get_recording_file_path(unique_file_name)
        if len(self.recordings_history) >= self.max_history_size:
            oldest_recording = self.recordings_history.pop(0)
            if os.path.exists(oldest_recording):
                os.remove(oldest_recording)

        self.recordings_history.append(full_path)
    
    def ensure_recordings_folder(self):
        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)
    
    def get_recording_file_path(self, file_name):
        return os.path.join(self.recordings_folder, file_name)
    
    def get_unique_file_name(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        return f"recording_{timestamp}.wav"
    
    def update_model(self, new_model_name):
        self.model_name = new_model_name
        self.model = whisper.load_model(self.model_name)
    
    def load_model_from_config(self):
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                model_name = config.get('model', 'tiny')
                self.model = whisper.load_model(model_name)
        except Exception as e:
            print(f"Error loading model from config: {e}")
            self.model = whisper.load_model('tiny')

    def simulate_keystrokes(self):
        if self.ui.chat_mode.get():
            # Press 'T' once to open the chat window
            self.keyboard_controller.press(keyboard.KeyCode.from_char('t'))
            self.keyboard_controller.release(keyboard.KeyCode.from_char('t'))
            time.sleep(0.5)  # Short delay before starting the loop

            # Cycle space and backspace while recording
            while self.is_recording:
                self.keyboard_controller.press(keyboard.Key.space)
                self.keyboard_controller.release(keyboard.Key.space)
                time.sleep(0.1)  # Short delay between space and backspace
                self.keyboard_controller.press(keyboard.Key.backspace)
                self.keyboard_controller.release(keyboard.Key.backspace)
                time.sleep(0.9)  # Continue the loop every second