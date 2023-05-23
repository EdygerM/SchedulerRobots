import errno
import socket
import json
import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from threading import Event


# Base class for all Robots with a common attribute of a unique name
class Robot:
    def __init__(self, name):
        self.name = name


# Class for Universal Robots that can host a server, send tasks and wait for tasks to end
class UniversalRobot(Robot):
    def __init__(self, name, host, port):
        super().__init__(name)
        self.host = host
        self.port = port
        self.connection = None
        self.server_socket = None
        self.is_server_running = False
        self.stop_thread = False
        self.connection_event = Event()

    def start_server(self):
        """
        Start a server that listens for incoming connections in a separate thread.
        Non-blocking mode is used, i.e., the server does not block waiting for connections.
        """

        def server_func():
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            self.server_socket.setblocking(False)  # set the socket to non-blocking mode
            self.is_server_running = True
            while self.is_server_running:
                try:
                    self.connection, addr = self.server_socket.accept()
                    print(f'Connected by {addr}')
                    self.connection_event.set()  # Signal that a connection has been made
                except socket.error as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        raise
                    time.sleep(1)  # No connection, sleep for a while and try again
                except Exception as e:
                    print(f"An error occurred: {e}")
            self.server_socket.close()
            print("Server function exited.")

        server_thread = threading.Thread(target=server_func)
        server_thread.start()
        print(f"Server started on {self.host}:{self.port}")

    def stop_server(self):
        """
        Stop the server and close the connection and the socket.
        """

        self.is_server_running = False
        if self.connection:
            self.connection.close()
        if self.server_socket:
            self.server_socket.close()
        print(f"Server stopped on {self.host}:{self.port}")

    def send_task(self, task):
        """
        Sends a task to the robot's server.
        """

        try:
            self.connection.sendall(task.encode())
            print(f"Task '{task}' sent to {self.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def wait_task_end(self, task):
        """
        Waits for a task to end. The function blocks until a response is received from the server.
        """

        print(f"Waiting task '{task}' ending from {self.name}")
        while True:
            if self.connection is None:
                time.sleep(1)
                continue
            data = self.connection.recv(1024)
            if data:
                print(f"Task ended. Received message: {data.decode()}")
                break
            time.sleep(1)


# Class for Mobile Robots that can send tasks and wait for tasks to end
class MobileRobot(Robot):
    def __init__(self, name):
        super().__init__(name)

    def send_task(self, task):
        print(f"Sending task '{task}' to {self.name}")
        time.sleep(1)  # Simulate the time it takes to send a task

    def wait_task_end(self, task):
        print(f"Waiting task '{task}' ending from {self.name}")
        time.sleep(1)  # Simulate the time it takes for a task to end


# Class for a Path that has a series of tasks that can be executed by the robots
class Path:
    def __init__(self, ID, Name, StartPosition, EndPosition, Action, PlateNumber, handler, task_queue=None):
        self.ID = ID
        self.Name = Name
        self.StartPosition = StartPosition
        self.EndPosition = EndPosition
        self.Action = Action
        self.PlateNumber = PlateNumber
        self.handler = handler
        self.EM = MobileRobot("EM")  # Mobile robot
        self.task_queue = task_queue or self.initialize_task_queue()
        self.stop_thread = False

    def initialize_task_queue(self):
        """
        Initialize the task queue with tasks for the robots
        """

        return [(self.EM, f"EM_to_{self.StartPosition}", "NotDone"),
                (robots_dict[("UR_" + self.StartPosition)], "Place", "NotDone"),
                (self.EM, f"EM_{self.StartPosition}_to_{self.EndPosition}", "NotDone"),
                (robots_dict[("UR_" + self.EndPosition)], "Pick", "NotDone")]

    def execute_tasks(self):
        """
        Execute tasks in the task queue one by one. If the task queue is empty, remove this path from the handler.
        """

        while self.task_queue and not self.stop_thread:
            robot, task, state = self.task_queue[0]
            if state == "NotDone":
                robot.send_task(task)
                self.task_queue[0] = (robot, task, "IsDoing")
                self.handler.save_state()
            elif state == "IsDoing":
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


# Class for a handler that handles file system events and maintains a list of paths
class PathHandler(PatternMatchingEventHandler):
    patterns = ["*.json"]

    def __init__(self):
        super().__init__()
        self.path_list = []
        self.load_state()

    def process(self, event):
        """
        Process a new json file, create a new Path object and start executing its tasks.
        """

        with open(event.src_path, 'r') as file:
            data = json.load(file)
            for path in data['paths']:
                path_obj = Path(path['ID'], path['Name'], path['StartPosition'],
                                path['EndPosition'], path['Action'], path['PlateNumber'], self)
                self.path_list.append(path_obj)
                threading.Thread(target=path_obj.execute_tasks).start()

    def print_all_names(self):
        """
        Print the names of all path objects. This is useful for debugging.
        """
        for path_obj in self.path_list:
            print(path_obj.name)

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

        with open('state.json', 'w') as f:
            paths_to_save = [p for p in self.path_list if p.task_queue]
            json.dump([p.to_dict() for p in paths_to_save], f, indent=4)

    def load_state(self):
        """
        Load state from a file.
        """

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
            pass

    def stop_all_tasks(self):
        """
        Stop executing all tasks.
        """

        for path in self.path_list:
            path.stop_tasks()


if __name__ == '__main__':

    # Load robot info from json file and create an instance for each robot and start the server
    with open('setup_universal_robot.json', 'r') as f:
        robots_info = json.load(f)

    robot_instances = {}
    for info in robots_info:
        UR = UniversalRobot(info["name"], info["host"], info["port"])
        UR.start_server()
        robot_instances[info["name"]] = UR

    # Define robots_dict
    robots_dict = {}
    for name, instance in robot_instances.items():
        robots_dict[name] = instance

    # Wait for all UR servers to accept at least one connection each
    for UR in robot_instances.values():
        UR.connection_event.wait()

    input_path = "/home/mariano/Music"  # Directory to watch
    handler = PathHandler()
    observer = Observer()
    observer.schedule(handler, input_path, recursive=False)
    observer.start()
    running = True

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        handler.print_all_names()
        for path in handler.path_list:  # Stop all tasks
            path.stop_tasks()
        for UR in robot_instances.values():  # Stop all servers
            UR.stop_server()
        observer.stop()
        time.sleep(1)  # Allow some time for all servers and tasks to stop
        running = False  # Stop the loop
