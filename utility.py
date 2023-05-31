import logging
import json
import sys


def load_json_file(file_name):
    data = []
    try:
        logging.info(f"Attempting to open and load {file_name}.")
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.error(f'{file_name} file does not exist or could not be opened.')
    except json.JSONDecodeError:
        logging.error(f'Could not decode JSON from {file_name}.')
    except Exception as e:
        logging.error('An unexpected error occurred: ' + str(e))
    finally:
        if not data:
            logging.info(f"Exiting the application due to errors while loading the {file_name}.")
            sys.exit(1)

    logging.info(f"Successfully loaded {file_name}.")
    return data
