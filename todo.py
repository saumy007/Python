import tkinter as tk
from tkinter import messagebox
import os

class StickyToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes To-Do")
        self.root.geometry("300x400")
        self.root.resizable(False, False)

        # Make the window frameless
        self.root.overrideredirect(True)

        # Add rounded corners using the canvas
        self.canvas = tk.Canvas(self.root, bg="#fdfd96", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Move window by dragging
        self.canvas.bind("<B1-Motion>", self.move_window)
        self.canvas.bind("<Button-1>", self.get_mouse_position)

        # Close button
        close_button = tk.Button(self.root, text="X", font=("Arial", 12, "bold"), fg="white", bg="#ff5f5f",
                                 command=self.root.destroy, bd=0)
        close_button.place(x=270, y=5, width=25, height=25)

        # Task list
        self.tasks = []

        # Task Entry
        self.task_entry = tk.Entry(self.root, font=("Arial", 12), bg="#fffaf0", bd=0)
        self.task_entry.place(x=10, y=40, width=280, height=30)
        self.task_entry.bind("<Return>", self.add_task)  # Add task on Enter key

        # Task Listbox
        self.task_listbox = tk.Listbox(self.root, font=("Arial", 12), bg="#fffaf0", bd=0, highlightthickness=0,
                                       selectbackground="#d4a5a5")
        self.task_listbox.place(x=10, y=80, width=280, height=300)
        self.task_listbox.bind("<Delete>", self.delete_task)  # Delete task on Delete key

        # Delete button
        delete_button = tk.Button(self.root, text="Delete", font=("Arial", 12), fg="white", bg="#ff6961",
                                  command=self.delete_task, bd=0)
        delete_button.place(x=10, y=360, width=280, height=30)

        self.load_tasks()

    def add_task(self, event=None):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append(task)
            self.update_listbox()
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Task cannot be empty!")

    def delete_task(self, event=None):
        try:
            selected_index = self.task_listbox.curselection()[0]
            del self.tasks[selected_index]
            self.update_listbox()
        except IndexError:
            messagebox.showwarning("Warning", "No task selected!")

    def update_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)

    def save_tasks(self):
        with open("tasks.txt", "w") as file:
            for task in self.tasks:
                file.write(task + "\n")

    def load_tasks(self):
        if os.path.exists("tasks.txt"):
            with open("tasks.txt", "r") as file:
                self.tasks = [line.strip() for line in file.readlines()]
            self.update_listbox()

    def move_window(self, event):
        self.root.geometry(f"+{event.x_root - self.offset_x}+{event.y_root - self.offset_y}")

    def get_mouse_position(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

if __name__ == "__main__":
    root = tk.Tk()
    StickyToDoApp(root)
    root.mainloop()
