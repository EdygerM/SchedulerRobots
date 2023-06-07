import socket
import time
import threading

# Define robot names and associated hosts and ports
robots_info = [
    {"name": "UR_Hplc", "host": "localhost", "port": 8001},
    {"name": "UR_Hplc2", "host": "localhost", "port": 8002},
    {"name": "UR_Synth", "host": "localhost", "port": 8003},
    {"name": "UR_Omni", "host": "localhost", "port": 8004},
    {"name": "UR_Sfc", "host": "localhost", "port": 8005},
    {"name": "UR_Nmr", "host": "localhost", "port": 8006},
]


class UniversalRobotSimulator:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        self.s = None
        self.stop_thread = False
        self.client_thread = None

    def start_client(self):
        def client_func():
            while not self.stop_thread:
                try:
                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.connect((self.host, self.port))
                    while not self.stop_thread:
                        data = self.s.recv(1024)
                        if not data:
                            break
                        print(f"Received task: {data.decode()}")
                        self.send_response(f"Task {data.decode()} done by {self.name}")
                except socket.error as e:
                    print(f"Connection error on {self.name}: {e}")
                    if self.s:
                        self.s.close()
                    print("Retrying in 5 seconds...")
                    time.sleep(5)

        self.client_thread = threading.Thread(target=client_func)
        self.client_thread.start()
        print(f"Client started for {self.name} on {self.host}:{self.port}")

    def stop_client(self):
        self.stop_thread = True
        if self.s:
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            print(f"Socket closed for {self.name}")
        if self.client_thread:
            self.client_thread.join()
        print(f"Client stopped for {self.name}")

    def send_response(self, message):
        time.sleep(1)  # simulate processing time
        self.s.sendall(message.encode())
        print(f"Response '{message}' sent.")


if __name__ == '__main__':
    UR_Sims = []
    for info in robots_info:
        UR_Sim = UniversalRobotSimulator(info["name"], info["host"], info["port"])
        UR_Sim.start_client()
        UR_Sims.append(UR_Sim)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Received keyboard interrupt, stopping clients...")
        for UR_Sim in UR_Sims:
            UR_Sim.stop_client()
        print("All clients stopped. Exiting.")
