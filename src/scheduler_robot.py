import logging
from config import Config
from task_handler import TaskHandler
from watchdog.observers import Observer

config = Config()


class SchedulerRobot:
    """
    The SchedulerRobot class is responsible for managing tasks and observing changes in a given input path.
    """
    def __init__(self):
        """
        Initialize the TaskHandler for task management and the Observer for monitoring the changes in the input path.
        The observer is set to start observing as soon as an instance of the class is created.
        """
        self.handler = TaskHandler()
        self.observer = Observer()
        self.observer.schedule(self.handler, config.get('GENERAL', 'INPUT_PATH'), recursive=False)
        self.observer.start()

    def stop(self):
        """
        Stops the task handling process and the observer.
        """
        self.handler.stop()
        self.stop_observer()

    def stop_observer(self):
        """
        Stop the observer that is monitoring the input path.
        """
        logging.info("Stopping observer.")
        try:
            self.observer.stop()
        except Exception as e:
            logging.error(f"An error occurred while stopping observer: {str(e)}")
