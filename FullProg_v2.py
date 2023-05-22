import errno
import socket
import json
import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from threading import Event


# Define base class Robot with a name
class Robot:
    def __init__(self, name):
        self.name = name


class UniversalRobot(Robot):
    def __init__(self, name, host, port):
        super().__init__(name)
        self.host = host
        self.port = port
        self.conn = None
        self.s = None
        self.server_running = False  # Add another flag to indicate whether the server is running or not
        self.stop_thread = False
        self.connection_event = Event()  # Add this line

    def start_server(self):
        def server_func():
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.host, self.port))
            self.s.listen()
            self.s.setblocking(False)  # set the socket to non-blocking mode
            self.server_running = True  # Set the flag to True as the server has started
            while self.server_running:  # check the flag in the loop
                try:
                    self.conn, addr = self.s.accept()
                    print(f'Connected by {addr}')
                    self.connection_event.set()  # Add this line
                except socket.error as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        raise
                    time.sleep(1)  # no connection, sleep for a while and try again
                except Exception as e:
                    print(f"An error occurred: {e}")
            self.s.close()
            print("Server function exited.")

        self.stop_thread = False
        server_thread = threading.Thread(target=server_func)
        server_thread.start()
        print(f"Server started on {self.host}:{self.port}")

    def stop_server(self):
        self.stop_thread = True
        self.server_running = False  # Set the flag to False as the server is about to stop
        if self.conn:
            self.conn.close()
        if self.s:
            self.s.close()
        print(f"Server stopped on {self.host}:{self.port}")

    def send_task(self, task):
        """Sends a task to the robot's server"""

        try:
            self.conn.sendall(task.encode())
            print(f"Task '{task}' sent to {self.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def wait_task_end(self, task):
        """Waits for a task to end"""

        print(f"Waiting task '{task}' ending from {self.name}")
        while True:
            if self.conn is None:
                time.sleep(1)  # wait for a while before trying again
                continue
            data = self.conn.recv(1024)
            if data:
                print(f"Task ended. Received message: {data.decode()}")
                break
            time.sleep(1)  # wait for a while before trying to read again


# Define a class for mobile robot with functionalities to send tasks and wait for them to end
class MobileRobot(Robot):
    def __init__(self, name):
        super().__init__(name)

    def send_task(self, task):
        print(f"Sending task '{task}' to {self.name}")
        time.sleep(1)  # simulate sending task

    def wait_task_end(self, task):
        print(f"Waiting task '{task}' ending from {self.name}")
        time.sleep(1)  # simulate waiting for task to end


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
        self.task_queue = task_queue or self.initialize_task_queue()  # Initialize the task queue with tasks for the robots
        self.stop_thread = False  # Add this attribute to stop the thread

    def initialize_task_queue(self):
        """Initialize the task queue with tasks for the robots"""

        return [(self.EM, f"EM_to_{self.StartPosition}", "NotDone"),
                (robots_dict[("UR_" + self.StartPosition)], "Place", "NotDone"),
                (self.EM, f"EM_{self.StartPosition}_to_{self.EndPosition}", "NotDone"),
                (robots_dict[("UR_" + self.EndPosition)], "Pick", "NotDone")]

    def execute_tasks(self):
        """Execute tasks in the task queue one by one"""
        while self.task_queue and not self.stop_thread:  # Add check for self.stop_thread
            robot, task, state = self.task_queue[0]  # peek at the first element
            if state == "NotDone":
                robot.send_task(task)
                self.task_queue[0] = (robot, task, "IsDoing")  # update state to "IsDoing"
                self.handler.save_state()  # save current state
            elif state == "IsDoing":
                robot.wait_task_end(task)
                self.task_queue.pop(0)  # remove the first element
                self.handler.save_state()  # save current state
        if not self.task_queue:  # Add this condition to remove the path from the handler only if the task_queue is empty
            self.handler.remove_path(self)  # After all tasks are done, remove this path from the handler

    def stop_tasks(self):  # Add this method to stop tasks
        """Stops executing tasks"""
        self.stop_thread = True

    def to_dict(self):
        """Convert this path to a dictionary for serialization"""

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

    def process(self, event):
        """Process a new json file"""

        with open(event.src_path, 'r') as file:
            data = json.load(file)
            for path in data['paths']:
                # Create a new Path object and start executing its tasks
                path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                path['EndPosition'], path['Action'], path['PlateNumber'], self)
                self.path_list.append(path_obj)
                threading.Thread(target=path_obj.execute_tasks).start()

    def on_created(self, event):
        """Called when a new file is created"""

        self.process(event)

    def print_all_names(self):
        """Print names of all paths for debugging"""

        for path_obj in self.path_list:
            print(path_obj.Name)

    def remove_path(self, path_obj):
        """Remove a path from the list"""

        self.path_list.remove(path_obj)

    def save_state(self):
        """Save the current state to a file"""
        with open('state.json', 'w') as f:
            # Filter paths that have non-empty task queues
            paths_to_save = [p for p in self.path_list if p.task_queue]
            json.dump([p.to_dict() for p in paths_to_save], f, indent=4)

    def load_state(self):
        """Load state from a file"""

        try:
            with open('state.json', 'r') as file:
                data = json.load(file)
                for path in data:
                    task_queue = []
                    for robot_name, task, state in path['TaskQueue']:
                        if 'EM' in robot_name:
                            robot = MobileRobot(robot_name)
                        else:
                            robot = robots_dict[robot_name]
                        task_queue.append((robot, task, state))
                    path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                    path['EndPosition'], path['Action'], path['PlateNumber'], self,
                                    task_queue)
                    self.path_list.append(path_obj)
                    threading.Thread(target=path_obj.execute_tasks).start()
        except FileNotFoundError:
            pass  # state file does not exist yet

    def stop_all_tasks(self):  # Add this method to stop all tasks
        """Stops executing all tasks"""

        for path in self.path_list:
            path.stop_tasks()


if __name__ == '__main__':

    # Load robot info from json file
    with open('robots_info.json', 'r') as f:
        robots_info = json.load(f)

        # Create an instance for each robot and start the server
    robots_dict = {}
    for info in robots_info:
        UR = UniversalRobot(info["name"], info["host"], info["port"])
        UR.start_server()
        robots_dict[info["name"]] = UR

    # Wait for all UR servers to accept at least one connection each
    for UR in robots_dict.values():
        UR.connection_event.wait()

    input_path = "/home/mariano/Music"  # directory to watch
    handler = MyHandler()
    observer = Observer()
    observer.schedule(handler, input_path, recursive=False)
    observer.start()
    running = True

    try:
        while running:
            time.sleep(1)  # keep the program running
    except KeyboardInterrupt:
        handler.print_all_names()  # print names of all paths for debugging
        for path_ in handler.path_list:  # Stop all tasks
            path_.stop_tasks()
        for UR in robots_dict.values():  # Stop all servers
            UR.stop_server()
        observer.stop()
        time.sleep(1)  # Allow some time for all servers and tasks to stop
        running = False  # Stop the loop