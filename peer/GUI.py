import tkinter as tk
from screens.MainScreen import MainScreen

class GUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
    
    def start(self):
        self.root.title("Peer")

        self.container = tk.Frame(self.root)
        self.container.grid_columnconfigure(0,weight=1)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Screens
        self.screens = {}
        for F in (MainScreen,):
            page_name = F.__name__
            screen = F(self.container, self)
            screen.grid(row=0, column=0, sticky=tk.NSEW)
            self.screens[page_name] = screen

        # Show screen
        self.show_screen("MainScreen")

        self.root.geometry("816x600")
        self.root.mainloop()

    def show_screen(self, screen_name):
        screen = self.screens[screen_name]
        screen.tkraise()
        func = getattr(screen, 'start_screen', None)
        if callable(func):
            func()

    def close(self):
        self.client.stop()
        self.root.destroy()
