import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import json
from pynput import keyboard, mouse


class WhisperUI:
    def __init__(self, on_close_callback, controller):
        # Create the main application window
        self.root = tk.Tk()
        self.root.title("Wehspr")
        self.icon = tk.PhotoImage(file='WEH.png')  # or .png
        self.root.iconphoto(True, self.icon)

        # Create a tab control
        self.tabControl = ttk.Notebook(self.root)

        # Create tabs
        self.main_tab = ttk.Frame(self.tabControl)
        self.config_tab = ttk.Frame(self.tabControl)

        # Add tabs to the notebook
        self.tabControl.add(self.main_tab, text='Main')
        self.tabControl.add(self.config_tab, text='Config')
        self.tabControl.pack(expand=1, fill="both")

        # Create a label for the image
        self.icon_label = tk.Label(self.main_tab, image=self.icon)
        self.icon_label.pack()

        # Header
        self.header = tk.Label(self.main_tab, text="Wehspr", font=("Helvetica", 16))
        self.header.pack()

        # State indicator (as full-width canvas)
        self.state_indicator = tk.Canvas(self.main_tab, height=50, bg="gray")
        self.state_indicator.pack(fill=tk.X, pady=20)

        # State text label
        self.state_text = tk.Label(self.main_tab, text="Ready", font=("Helvetica", 12))
        self.state_text.pack()

        # Admin mode toggle
        self.chat_mode = tk.BooleanVar()
        self.chat_mode_toggle = tk.Checkbutton(self.main_tab, text="Chat Mode", var=self.chat_mode, command=self.toggle_chat_mode)
        self.chat_mode_toggle.pack()

        # Clipboard details label
        self.clipboard_label = tk.Label(self.main_tab, text="On your clipboard:", font=("Helvetica", 10))
        self.clipboard_label.pack()

        # Transcription text box
        self.transcription_box = scrolledtext.ScrolledText(self.main_tab, wrap=tk.WORD)
        self.transcription_box.pack(pady=10, fill=tk.BOTH, expand=True)

        # Set the callback for when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", on_close_callback)

        # Detect shortcut buttons
        self.detect_record_button = tk.Button(self.config_tab, text="Detect", command=lambda: self.detect_shortcut('record'))
        self.detect_paste_button = tk.Button(self.config_tab, text="Detect", command=lambda: self.detect_shortcut('paste'))

        self.detect_record_button.grid(row=0, column=2)
        self.detect_paste_button.grid(row=1, column=2)

        # Set controller
        self.controller = controller
        # Configure tab
        self.create_config_ui()

        # Load saved/default config
        self.load_configuration()

    # Updates the UI state indicator color (entire canvas)
    def change_state_indicator(self, color, text=""):
        self.state_indicator.config(bg=color)
        self.state_text.config(text=text)  # Update the text of the state label
        self.root.update_idletasks()

    # Makes the indicator flash green
    def flash_indicator(self):
        self.change_state_indicator("green")
        self.root.after(1000, lambda: self.change_state_indicator("grey", text="Ready"))

    # Updates the transcription box
    def update_transcription_box(self, text):
        self.transcription_box.delete(1.0, tk.END)
        self.transcription_box.insert(tk.INSERT, text)
        self.transcription_box.update_idletasks()

    def toggle_chat_mode(self):
        if self.chat_mode.get():
            print("Chat Mode ON")
        else:
            print("Chat Mode OFF")
    
    def create_config_ui(self):
        # Labels
        tk.Label(self.config_tab, text="Record Shortcut:").grid(row=0, column=0, sticky='w')
        tk.Label(self.config_tab, text="Paste Shortcut:").grid(row=1, column=0, sticky='w')

        # Detect shortcut buttons
        self.detect_record_button = tk.Button(self.config_tab, text="Detect", command=lambda: self.detect_shortcut('record'))
        self.detect_paste_button = tk.Button(self.config_tab, text="Detect", command=lambda: self.detect_shortcut('paste'))

        # Entry fields for shortcuts
        self.record_shortcut_entry = tk.Entry(self.config_tab)
        self.paste_shortcut_entry = tk.Entry(self.config_tab)
    
        self.record_shortcut_entry.grid(row=0, column=1)
        self.paste_shortcut_entry.grid(row=1, column=1)

        # Model selection label and dropdown
        self.model_label = tk.Label(self.config_tab, text="Model:")
        self.model_label.grid(row=3, column=0, sticky='w')

        # Combobox for model selection
        self.model_combobox = ttk.Combobox(self.config_tab, 
                                        values=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"])
        self.model_combobox.grid(row=3, column=1)
        self.model_combobox.current(0)  # Set default selection to 'tiny'

        # Save button
        self.save_config_button = tk.Button(self.config_tab, text="Save and Close", command=self.save_configuration)
        self.save_config_button.grid(row=4, column=1, sticky='e')

    def load_configuration(self):
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                record_config = config.get('record_shortcut', {"type": "", "key": ""})
                paste_config = config.get('paste_shortcut', {"type": "", "key": ""})

                # Format and insert the configuration in a readable format
                formatted_record_config = f"{record_config.get('type', '').capitalize()}: {record_config.get('key', '')}"
                formatted_paste_config = f"{paste_config.get('type', '').capitalize()}: {paste_config.get('key', '')}"

                self.record_shortcut_entry.delete(0, tk.END)
                self.record_shortcut_entry.insert(0, formatted_record_config)

                self.paste_shortcut_entry.delete(0, tk.END)
                self.paste_shortcut_entry.insert(0, formatted_paste_config)

                # Set the model selection based on the configuration
                model_config = config.get('model', 'tiny')
                self.model_combobox.set(model_config)

        except FileNotFoundError:
            print("Configuration file not found. Using default settings.")
        except json.JSONDecodeError:
            print("Error decoding configuration file. Using default settings.")


    def save_configuration(self):
        # Extract only the type and key from the formatted string
        record_shortcut = self.record_shortcut_entry.get().split(": ")
        paste_shortcut = self.paste_shortcut_entry.get().split(": ")
        self.controller.update_shortcuts_from_config()

        # Save the model selection
        selected_model = self.model_combobox.get()

        config = {
            "record_shortcut": {"type": record_shortcut[0].lower(), "key": record_shortcut[1]},
            "paste_shortcut": {"type": paste_shortcut[0].lower(), "key": paste_shortcut[1]},
            "model": selected_model
        }
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        print("Configuration saved.")

        # I need to reboot the app here to apply the config
        self.close_application()


    def detect_shortcut(self, mode):
        self.controller.shortcut_detection_mode = mode
        self.controller.start_listening_for_shortcut()

    def set_record_shortcut(self, shortcut_info):
        formatted_shortcut = f"{shortcut_info['type'].capitalize()}: {shortcut_info['key']}"
        self.record_shortcut_entry.delete(0, tk.END)
        self.record_shortcut_entry.insert(0, formatted_shortcut)
        self.controller.stop_listening_for_shortcut()

    def set_paste_shortcut(self, shortcut_info):
        formatted_shortcut = f"{shortcut_info['type'].capitalize()}: {shortcut_info['key']}"
        self.paste_shortcut_entry.delete(0, tk.END)
        self.paste_shortcut_entry.insert(0, formatted_shortcut)
        self.controller.stop_listening_for_shortcut()

    # Starts the tkinter main loop
    def start(self):
        self.root.mainloop()

    def close_application(self):
        self.controller.close_application()