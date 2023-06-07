# Project Title: Universal Robot File System Monitor

## Description
This project is a Python-based application designed to monitor a specific directory for changes and interact with one or more Universal Robots based on those changes. Universal Robots are a brand of robotic arms used for industrial applications. 

The script leverages the watchdog package to monitor a specified file directory and triggers actions on the Universal Robots when file changes are detected. The robot configurations, such as host and port, are stored in a JSON file.

The project uses logging to provide a transparent and trackable operation trail, useful for debugging and understanding the application's workflow.

## Getting Started
### Prerequisites
- Python 3.7 or later
- The `watchdog` Python package
- Universal Robots accessible through a network
- A directory with files that you want to monitor

### Setup
1. Clone or download the project to your local machine.
2. Install the required packages: `watchdog`.
3. Update the `setup_universal_robot.json` file with the necessary details for your Universal Robots.
4. Update the `INPUT_PATH` in the `main.py` file to the directory you want to monitor.

## Usage
1. Run `main.py` to start the application.
2. The script will log the start of the script, the initiation and server start of each Universal Robot, and the start of the file system observer.
3. The script will continue to run, logging any changes in the monitored directory and any resulting actions on the Universal Robots.
4. Stop the script with a KeyboardInterrupt (usually Ctrl+C in the terminal), and the script will log the stop of all tasks, the stop of all servers, and the stop of the observer before logging the end of the script.

## Function Overview
- `setup_universal_robots()`: This function initializes instances of Universal Robots based on the details provided in the setup file and starts their servers. Each robot's details are logged as they are initiated and started.
- `stop_tasks(handler)`: This function stops all tasks handled by the given robot handler.
- `stop_servers(ur_dict)`: This function stops all Universal Robot servers.
- `stop_observer(observer)`: This function stops the observer instance which monitors the file system.

## Project Structure
- `main.py`: The main script for running the application.
- `setup_universal_robot.json`: A JSON file containing the setup details for each Universal Robot.
- `robot.py`: The file contains the `UniversalRobot` class.
- `robot_handler.py`: The file contains the `RobotHandler` class.
- `utility.py`: The file contains utility functions like `load_json_file`.

## Notes
This project is designed to work with Universal Robots. If you're working with a different type of robot, the `UniversalRobot` class and `setup_universal_robots()` function in `main.py` will need to be adjusted accordingly.

This script is designed to run continuously until stopped manually. If you want to run it for a specific amount of time or until a specific condition is met, you'll need to modify the `while` loop in the `if __name__ == '__main__':` section.

## Contact Information
For further queries or if you encounter any issues, please contact [Your Name] at [Your Email].
