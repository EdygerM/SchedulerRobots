import logging
import time


class FleetManager:
    def __init__(self, name):
        # Initiate MobileRobot instance with a name
        self.name = name
        logging.info(f"Fleet manager {self.name} initialized.")

    def send_task(self, task):
        """
        """

        try:
            logging.info(f"Attempting to send task '{task}' to {self.name}.")
            time.sleep(1)  # Simulate the time it takes to send a task
            logging.info(f"Task '{task}' sent to {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while sending task '{task}' to {self.name}: {str(e)}")

    def wait_task_end(self):
        """
        """

        try:
            logging.info(f"Waiting task ending from {self.name}.")
            time.sleep(1)  # Simulate the time it takes for a task to end
            logging.info(f"Task ended from {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while waiting for the task to end from {self.name}: {str(e)}")
