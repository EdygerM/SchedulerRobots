import time
import logging
from scheduler_robot import SchedulerRobot

# UR_SETUP_FILE: The file containing the setup information for Universal Robots
UR_SETUP_FILE = "setup_universal_robot_test.json"

# INPUT_PATH: The directory which the program will monitor for changes
INPUT_PATH = "/home/mariano/Music"

# Configure the logging settings
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

if __name__ == '__main__':
    logging.info("START OF SCRIPT")

    running = True
    scheduler = SchedulerRobot(UR_SETUP_FILE, INPUT_PATH)

    try:
        logging.info("Starting main loop.")
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.exception("Interrupt received!")
    finally:
        # Stop all tasks, servers, and observer in the event of a KeyboardInterrupt or other exit
        scheduler.stop_all()

        time.sleep(1)  # Allow some time for all servers and tasks to stop
        running = False  # Stop the loop
        logging.info("Main loop stopped.")
