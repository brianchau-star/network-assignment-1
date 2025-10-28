import tkinter as tk
from tkinter import filedialog, messagebox

import sys

class RedirectedText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text, tag=None):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text, tag)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.yview(tk.END)

    def flush(self):
        pass  # No need to flush for this example

class MainScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.list_container = tk.Frame(self)
        self.list_container.grid_columnconfigure(0,weight=1)
        self.list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=32)

        self.file_listbox = tk.Listbox(self.list_container, selectmode=tk.SINGLE)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.log_space = tk.Text(self.list_container, wrap=tk.WORD, state=tk.DISABLED)
        self.log_space.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=4)

        # Print to log space
        sys.stdout = RedirectedText(self.log_space)

        label = tk.Label(self, text="Choose a file", font=("Arial", 18))
        label.pack(pady=20,fill=tk.X)

        download_button = tk.Button(self, text="Publish", command=self.open_popup)
        download_button.pack(pady=10, padx=10)

        tk.Button(self, text="Refresh", command= self.fetch_local_list).pack(pady=10, padx=10)

    def start_screen(self):
        self.fetch_local_list()

    def fetch_local_list(self):
        if self.file_listbox != None and self.file_listbox.size() > 0:
            self.file_listbox.delete(0, tk.END)

        list_file = self.controller.client.fetch_local_list()
        list_file = list_file == None and [] or list_file

        for (fname, location) in list_file:
            self.file_listbox.insert(tk.END, fname + "   " + location)

    def publish(self, fname):
        location = filedialog.askopenfilename()
        if (location == None or location == ""):
            self.popup.destroy()
            return

        self.controller.client.publish(fname, location)
        self.popup.destroy()
        self.fetch_local_list()


    def open_popup(self):
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Publish file")

        label = tk.Label(self.popup, text="Enter file name:")
        label.pack(pady=10)

        entry = tk.Entry(self.popup)
        entry.pack(pady=10)

        # Create a button to open a file and populate the text box
        open_button = tk.Button(self.popup, text="Open File", command=lambda: self.publish(entry.get()))
        open_button.pack(pady=10)

        # Create a button to close the popup
        close_button = tk.Button(self.popup, text="Close", command=self.popup.destroy)
        close_button.pack(pady=10)


