import json
import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


# Abstract class for robots
class Robot:
    def __init__(self, name):
        self.name = name

    def send_task(self, task):
        print(f"Sending task '{task}' to {self.name}")
        time.sleep(1)  # simulate sending task

    def wait_task_end(self, task):
        print(f"Waiting task '{task}' ending from {self.name}")
        time.sleep(1)  # simulate waiting for task to end


# Two types of robots, but they behave the same in this context
class UniversalRobot(Robot):
    pass


class MobileRobot(Robot):
    pass


# Represents a path with a list of tasks to execute
class Path:
    def __init__(self, ID, Name, StartPosition, EndPosition, Action, PlateNumber, handler, task_queue=None):
        self.ID = ID
        self.Name = Name
        self.StartPosition = StartPosition
        self.EndPosition = EndPosition
        self.Action = Action
        self.PlateNumber = PlateNumber
        self.handler = handler
        self.EM = MobileRobot("EM")  # mobile robot
        self.URStart = UniversalRobot("UR_" + StartPosition)  # universal robot at start position
        self.UREnd = UniversalRobot("UR_" + EndPosition)  # universal robot at end position
        # If task queue is not provided, initialize it
        self.task_queue = task_queue or self.initialize_task_queue()

    # Initialize the task queue with tasks for the robots
    def initialize_task_queue(self):
        return [(self.EM, f"EM_to_{self.StartPosition}", "NotDone"),
                (self.URStart, "Place", "NotDone"),
                (self.EM, f"EM_{self.StartPosition}_to_{self.EndPosition}", "NotDone"),
                (self.UREnd, "Pick", "NotDone")]

    # Execute tasks in the task queue one by one
    def execute_tasks(self):
        while self.task_queue:
            robot, task, state = self.task_queue[0]  # peek at the first element
            if state == "NotDone":
                robot.send_task(task)
                self.task_queue[0] = (robot, task, "IsDoing")  # update state to "IsDoing"
                self.handler.save_state()  # save current state
            elif state == "IsDoing":
                robot.wait_task_end(task)
                self.task_queue.pop(0)  # remove the first element
                self.handler.save_state()  # save current state
        # After all tasks are done, remove this path from the handler
        self.handler.remove_path(self)

    # Convert this path to a dictionary for serialization
    def to_dict(self):
        return {
            "ID": self.ID,
            "Name": self.Name,
            "StartPosition": self.StartPosition,
            "EndPosition": self.EndPosition,
            "Action": self.Action,
            "PlateNumber": self.PlateNumber,
            "TaskQueue": [(robot.name, task, state) for robot, task, state in self.task_queue]
        }


# Handles file system events and maintains a list of paths
class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.json"]  # only process json files

    def __init__(self):
        super().__init__()
        self.path_list = []  # list of paths to execute
        self.load_state()  # load state from file at startup

    # Process a new json file
    def process(self, event):
        with open(event.src_path, 'r') as f:
            data = json.load(f)
            for path in data['paths']:
                # Create a new Path object and start executing its tasks
                path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                path['EndPosition'], path['Action'], path['PlateNumber'], self)
                self.path_list.append(path_obj)
                threading.Thread(target=path_obj.execute_tasks).start()

    # Called when a new file is created
    def on_created(self, event):
        self.process(event)

    # Print names of all paths for debugging
    def print_all_names(self):
        for path_obj in self.path_list:
            print(path_obj.Name)

    # Remove a path from the list
    def remove_path(self, path_obj):
        self.path_list.remove(path_obj)

    # Save current state to file
    def save_state(self):
        with open('state.json', 'w') as f:
            # Only save Path objects with non-empty task queues
            json.dump([path.to_dict() for path in self.path_list if path.task_queue], f, indent=4)

    # Load state from file
    def load_state(self):
        try:
            with open('state.json', 'r') as f:
                data = json.load(f)
                for path in data:
                    task_queue = []
                    for robot_name, task, state in path['TaskQueue']:
                        if 'EM' in robot_name:
                            robot = MobileRobot(robot_name)
                        else:
                            robot = UniversalRobot(robot_name)
                        task_queue.append((robot, task, state))

                    # Create a new Path object for each path in the state file
                    path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                    path['EndPosition'], path['Action'], path['PlateNumber'], self, task_queue)
                    self.path_list.append(path_obj)
                    # Start executing tasks for each path
                    threading.Thread(target=path_obj.execute_tasks).start()
        except FileNotFoundError:
            with open('state.json', 'w') as f:
                json.dump([], f, indent=4)  # Creates an empty state.json file


if __name__ == '__main__':
    input_path = "/home/mariano/Music"  # directory to watch
    handler = MyHandler()
    observer = Observer()
    observer.schedule(handler, input_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)  # keep the program running
    except KeyboardInterrupt:
        handler.print_all_names()  # print names of all paths for debugging
        observer.stop()

    observer.join()
