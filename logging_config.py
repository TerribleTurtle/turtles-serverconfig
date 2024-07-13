import logging

def setup_logging():
    logging.basicConfig(
        level=logging.ERROR,  # Change log level to ERROR
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("error.log", mode='w'),  # Overwrite existing log file
            logging.StreamHandler()
        ]
    )
