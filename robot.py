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
        """

        # server_func: Internal function to handle the server functionality
        def server_func():
            try:
                logging.info(f"Attempting to start server on {self.host}:{self.port} for {self.name}.")
                # Create a server socket, bind it, and set it to listen
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen()
                self.server_socket.settimeout(1.0)  # Set a timeout of 1 second for the accept call
                self.is_server_running = True
                while self.is_server_running and self.server_socket is not None:
                    try:
                        # Check if there is no connection or the current connection is closed
                        if self.connection is None or self.is_client_disconnected():
                            self.connection, addr = self.server_socket.accept()
                            logging.info(f'Connected by {addr} on {self.host}:{self.port} for {self.name}.')
                            self.connection_event.set()  # Signal that a connection has been made
                    except socket.timeout:
                        # If no client connected within the timeout period, just continue and try again
                        continue
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
            # Wait for the client to connect before sending the task
            while self.connection is None or self.is_client_disconnected():
                logging.info(f"Waiting for the client to connect to send task '{task}' to {self.name}.")
                time.sleep(1)  # Wait for a second before checking again
            # Send the task as an encoded string to the server
            self.connection.sendall(task.encode())
            logging.info(f"Task '{task}' sent to {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while sending task '{task}' to {self.name}: {str(e)}")

    def wait_task_end(self, task):
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

        while self.is_client_disconnected() and not self.stop_flag:
            time.sleep(1)
            logging.info(f"Waiting for connection to {self.name}")

    # Helper function to check if the client is disconnected
    def is_client_disconnected(self):
        if self.connection is None:
            return True

        try:
            # Try to receive data, with the MSG_PEEK flag to not consume any data from the buffer
            data = self.connection.recv(1024, socket.MSG_PEEK)
        except ConnectionResetError:
            # The client has disconnected
            return True
        except BlockingIOError:
            # The socket is still connected and has no data to receive
            return False
        # If no exception was raised, check if the client has closed the connection
        return len(data) == 0


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
