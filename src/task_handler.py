import threading
import json
from watchdog.events import PatternMatchingEventHandler
from src.path import Path
from universal_robot import UniversalRobot
from utility import load_json_file
from src.edy_mobile_robot import EdyMobile
import logging
from config import Config

config = Config()


# Class for a handler that handles file system events and maintains a list of paths
class TaskHandler(PatternMatchingEventHandler):
    patterns = ["*.json"]

    def __init__(self):
        super().__init__()
        self.ur_robots = {}
        self.setup_universal_robots()
        self.path_list = []
        self.load_state()

    def setup_universal_robots(self):
        """
        Set up UniversalRobot instances.
        Reads the setup file, creates UniversalRobot instances, and starts servers for each of them.
        """
        for info in load_json_file(config.get('GENERAL', 'UR_SETUP_FILE')):
            try:
                logging.info(f"Creating UniversalRobot instance for {info['name']} with host {info['host']}"
                             f" and port {info['port']}.")
                ur = UniversalRobot(info["name"], info["host"], info["port"])
                self.ur_robots[info["name"]] = ur

                logging.info(f"Starting server for {info['name']}.")
                ur.start_server()
                logging.info(f"Server for {info['name']} started successfully.")

            except Exception as e:
                logging.error(f"An error occurred while setting up {info['name']}: {str(e)}")

    def load_state(self):
        """
        Load state from a file.
        """

        try:
            with open(config.get('GENERAL', 'STATE_FILE'), 'r') as file:
                data = json.load(file)
                for path in data:
                    task_queue = []
                    for robot_name, task, state in path['TaskQueue']:
                        if 'EM' in robot_name:
                            robot = EdyMobile(robot_name)
                        else:
                            robot = self.ur_robots[robot_name]
                        task_queue.append((robot, task, state))
                    path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                    path['EndPosition'], path['Action'], path['PlateNumber'], self, self.ur_robots,
                                    task_queue)
                    self.path_list.append(path_obj)
                    threading.Thread(target=path_obj.execute_tasks).start()
        except FileNotFoundError:
            pass

    def process(self, event):
        """
        Process a new json file, create a new Path object and start executing its tasks.
        """

        with open(event.src_path, 'r') as file:
            data = json.load(file)
            for path in data['paths']:
                path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                path['EndPosition'], path['Action'], path['PlateNumber'], self, self.ur_robots)
                self.path_list.append(path_obj)
                threading.Thread(target=path_obj.execute_tasks).start()

    def print_all_names(self):
        """
        Print the names of all path objects. This is useful for debugging.
        """
        for path_obj in self.path_list:
            print(path_obj.Name)

    def on_created(self, event):
        """
        Called when a new file is created.
        """

        self.process(event)

    def remove_path(self, path_obj):
        """
        Remove a path from the list.
        """

        self.path_list.remove(path_obj)

    def save_state(self):
        """
        Save the current state to a file.
        """

        with open(config.get('GENERAL', 'STATE_FILE'), 'w') as f:
            paths_to_save = [p for p in self.path_list if p.task_queue]
            json.dump([p.to_dict() for p in paths_to_save], f, indent=4)

    def stop(self):
        """
        Stops all the servers and the tasks.
        """
        self.stop_servers()
        self.stop_tasks()

    def stop_servers(self):
        """
        Attempt to stop all servers associated with each UniversalRobot instance.
        """
        logging.info("Attempting to stop all servers.")
        for UR in self.ur_robots.values():
            try:
                UR.stop_server()
                logging.info(f"Server for {UR.name} stopped successfully.")
            except Exception as e:
                logging.error(f"An error occurred while stopping server for {UR.name}: {str(e)}")

    def stop_tasks(self):
        """
        Attempt to stop all tasks associated with each path in the TaskHandler.
        """
        logging.info("Attempting to stop all tasks.")
        for path in self.path_list:
            try:
                path.stop_tasks()
                logging.info(f"Stopped tasks for path {path}")
            except Exception as e:
                logging.error(f"An error occurred while stopping tasks for path {path}: {str(e)}")
