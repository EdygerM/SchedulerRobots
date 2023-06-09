import socket
import time
import threading
from threading import Event
import logging


class SocketServer:
    def __init__(self, name, host, port):
        self.name = name
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
                try:
                    self.server_socket.bind((self.host, self.port))
                except OSError as e:
                    logging.error(f"An error occurred while binding the server socket: {str(e)}")
                    raise e
                self.server_socket.listen()
                self.server_socket.settimeout(1.0)  # Set a timeout of 1 second for the accept call
                self.is_server_running = True
                disconnected_logged = False
                while self.is_server_running and self.server_socket is not None:
                    try:
                        # Check if there is no connection or the current connection is closed
                        if self.connection is None or self.is_client_disconnected():
                            if not disconnected_logged:
                                logging.info(f"Client of {self.name} has closed the connection.")
                                disconnected_logged = True
                            self.connection, addr = self.server_socket.accept()
                            logging.info(f'Connected by {addr} on {self.host}:{self.port} for {self.name}.')
                            self.connection_event.set()  # Signal that a connection has been made
                            disconnected_logged = False
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
        self.stop_flag = True
        self.is_server_running = False
        if self.connection is not None:
            try:
                self.connection.close()
                logging.info("Connection closed.")
            except Exception as e:
                logging.error(f"An error occurred while closing the connection: {str(e)}")
        logging.info(f"Server stopped on {self.host}:{self.port} for {self.name}.")

    def send_data(self, data):
        """
        """

        try:
            logging.info(f"Attempting to send message '{data}' to {self.name}.")
            # Wait for the client to connect before sending the task
            while self.connection is None or self.is_client_disconnected():
                logging.info(f"Waiting for the client to connect to send message '{data}' to {self.name}.")
                time.sleep(1)  # Wait for a second before checking again
            # Send the task as an encoded string to the server
            self.connection.sendall(data.encode())
            logging.info(f"message '{data}' sent to {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while sending message '{data}' to {self.name}: {str(e)}")

    def wait_data(self):
        """
        """

        while True:
            try:
                data = self.connection.recv(1024)
                if data:
                    logging.info(f"Received message: {data.decode()}")
                    break
            except Exception as e:
                logging.error(f"An error occurred while waiting for the data: {str(e)}")
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
            logging.info(f"No connection object for {self.name}.")
            return True

        try:
            # Set the socket to non-blocking
            self.connection.setblocking(0)

            # Make a zero-byte send call
            self.connection.send(b'')

            # If we've gotten here, then the send call didn't raise an error,
            # so the socket is still connected
            return False
        except BlockingIOError:
            # This error means the operation would have blocked if the socket was blocking,
            # which in turn means that the socket is still connected
            return False
        except Exception:
            # If any other exception was raised, then the socket is probably disconnected
            return True
