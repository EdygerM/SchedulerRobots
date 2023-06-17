import json
import logging
import threading
from file_loader import load_json_file
from watchdog.events import PatternMatchingEventHandler
from path import Path
from universal_robot import UniversalRobot
from fleet_manager import FleetManager


class TasksHandler(PatternMatchingEventHandler):
    """
    Class for a handler that handles file system events and maintains a list of paths
    """
    patterns = ["*.json"]

    def __init__(self, universal_robots_setup_file, state_file):
        super().__init__()
        self.universal_robots_setup = load_json_file(universal_robots_setup_file)
        self.universal_robots = self.setup_universal_robots()
        self.fleet_manager = FleetManager()
        self.path_list = []
        self.create_and_start_paths_from_state(state_file)

    def setup_universal_robots(self):
        """
        Initialize UniversalRobot instances using a configuration file.
        Configuration file content is loaded and UniversalRobot instances are created.
        """
        return {
            setup["name"]: UniversalRobot(setup["name"], setup["host"], setup["port"])
            for setup in self.universal_robots_setup
        }

    def create_and_start_paths_from_state(self, state_file):
        state = load_json_file(state_file)
        for path in state:
            task_queue = self.create_task_queue(path['TaskQueue'])
            self.create_and_start_path(path, task_queue)

    def create_task_queue(self, task_queue_data):
        """
        Create the task queue for each path.
        """
        task_queue = []
        for robot_name, task, state in task_queue_data:
            if 'EM' in robot_name:
                robot = self.fleet_manager
            elif 'UR' in robot_name:
                robot = self.universal_robots[robot_name]
            else:
                robot = None
            task_queue.append((robot, task, state))
        return task_queue

    def create_and_start_path(self, path_data, task_queue):
        path = Path(path_data['Name'], path_data['StartPosition'],
                    path_data['EndPosition'], path_data['Action'], path_data['PlateNumber'], self,
                    self.universal_robots, task_queue)
        self.path_list.append(path)
        threading.Thread(target=path.execute_tasks).start()

    def on_created(self, event):
        """
        Called when a new file is created.
        """
        self.process(event)

    def process(self, event):
        """
        Process a new json file, create a new Path object and start executing its tasks.
        """

        with open(event.src_path, 'r') as input_file:
            path_data = load_json_file(input_file)
            self.create_and_start_path(path_data, None)

    def remove_path(self, path):
        """
        Remove a path from the list.
        """
        self.path_list.remove(path)

    def save_state(self):
        """
        Save the current state to a file.
        """
        with open(self.state_file, 'w') as file:
            paths_to_save = [path for path in self.path_list if path.task_queue]
            json.dump([path.to_dict() for path in paths_to_save], file, indent=4)

    def stop_tasks(self):
        """
        Attempt to stop all tasks associated with each path in the TaskHandler.
        """
        logging.info("Attempting to stop all tasks.")
        for path in self.path_list:
            try:
                path.stop_tasks()
            except Exception as e:
                logging.error(f"An error occurred while stopping tasks for path {path}: {e}")

    def stop_servers(self):
        logging.info("Attempting to stop all servers.")
        for universal_robot in self.universal_robots.values():
            universal_robot.stop_server()

    def stop(self):
        self.stop_tasks()
        self.stop_servers()
