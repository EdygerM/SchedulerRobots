import logging
from watchdog.observers import Observer
from src.robot_handler import TaskHandler
from universal_robot import UniversalRobot
from utility import load_json_file
from config import Config

config = Config()


class SchedulerRobot:
    def __init__(self):
        self.ur_robots = {}
        self.setup_universal_robots(config.get('GENERAL', 'UR_SETUP_FILE'))
        self.handler = TaskHandler(self.ur_robots)
        self.observer = Observer()
        self.observer.schedule(self.handler, config.get('GENERAL', 'INPUT_PATH'), recursive=False)
        self.observer.start()

    def setup_universal_robots(self, ur_setup_file):
        for info in load_json_file(ur_setup_file):
            try:
                logging.info(f"Creating UniversalRobot instance for {info['name']} with host {info['host']}"
                             f" and port {info['port']}.")
                ur = UniversalRobot(info["name"], info["host"], info["port"])
                self.ur_robots[info["name"]] = ur

                logging.info(f"Starting server for {info['name']}.")
                ur.start_server()
                logging.info(f"Server for {info['name']} started successfully.")

            except Exception as e:
                logging.error(f"An error occurred while setting up {info['name']}: {str(e)}")

    def stop_all(self):
        logging.info("Stopping all.")
        self.stop_tasks()
        self.stop_servers()
        self.stop_observer()

    def stop_tasks(self):
        logging.info("Attempting to stop all tasks.")
        for path in self.handler.path_list:
            try:
                path.stop_tasks()
                logging.info(f"Stopped tasks for path {path}")
            except Exception as e:
                logging.error(f"An error occurred while stopping tasks for path {path}: {str(e)}")

    def stop_servers(self):
        logging.info("Attempting to stop all servers.")
        for UR in self.ur_robots.values():
            try:
                UR.stop_server()
                logging.info(f"Server for {UR.name} stopped successfully.")
            except Exception as e:
                logging.error(f"An error occurred while stopping server for {UR.name}: {str(e)}")

    def stop_observer(self):
        logging.info("Stopping observer.")
        try:
            self.observer.stop()
        except Exception as e:
            logging.error(f"An error occurred while stopping observer: {str(e)}")
