import threading
import json
from watchdog.events import PatternMatchingEventHandler
from src.path import Path
from src.edy_mobile_robot import EdyMobile
from config import Config

config = Config()


# Class for a handler that handles file system events and maintains a list of paths
class TaskHandler(PatternMatchingEventHandler):
    patterns = ["*.json"]

    def __init__(self, ur_robots):
        super().__init__()
        self.ur_robots = ur_robots
        self.path_list = []
        self.load_state()

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

    def stop_all_tasks(self):
        """
        Stop executing all tasks.
        """

        for path in self.path_list:
            path.stop_tasks()
