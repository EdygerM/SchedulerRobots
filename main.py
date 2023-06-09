import time
import logging
from utility import load_config, setup_logging
from scheduler_robot import SchedulerRobot


if __name__ == '__main__':
    config = load_config()
    setup_logging(config)
    scheduler = SchedulerRobot(config.get('GENERAL', 'UR_SETUP_FILE'), config.get('GENERAL', 'INPUT_PATH'))

    try:
        logging.info("Starting main loop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.exception("Interrupt received!")
    finally:
        scheduler.stop_all()
        time.sleep(1)
        logging.info("Main loop stopped.")
