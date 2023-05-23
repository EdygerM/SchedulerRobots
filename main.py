import json
import time
from watchdog.observers import Observer
from robot import UniversalRobot
from path_handler import PathHandler

if __name__ == '__main__':
    # Load robot info from json file, create an instance for each robot and start the server
    with open('setup_universal_robot.json', 'r') as setup_file:
        setup_ur = json.load(setup_file)

    robot_instances = {}
    for info in setup_ur:
        ur = UniversalRobot(info["name"], info["host"], info["port"])
        ur.start_server()
        robot_instances[info["name"]] = ur

    # Define robots_dict
    robots_dict = {}
    for name, instance in robot_instances.items():
        robots_dict[name] = instance

    input_path = "/home/mariano/Music"  # Directory to watch
    handler = PathHandler(robots_dict)
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
        handler.print_all_names()
        for path in handler.path_list:  # Stop all tasks
            path.stop_tasks()
        for UR in robot_instances.values():  # Stop all servers
            UR.stop_server()
        observer.stop()
        time.sleep(1)  # Allow some time for all servers and tasks to stop
        running = False  # Stop the loop
