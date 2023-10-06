from universal_robots import UniversalRobots
import logging
import time

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class RobotHandler:
    def __init__(self):
        super().__init__()
        self.urSFC = UniversalRobots("UR_SFC", "172.31.0.14", 7993)
        self.urNMR = UniversalRobots("UR_NMR", "172.31.0.14", 7992)
        self.pcNMR = UniversalRobots("PC_NMR", "172.31.0.14", 8001)

        self.urSFC.start_server()
        self.urNMR.start_server()
        self.pcNMR.start_server()


if __name__ == '__main__':
    try:
        logging.info("Starting main loop.")
        Robots = RobotHandler()
        input("Input any key when the robots are connected.")
        print("Program running")
        running = True
        while running:
            Robots.urSFC.send_task("PickStorageNmr")
            Robots.urSFC.wait_task_end()
            Robots.urSFC.send_task("PlaceStorageNmr")
            Robots.urSFC.wait_task_end()
            Robots.urNMR.send_task("PickStorage")
            Robots.urNMR.wait_task_end()
            Robots.urNMR.send_task("PlaceStorage")
            Robots.urNMR.wait_task_end()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.exception("Interrupt received! Stopping servers.")
    finally:

        time.sleep(1)  # Allow some time for all servers and tasks to stop
        running = False  # Stop the loop
