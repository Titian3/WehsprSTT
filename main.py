from WhisperController import WhisperController
import logging

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("LOADING WEHSPER....")
    logging.info("This can take a minute if very large model is used.")
    whisper_controller = WhisperController()
    whisper_controller.run()

if __name__ == "__main__":
    main()
    
