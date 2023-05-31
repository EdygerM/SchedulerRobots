import time
from watchdog.observers import Observer
from robot import UniversalRobot
from robot_handler import RobotHandler
import logging
from utility import load_json_file

# UR_SETUP_FILE: The file containing the setup information for Universal Robots
UR_SETUP_FILE = "setup_universal_robot.json"

# INPUT_PATH: The directory which the program will monitor for changes
INPUT_PATH = "/home/mariano/Music"


# Configure the logging settings
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)


# setup_universal_robots: Initializes Universal Robot instances based on the UR_SETUP_FILE and starts their servers
def setup_universal_robots():
    ur_dict = {}
    # Load the setup information from the JSON file
    setup_ur = load_json_file(UR_SETUP_FILE)
    for info in setup_ur:
        try:
            # Log the initiation of a new UniversalRobot instance
            logging.info(
                f"Creating UniversalRobot instance for {info['name']} with host {info['host']} and port {info['port']}.")
            ur = UniversalRobot(info["name"], info["host"], info["port"])
            ur_dict[info["name"]] = ur

            # Start the server for the new UniversalRobot instance and log its status
            logging.info(f"Starting server for {info['name']}.")
            ur.start_server()
            logging.info(f"Server for {info['name']} started successfully.")

        except Exception as e:
            # Log any errors that occur during setup
            logging.error(f"An error occurred while setting up {info['name']}: {str(e)}")
    return ur_dict


# stop_tasks: Stops all tasks handled by the given robot handler
def stop_tasks(handler):
    logging.info("Attempting to stop all tasks.")
    for path in handler.path_list:  # Stop all tasks
        try:
            path.stop_tasks()
            logging.info(f"Stopped tasks for path {path}")
        except Exception as e:
            logging.error(f"An error occurred while stopping tasks for path {path}: {str(e)}")


# stop_servers: Stops all Universal Robot servers
def stop_servers(ur_dict):
    logging.info("Attempting to stop all servers.")
    for UR in ur_dict.values():  # Stop all servers
        try:
            UR.stop_server()
            logging.info(f"Server for {UR.name} stopped successfully.")
        except Exception as e:
            logging.error(f"An error occurred while stopping server for {UR.name}: {str(e)}")


# stop_observer: Stops the Observer instance
def stop_observer(observer):
    logging.info("Stopping observer.")
    try:
        observer.stop()
    except Exception as e:
        logging.error(f"An error occurred while stopping observer: {str(e)}")


if __name__ == '__main__':
    # Initialize Universal Robot instances and start their servers
    ur_instance = setup_universal_robots()

    # Set up file system monitoring for specified directory
    robotHandler = RobotHandler(ur_instance)
    schedulerObserver = Observer()

    # Schedule the robotHandler to watch for changes in the input_path
    schedulerObserver.schedule(robotHandler, INPUT_PATH, recursive=False)
    schedulerObserver.start()
    running = True

    try:
        logging.info("Starting main loop.")
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.exception("Interrupt received! Stopping servers.")
    finally:
        # Stop all tasks, servers, and observer in the event of a KeyboardInterrupt or other exit
        stop_tasks(robotHandler)
        stop_servers(ur_instance)
        stop_observer(schedulerObserver)

        time.sleep(1)  # Allow some time for all servers and tasks to stop
        running = False  # Stop the loop
        logging.info("Main loop stopped.")
