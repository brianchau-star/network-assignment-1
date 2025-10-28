import tkinter as tk
from tkinter import filedialog, messagebox

import sys

class RedirectedText:
    def __init__(self, text_widget, stdout):
        self.text_widget = text_widget
        self.stdout = stdout

    def write(self, text, tag=None):
        self.stdout.write(text)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text, tag)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.yview(tk.END)

    def flush(self):
        self.stdout.flush()
        pass  # No need to flush for this example

class DownloadScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.list_container = tk.Frame(self)
        self.list_container.grid_columnconfigure(0,weight=1)
        self.list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=32)

        self.file_listbox = tk.Listbox(self.list_container, selectmode=tk.SINGLE)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.log_space = tk.Text(self.list_container, wrap=tk.WORD, state=tk.DISABLED)
        self.log_space.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=4)

        # Print to log space
        sys.stdout = RedirectedText(self.log_space, sys.stdout)

        label = tk.Label(self, text="Choose a file", font=("Arial", 18))
        label.pack(pady=20,fill=tk.X)

        download_button = tk.Button(self, text="Download", command=self.download_file)
        download_button.pack(pady=10, padx=10)

        back_btn = tk.Button(self, text="Fetch again", command=self.fetch_list)
        back_btn.pack(pady=10, padx=10)

    def start_screen(self):
        self.fetch_list()

    def fetch_list(self):
        if self.file_listbox != None and self.file_listbox.size() > 0:
            self.file_listbox.delete(0, tk.END)

        list_file = self.controller.client.fetch_list()

        if list_file == None or len(list_file) <= 0:
            # self.controller.show_screen("RetryScreen")
            return

        for file_name in list_file:
            self.file_listbox.insert(tk.END, file_name)

    def download_file(self):
        selected_index = self.file_listbox.curselection()

        if not selected_index:
            messagebox.showinfo("Error", "Please select a file to download.")
            return

        selected_file = self.file_listbox.get(selected_index)

        # Choose file location and name to save
        save_location = filedialog.asksaveasfilename(
            title="Save file as",
        )

        if save_location:
            self.controller.client.download_file(selected_file, save_location)
        else:
            print("Operation canceled by the user.")
    
