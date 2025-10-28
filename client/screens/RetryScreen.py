import tkinter as tk
from tkinter import filedialog, messagebox

class RetryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Button(self, text="Retry", command=self.try_again).pack(pady=10, padx=10)

    def try_again(self):
        self.controller.show_screen("DownloadScreen")

