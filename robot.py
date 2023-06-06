import errno
import socket
import time
import threading
from threading import Event
import logging
import platform


# Robot: Base class for all Robots with a common attribute of a unique name
class Robot:
    def __init__(self, name):
        self.name = name


# UniversalRobot: Class for Universal Robots that can host a server, send tasks, and wait for tasks to end
class UniversalRobot(Robot):
    def __init__(self, name, host, port):
        # Initiate UniversalRobot instance with a name, host, and port
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

        # server_func: Internal function to handle the server functionality
        def server_func():
            try:
                logging.info(f"Attempting to start server on {self.host}:{self.port} for {self.name}.")
                # Create a server socket, bind it, and set it to listen
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen()
                self.server_socket.setblocking(False)  # Set the socket to non-blocking mode
                self.is_server_running = True
                while self.is_server_running and self.server_socket is not None:
                    try:
                        # Accept any incoming connections
                        self.connection, addr = self.server_socket.accept()
                        logging.info(f'Connected by {addr} on {self.host}:{self.port} for {self.name}.')
                        self.connection_event.set()  # Signal that a connection has been made
                    except socket.error as e:
                        # Ignore the typical errors when no connection is made, and sleep before trying again
                        if platform.system() == 'Linux':
                            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                                raise
                        elif platform.system() == 'Windows':
                            if e.errno != errno.WSAEWOULDBLOCK and e.errno != errno.WSAECONNABORTED:
                                raise
                        time.sleep(1)
                    except Exception as e:
                        logging.error(f"An unexpected error occurred: {str(e)}")
            finally:
                # Close the server socket and connection when the server stops
                if self.server_socket is not None:
                    self.server_socket.close()
                    self.server_socket = None
                logging.info("Server function exited.")

        # Start a thread for the server function
        server_thread = threading.Thread(target=server_func)
        server_thread.start()
        logging.info(f"Server started on {self.host}:{self.port} for {self.name}.")

    def stop_server(self):
        """
        Stop the server and close the connection and the socket.
        """

        self.stop_flag = True  # Set the stop flag when stopping the server
        self.is_server_running = False
        logging.info(f"Server stopped on {self.host}:{self.port} for {self.name}.")

    def send_task(self, task):
        """
        Sends a task to the robot's server.
        """

        try:
            logging.info(f"Attempting to send task '{task}' to {self.name}.")
            # Send the task as an encoded string to the server
            self.connection.sendall(task.encode())
            logging.info(f"Task '{task}' sent to {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while sending task '{task}' to {self.name}: {str(e)}")

    def wait_task_end(self):
        """
        Waits for the task to end. This is simulated by waiting for a message from the server.
        """

        while True:
            try:
                data = self.connection.recv(1024)
                if data:
                    logging.info(f"Task ended. Received message: {data.decode()}")
                    break
            except Exception as e:
                logging.error(f"An error occurred while waiting for the task to end: {str(e)}")
            time.sleep(1)

    def wait_for_connection(self):
        """
        Wait for a connection to the server. This function blocks until a connection is established.
        """

        while not self.is_connected() and not self.stop_flag:
            time.sleep(1)
            logging.info(f"Waiting for connection to {self.name}")

    def is_connected(self):
        """
        Checks if the robot is currently connected to a client.
        """

        if self.connection is None:
            return False
        try:
            # Try to send an empty message to check the connection
            if platform.system() == 'Linux':
                self.connection.send(b'', socket.MSG_DONTWAIT)
            elif platform.system() == 'Windows':
                self.connection.setblocking(False)
                try:
                    self.connection.send(b'')
                finally:
                    self.connection.setblocking(True)
            return True
        except socket.error as e:
            # Broken pipe or connection reset errors mean the client has disconnected
            if e.errno in [errno.EPIPE, errno.ECONNRESET, errno.WSAECONNRESET, errno.WSAESHUTDOWN]:
                return False
            else:
                raise


# MobileRobot: Class for Mobile Robots that can send tasks and wait for tasks to end
class MobileRobot(Robot):
    def __init__(self, name):
        # Initiate MobileRobot instance with a name
        super().__init__(name)

    def send_task(self, task):
        """
        Sends a task to the mobile robot.
        """

        try:
            logging.info(f"Attempting to send task '{task}' to {self.name}.")
            time.sleep(1)  # Simulate the time it takes to send a task
            logging.info(f"Task '{task}' sent to {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while sending task '{task}' to {self.name}: {str(e)}")

    def wait_task_end(self, task):
        """
        Waits for a task to end. This is simulated with a sleep command.
        """

        try:
            logging.info(f"Waiting task '{task}' ending from {self.name}.")
            time.sleep(1)  # Simulate the time it takes for a task to end
            logging.info(f"Task '{task}' ended from {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while waiting for the task '{task}' to end from {self.name}: {str(e)}")
