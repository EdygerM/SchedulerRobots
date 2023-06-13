import time
import logging
from utility import setup_logging
from scheduler_robot import SchedulerRobot
from config import Config

config = Config()

if __name__ == '__main__':
    setup_logging()
    scheduler = SchedulerRobot(config.get('GENERAL', 'INPUT_PATH'))

    try:
        logging.info("Starting main loop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.exception("Interrupt received!")
    finally:
        scheduler.stop()
        time.sleep(1)
        logging.info("Main loop stopped.")
