import json
import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class UniversalRobot:
    def __init__(self, name):
        self.name = name

    def send_task(self, task):
        print(f"Sending task '{task}' to {self.name}")
        time.sleep(1)

    def wait_task_end(self, task):
        print(f"Waiting task '{task}' ending from {self.name}")
        time.sleep(1)


class MobileRobot:
    def __init__(self, name):
        self.name = name

    def send_task(self, task):
        print(f"Sending task '{task}' to {self.name}")
        time.sleep(1)

    def wait_task_end(self, task):
        print(f"Waiting task '{task}' ending from {self.name}")
        time.sleep(1)


class Path:
    def __init__(self, ID, Name, StartPosition, EndPosition, Action, PlateNumber, handler, task_queue=None):
        self.ID = ID
        self.Name = Name
        self.StartPosition = StartPosition
        self.EndPosition = EndPosition
        self.Action = Action
        self.PlateNumber = PlateNumber
        self.handler = handler
        self.EM = MobileRobot("EM")
        self.URStart = UniversalRobot("UR_" + StartPosition)
        self.UREnd = UniversalRobot("UR_" + EndPosition)
        self.task_queue = task_queue or self.initialize_task_queue()

    def initialize_task_queue(self):
        return [(self.EM, f"EM_to_{self.StartPosition}", "NotDone"),
                (self.URStart, "Place", "NotDone"),
                (self.EM, f"EM_{self.StartPosition}_to_{self.EndPosition}", "NotDone"),
                (self.UREnd, "Pick", "NotDone")]

    def execute_tasks(self):
        while self.task_queue:
            robot, task, state = self.task_queue[0]  # peek at the first element
            if state == "NotDone":
                robot.send_task(task)
                self.task_queue[0] = (robot, task, "IsDoing")
                self.handler.save_state()
            elif state == "IsDoing":
                robot.wait_task_end(task)
                self.task_queue.pop(0)  # remove the first element
                self.handler.save_state()
        self.handler.remove_path(self)

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


class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.json"]

    def __init__(self):
        super().__init__()
        self.path_list = []
        self.load_state()

    def process(self, event):
        """
        Process the json file when it appears in the directory
        """
        with open(event.src_path, 'r') as f:
            data = json.load(f)
            for path in data['paths']:
                path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                path['EndPosition'], path['Action'], path['PlateNumber'], self)
                self.path_list.append(path_obj)
                threading.Thread(target=path_obj.execute_tasks).start()

    def on_created(self, event):
        self.process(event)

    def print_all_names(self):
        for path_obj in self.path_list:
            print(path_obj.Name)

    def remove_path(self, path_obj):
        self.path_list.remove(path_obj)

    def save_state(self):
        with open('state.json', 'w') as f:
            # Only save Path objects with non-empty task queues
            json.dump([path.to_dict() for path in self.path_list if path.task_queue], f, indent=4)

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

                    path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                    path['EndPosition'], path['Action'], path['PlateNumber'], self, task_queue)
                    self.path_list.append(path_obj)
                    threading.Thread(target=path_obj.execute_tasks).start()
        except FileNotFoundError:
            with open('state.json', 'w') as f:
                json.dump([], f, indent=4)  # Creates an empty state.json file


if __name__ == '__main__':
    input_path = "/home/mariano/Music"
    handler = MyHandler()
    observer = Observer()
    observer.schedule(handler, input_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handler.print_all_names()
        observer.stop()

    observer.join()
