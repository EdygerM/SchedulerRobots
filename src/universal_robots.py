import logging
from file_loader import load_json_file
from socket_server import SocketServer


class UniversalRobots(SocketServer):
    def __init__(self, name, host, port):
        logging.info(f"Creating UniversalRobot instance for {name} "
                     f"with host {host} "
                     f"and port {port}.")
        super().__init__(name, host, port)
        self.start_server()

    def send_task(self, task):
        """
        Sends a task to the robot's server.
        """

        self.send_data(task)

    def wait_task_end(self):
        """
        Waits for the task to end.
        """

        self.wait_data()
