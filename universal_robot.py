from socket_server import SocketServer


class UniversalRobot(SocketServer):
    def __init__(self, name, host, port):
        super().__init__(name, host, port)

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