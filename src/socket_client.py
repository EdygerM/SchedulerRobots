import socket
import time
import logging


class SocketClient:
    def __init__(self, name, server_host, server_port):
        self.name = name
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None
        self.is_connected = False

    def connect(self):
        """
        Connect to the server.
        """
        try:
            logging.info(f"Attempting to connect to {self.server_host}:{self.server_port} as {self.name}.")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_host, self.server_port))
            self.is_connected = True
            logging.info(f"Connected to {self.server_host}:{self.server_port} as {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while connecting: {str(e)}")

    def disconnect(self):
        """
        Disconnect from the server.
        """
        if self.client_socket:
            try:
                self.client_socket.close()
                logging.info(f"Disconnected from {self.server_host}:{self.server_port} as {self.name}.")
            except Exception as e:
                logging.error(f"An error occurred while disconnecting: {str(e)}")
            self.is_connected = False

    def send_data(self, data):
        """
        Send data to the server.
        """
        if not self.is_connected:
            logging.warning("Not connected to the server.")
            return

        try:
            logging.info(f"Attempting to send message '{data}' from {self.name}.")
            self.client_socket.sendall(data.encode())
            logging.info(f"Message '{data}' sent from {self.name}.")
        except Exception as e:
            logging.error(f"An error occurred while sending message '{data}' from {self.name}: {str(e)}")

    def receive_data(self):
        """
        Receive data from the server.
        """
        if not self.is_connected:
            logging.warning("Not connected to the server.")
            return

        try:
            data = self.client_socket.recv(1024)
            if data:
                logging.info(f"Received message: {data.decode()}")
                return data.decode()
        except Exception as e:
            logging.error(f"An error occurred while receiving data for {self.name}: {str(e)}")
            return None
