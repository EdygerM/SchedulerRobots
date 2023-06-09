import tkinter as tk
from tkinter import ttk


class Application(tk.Tk):
    def __init__(self, robot_instances, handler):
        tk.Tk.__init__(self)
        self.tree = None
        self.title('Robot Status')
        self.geometry('300x200')
        self.robot_instances = robot_instances
        self.handler = handler
        self.create_widgets()
        self.refresh()  # Refresh robot statuses immediately upon start

    def create_widgets(self):
        self.tree = ttk.Treeview(self)

        # Define columns
        self.tree['columns'] = ('Status', 'Path')

        # Format columns
        self.tree.column('#0', width=120, minwidth=25)
        self.tree.column('Status', anchor='w', width=120, minwidth=25)
        self.tree.column('Path', anchor='w', width=120, minwidth=25)

        # Create headings
        self.tree.heading('#0', text='Robot', anchor='w')
        self.tree.heading('Status', text='Status', anchor='w')
        self.tree.heading('Path', text='Path', anchor='w')

        self.tree.pack()

    def refresh(self):
        # Delete all current items in the tree view
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Prepare list of path names
        path_names = [path.Name for path in self.handler.path_list]

        # Re-add items with updated statuses
        for robot in self.robot_instances:
            status = 'Connected' if self.robot_instances[robot].is_connected() else 'Not Connected'
            # If there are paths, add the first one to the current robot and remove it from the list
            path_name = path_names.pop(0) if path_names else 'No Path'
            self.tree.insert('', 'end', text=robot, values=(status, path_name))  # Note the comma to make it a tuple

        # Schedule next refresh
        self.after(1000, self.refresh)
