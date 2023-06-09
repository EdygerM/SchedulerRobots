import time
import logging
from utility import setup_logging
from scheduler_robot import SchedulerRobot


if __name__ == '__main__':
    setup_logging()
    scheduler = SchedulerRobot()

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
