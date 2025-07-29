\"""Todo application module for thefirstpackage"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os


class TodoApp:
    """A simple Todo application with a graphical user interface"""
    
    def __init__(self, root):
        """Initialize the Todo application
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Simple Todo App")
        self.root.geometry("500x450")
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f5f5")

        # Data storage
        self.tasks = []
        self.load_tasks()

        # Main frame
        self.main_frame = tk.Frame(root, bg="#f5f5f5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # App title
        self.title_label = tk.Label(
            self.main_frame, 
            text="Todo List", 
            font=("Arial", 18, "bold"),
            bg="#f5f5f5",
            fg="#333333"
        )
        self.title_label.pack(pady=(0, 20))

        # Task entry
        self.entry_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        self.entry_frame.pack(fill=tk.X, pady=10)

        self.task_entry = tk.Entry(
            self.entry_frame, 
            font=("Arial", 12),
            bd=2,
            relief=tk.GROOVE,
            width=30
        )
        self.task_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        self.add_button = tk.Button(
            self.entry_frame, 
            text="Add Task", 
            command=self.add_task,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=10,
            pady=5
        )
        self.add_button.pack(side=tk.LEFT)

        # Task list frame
        self.list_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.SOLID)
        self.list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Task listbox
        self.task_listbox = tk.Listbox(
            self.list_frame, 
            font=("Arial", 12),
            bg="white",
            fg="#333333",
            selectbackground="#a6a6a6",
            activestyle="none",
            height=10,
            yscrollcommand=self.scrollbar.set
        )
        self.task_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.scrollbar.config(command=self.task_listbox.yview)

        # Buttons frame
        self.buttons_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        self.buttons_frame.pack(fill=tk.X, pady=10)

        self.complete_button = tk.Button(
            self.buttons_frame, 
            text="Mark Complete", 
            command=self.mark_complete,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10),
            bd=0,
            padx=10,
            pady=5
        )
        self.complete_button.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_button = tk.Button(
            self.buttons_frame, 
            text="Delete Task", 
            command=self.delete_task,
            bg="#f44336",
            fg="white",
            font=("Arial", 10),
            bd=0,
            padx=10,
            pady=5
        )
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(
            self.buttons_frame, 
            text="Clear All", 
            command=self.clear_all,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 10),
            bd=0,
            padx=10,
            pady=5
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("0 tasks pending")
        self.status_bar = tk.Label(
            self.main_frame, 
            textvariable=self.status_var,
            font=("Arial", 10),
            bg="#f5f5f5",
            fg="#666666",
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

        # Load tasks into listbox
        self.refresh_listbox()

    def add_task(self):
        """Add a new task to the list"""
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append({"task": task, "completed": False})
            self.task_entry.delete(0, tk.END)
            self.refresh_listbox()
            self.save_tasks()
        else:
            messagebox.showwarning("Warning", "Please enter a task!")

    def mark_complete(self):
        """Mark the selected task as complete or incomplete"""
        try:
            index = self.task_listbox.curselection()[0]
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.refresh_listbox()
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task!")

    def delete_task(self):
        """Delete the selected task"""
        try:
            index = self.task_listbox.curselection()[0]
            del self.tasks[index]
            self.refresh_listbox()
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task!")

    def clear_all(self):
        """Clear all tasks after confirmation"""
        if messagebox.askyesno("Confirmation", "Are you sure you want to clear all tasks?"):
            self.tasks = []
            self.refresh_listbox()
            self.save_tasks()

    def refresh_listbox(self):
        """Refresh the task listbox with current tasks"""
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            task_text = task["task"]
            if task["completed"]:
                self.task_listbox.insert(tk.END, f"✓ {task_text}")
                self.task_listbox.itemconfig(self.task_listbox.size() - 1, fg="#888888")
            else:
                self.task_listbox.insert(tk.END, f"  {task_text}")
        
        # Update status bar
        pending_count = sum(1 for task in self.tasks if not task["completed"])
        self.status_var.set(f"{pending_count} tasks pending")

    def save_tasks(self, filename="todo_tasks.json"):
        """Save tasks to a JSON file
        
        Args:
            filename (str): Path to the JSON file
        """
        with open(filename, "w") as f:
            json.dump(self.tasks, f)

    def load_tasks(self, filename="todo_tasks.json"):
        """Load tasks from a JSON file
        
        Args:
            filename (str): Path to the JSON file
        """
        try:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    self.tasks = json.load(f)
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []


def run_app():
    """Run the Todo application"""
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()