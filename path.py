from edy_mobile_robot import EdyMobile
import logging


# Class for a Path that has a series of tasks that can be executed by the robots
class Path:
    def __init__(self, ID, Name, StartPosition, EndPosition, Action, PlateNumber, handler, robots_dict,
                 task_queue=None):
        self.ID = ID
        self.Name = Name
        self.StartPosition = StartPosition
        self.EndPosition = EndPosition
        self.Action = Action
        self.PlateNumber = PlateNumber
        self.handler = handler
        self.EM = EdyMobile("EM")
        self.robots_dict = robots_dict
        self.task_queue = task_queue or self.initialize_task_queue()
        self.stop_thread = False

    def initialize_task_queue(self):
        """
        Initialize the task queue with tasks for the robots
        """

        return [(self.EM, f"EM_to_{self.StartPosition}", "NotDone"),
                (self.robots_dict[("UR_" + self.StartPosition)], "Place", "NotDone"),
                (self.EM, f"EM_{self.StartPosition}_to_{self.EndPosition}", "NotDone"),
                (self.robots_dict[("UR_" + self.EndPosition)], "Pick", "NotDone")]

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
                robot.wait_task_end(task)
                self.task_queue.pop(0)
                self.handler.save_state()
        if not self.task_queue:
            self.handler.remove_path(self)

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
            "ID": self.ID,
            "Name": self.Name,
            "StartPosition": self.StartPosition,
            "EndPosition": self.EndPosition,
            "Action": self.Action,
            "PlateNumber": self.PlateNumber,
            "TaskQueue": [(robot.name, task, state) for robot, task, state in self.task_queue]
        }
