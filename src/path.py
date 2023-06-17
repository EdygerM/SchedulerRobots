from fleet_manager import FleetManager
from file_loader import load_json_file
import logging


# Class for a Path that has a series of tasks that can be executed by the robots
class Path:
    def __init__(self, name, start_position, end_position, action, plate_number, handler, robots_dict,
                 task_queue=None):
        self.name = name
        self.start_position = start_position
        self.end_position = end_position
        self.action = action
        self.plate_number = plate_number
        self.handler = handler
        self.EM = FleetManager("EM")
        self.robots_dict = robots_dict
        self.task_queue = task_queue or self.initialize_task_queue()
        self.stop_thread = False

    @classmethod
    def from_config(cls, config_file, handler, universal_robots, task_queue):
        path_data = load_json_file(config_file)
        return cls(path_data['Name'], path_data['StartPosition'],
                   path_data['EndPosition'], path_data['Action'], path_data['PlateNumber'], handler,
                   universal_robots, task_queue)

    def initialize_task_queue(self):
        """
        Initialize the task queue with tasks for the robots
        """

        return [(self.EM, f"EM_to_{self.start_position}", "NotDone"),
                (self.robots_dict[("UR_" + self.start_position)], "Place", "NotDone"),
                (self.EM, f"EM_{self.start_position}_to_{self.end_position}", "NotDone"),
                (self.robots_dict[("UR_" + self.end_position)], "Pick", "NotDone")]

    def execute_tasks(self):
        """
        Execute tasks in the task queue one by one. If the task queue is empty, remove this path from the handler.
        """

        while self.task_queue and not self.stop_thread:
            robot, task, state = self.task_queue[0]
            if state == "NotDone":
                # Wait for the robot to be connected before sending the task
                if robot.name[:2] == "UR":
                    robot.wait_for_connection()
                robot.send_task(task)
                self.task_queue[0] = (robot, task, "IsDoing")
                self.handler.save_state()
            elif state == "IsDoing":
                if robot.name[:2] == "UR":
                    robot.wait_for_connection()
                robot.wait_task_end()
                self.task_queue.pop(0)
                self.handler.save_state()
        if not self.task_queue:
            self.handler.remove_path(self)
            logging.info(f"Stopped tasks for path {self.name}")

    def stop_tasks(self):
        """
        Stop executing tasks.
        """

        self.stop_thread = True

    def to_dict(self):
        """
        Convert this path to a dictionary for serialization.
        """

        return {
            "Name": self.name,
            "start_position": self.start_position,
            "end_position": self.end_position,
            "Action": self.action,
            "PlateNumber": self.plate_number,
            "TaskQueue": [(robot.name, task, state) for robot, task, state in self.task_queue]
        }
