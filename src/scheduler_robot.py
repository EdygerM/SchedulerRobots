import logging
from tasks_handler import TasksHandler
from watchdog.observers import Observer

class SchedulerRobot:
    """
    Manages tasks and observes changes in a given input path.

    The SchedulerRobot manages tasks via an instance of TasksHandler and observes changes in a given input path
    using an instance of the Observer class. The Observer is set to start observing as soon as a SchedulerRobot
    instance is created.

    Attributes:
        tasksHandler (TasksHandler): Handles tasks.
        inputObserver (Observer): Monitors changes in the input path.
    """
    def __init__(self, input_path: str) -> None:
        """
        Initializes a new instance of the SchedulerRobot class.

        The TasksHandler and Observer instances are created, and the Observer starts observing the specified input path.
        The observer will not monitor subdirectories of the input path.

        Args:
            input_path (str): The path to be monitored by the observer.
        """
        self.tasksHandler = TasksHandler()
        self.inputObserver = Observer()
        self.inputObserver.schedule(self.tasksHandler, input_path, recursive=False)
        self.inputObserver.start()

    def stop(self) -> None:
        """
        Stops the task handler and the observer.

        This method is generally called when task processing and path monitoring are no longer required.
        """
        self.tasksHandler.stop()
        self.stop_observer()

    def stop_observer(self) -> None:
        """
        Stops the observer.

        This method stops the observer that is monitoring changes in the input path. If an error occurs while
        attempting to stop the observer, it will be logged.

        Raises:
            RuntimeError: If the observer was not running when stop was attempted.
            Exception: If an unexpected error occurred while attempting to stop the observer.
        """
        logging.info("Stopping observer.")
        try:
            self.inputObserver.stop()
        except RuntimeError as e:
            logging.error(
                f"An error occurred while stopping observer: {str(e)} - Possibly the observer was not running.")
        except Exception as e:
            logging.error(f"An unexpected error occurred while stopping observer: {str(e)}")
