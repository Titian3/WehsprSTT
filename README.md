# Wehspr - STT

## Description

Wehspr is a speech-to-text (STT) application designed to transcribe audio inputs into text. It uses locally running Whisper STT models to transribe also to translate on higher models. The main purpose for making it was to quickly transcribe in english for RP games to have better immersion, potentially connect communities with translation and save some time.

## Setup

To run Wehspr, ensure you have the following prerequisites installed:

- Python 3.x
- Tkinter (usually comes with Python)
- PyAudio: `pip install pyaudio`
- Whisper: `pip install whisper`
- pynput: `pip install pynput`
- pyperclip: `pip install pyperclip`

Clone the repository or download the source code:

```bash
git clone [repository_url]
cd [repository_directory]
```

## Usage

1. **Starting the Application**: Run the application with `python main.py`.
2. **Recording**: Initiate recording using the configured shortcut or mouse button.
3. **Transcription**: After recording, the audio is transcribed and displayed in the main window.
4. **Paste Text**: Use Paste shortcut to paste transcription, modify it first in the text field if required.

## Configuration

The configuration tab in the application allows you to:

- Set keyboard and mouse shortcuts for recording and pasting.
- Select the Whisper model to be used for transcription (`tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`).
- Save and apply configurations, which will close the application for changes to take effect.

Configuration is stored in `config.json`. On the next launch, the application loads the saved settings.

## Additional Information

- **Runs locally**: No APIs, runs with locally running Whisper models.
- **Recording History**: The application maintains a small history of recent recordings locally for debugging purposes.
- **Customizable Models**: Different Whisper models can be selected based on preference and resource availability.
- **Translation Possible**: On higher models you can use it as a translator, they take longer to process and require better hardware.

