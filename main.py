import json
import time
from watchdog.observers import Observer
from robot import UniversalRobot
from robot_handler import RobotHandler

if __name__ == '__main__':
    # Load Universal Robot (ur) setup from json file
    with open('setup_universal_robot.json', 'r') as setup_file:
        setup_ur = json.load(setup_file)

    # For each ur, create an instance and start a server
    ur_dict = {}
    for info in setup_ur:
        ur = UniversalRobot(info["name"], info["host"], info["port"])
        ur.start_server()
        ur_dict[info["name"]] = ur

    # Set up file system monitoring for specified directory
    input_path = "/home/mariano/Music"  # Directory to watch
    handler = RobotHandler(ur_dict)
    observer = Observer()
    observer.schedule(handler, input_path, recursive=False)
    observer.start()
    running = True

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupt received! Stopping servers.")
    finally:
        for path in handler.path_list:  # Stop all tasks
            path.stop_tasks()
        for UR in ur_dict.values():  # Stop all servers
            UR.stop_server()
        observer.stop()
        time.sleep(1)  # Allow some time for all servers and tasks to stop
        running = False  # Stop the loop
