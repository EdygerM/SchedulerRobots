import errno
import socket
import time
import threading
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
        self.stop_flag = False

    def start_server(self):
        """
        Start a server that listens for incoming connections in a separate thread.
        Non-blocking mode is used, i.e., the server does not block waiting for connections.
        """

        def server_func():
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen()
                self.server_socket.setblocking(False)  # set the socket to non-blocking mode
                self.is_server_running = True
                while self.is_server_running and self.server_socket is not None:
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
            finally:
                if self.server_socket is not None:
                    self.server_socket.close()
                    self.server_socket = None
                if self.connection is not None:
                    self.connection.close()
                    self.connection = None
                print("Server function exited.")

        server_thread = threading.Thread(target=server_func)
        server_thread.start()
        print(f"Server started on {self.host}:{self.port}")

    def stop_server(self):
        """
        Stop the server and close the connection and the socket.
        """

        self.stop_flag = True  # Set the stop flag when stopping the server
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

    def wait_for_connection(self):
        """
        Wait for a connection to the server. This function blocks until a connection is established.
        """

        while not self.is_connected() and not self.stop_flag:
            time.sleep(1)
            print(f"Waiting for connection to {self.name}")

    def is_connected(self):
        """
        Checks if the robot is currently connected to a client.
        """
        if self.connection is None:
            return False
        try:
            self.connection.send(b'', socket.MSG_DONTWAIT)  # Try to send an empty message
            return True
        except socket.error as e:
            if e.errno == errno.EPIPE or e.errno == errno.ECONNRESET:  # Broken pipe or connection reset errors mean the client has disconnected
                return False
            else:
                raise


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
