import logging
from task_handler import TaskHandler
from watchdog.observers import Observer


class SchedulerRobot:
    """
    Manages tasks and observes changes in a given input path.

    Attributes:
        handler (TaskHandler): The object to handle tasks.
        observer (Observer): The object to monitor changes in the input path.
    """
    def __init__(self, input_path: str) -> None:
        """
        Initializes a new instance of the SchedulerRobot class.

        The TaskHandler and Observer instances are created, and the Observer starts observing the input path
        specified in the configuration.
        """
        self.handler = TaskHandler()
        self.observer = Observer()
        self.observer.schedule(self.handler, input_path, recursive=False)
        self.observer.start()

    def stop(self) -> None:
        """
        Stops the task handler and the observer.

        This method is generally called when you want to stop task processing and path monitoring.
        """
        self.handler.stop()
        self.stop_observer()

    def stop_observer(self) -> None:
        """
        Stops the observer.

        This method stops the observer that is monitoring changes in the input path.
        """
        logging.info("Stopping observer.")
        try:
            self.observer.stop()
        except Exception as e:
            logging.error(f"An error occurred while stopping observer: {str(e)}")
