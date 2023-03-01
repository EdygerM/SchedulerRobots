from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from configparser import ConfigParser
import time


class OnMyWatch:
    # Set the directory on watch
    watchDirectory = "/home/mariano/Music"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1500)
                print("Still running")
        except:
            self.observer.stop()
            print("Observer Stopped")
        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
            if "txt" in event.src_path:
                labTasks = []
                robotTasks = []
                taskList = []
                with open(event.src_path) as f:
                    # Read the tasks sent by the Laboratory Scheduler and store them in a list (LabSchedulerTasks)
                    for line in f:
                        labTasks.append(line.replace("\n", ""))
                    print("Laboratory Tasks are:")
                    print(labTasks)

                    # Translate Lab Tasks in Robot Tasks
                    parser = ConfigParser()
                    parser.read("taskConfig.ini")
                    for path in labTasks:
                        robotTasks.append(parser.get('Task', path).split(","))
                    print("Robot Tasks are:")
                    print(robotTasks)

                    # Create a Tasklist with status NotDone
                    taskNumber = 0
                    for labTask in robotTasks:
                        for robotTask in labTask:
                            taskList.append([taskNumber, robotTask, "NotDone"])
                            taskNumber += 1
                    print(taskList)
                    time.sleep(3)


            # for taskLo in taskList:
            #     for taskL in taskLo:
            #
            #         #fait passer à ToBeDone si le robot est dispo
            #         robotStatus = #call robot
            #         while robotStatus =! "Available"
            #
            #         if taskL[2] = "ToBeDone" :
            #             #Send to UR or EM
            #             if success :
            #                 taskL[2] = "Done"

            print("!! Sequence complete !!")
            # move file to "Done" folder

            print("ENG PROG")


if __name__ == '__main__':
    print("STARTING PROGRAM")
    watch = OnMyWatch()
    watch.run()
