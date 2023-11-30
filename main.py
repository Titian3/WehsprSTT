from WhisperController import WhisperController
from WhisperUI import WhisperUI
import logging

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("LOADING WEHSPER....")

    logging.info("Setup UI.")
    whisper_ui = WhisperUI()
    
    logging.info("Setup Controller.")
    whisper_controller = WhisperController(whisper_ui)
    whisper_ui.set_controller(whisper_controller)
    whisper_ui.set_on_close_callback(whisper_controller.close_application)

    logging.info("Start Controller.")
    whisper_controller.run()
    

if __name__ == "__main__":
    main()
