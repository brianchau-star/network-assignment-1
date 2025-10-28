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
        sys.stdout = RedirectedText(self.log_space, sys.stdout)

        # Add peer
        tk.Label(self, text="Choose a peer", font=("Arial", 18)).pack(pady=8,fill=tk.X)

        add_peer_container = tk.Frame(self)
        add_peer_container.configure(width=50)
        add_peer_container.pack(expand=True, padx=10, pady=10)
        
        self.peer_entry = tk.Entry(add_peer_container)
        self.peer_entry.configure(width=20)
        self.peer_entry.grid(row=0,column=0,pady=8)

        tk.Button(add_peer_container, text="Add Peer", command=self.add_host).grid(row=0,column=1,pady=10, padx=10)

        # Peer actions
        label = tk.Label(self, text="Choose a peer", font=("Arial", 18))
        label.pack(pady=8,fill=tk.X)

        button_container = tk.Frame(self)
        button_container.configure(width=50)
        button_container.pack(pady=20)

        tk.Button(button_container, text="Ping", command=self.ping).grid(row=0, column=0,pady=10, padx=10)
        tk.Button(button_container, text="Discover", command=self.discover).grid(row=0,column=1,pady=10, padx=10)
        tk.Button(button_container, text="Delete", command=self.delete_host).grid(row=0,column=2,pady=10, padx=10)
        tk.Button(button_container, text="Refresh", command=self.fetch_peers).grid(row=0,column=3,pady=10, padx=10)

    def add_host(self):
        ip = self.peer_entry.get()
        if ip == "":
            messagebox.showerror("Error", "Hostname cannot be empty")
            return

        self.controller.client.add_host(ip)
        self.peer_entry.delete(0, tk.END)
        self.fetch_peers() 
    
    def delete_host(self):
        selected_index = self.file_listbox.curselection()

        if not selected_index:
            return

        text = self.file_listbox.get(selected_index) 
        ip = text.split("-")[0].strip()
        self.controller.client.delete_host(ip)
        self.peer_entry.delete(0, tk.END)
        self.fetch_peers() 

    def start_screen(self):
        self.fetch_peers()

    def fetch_peers(self):
        if self.file_listbox != None and self.file_listbox.size() > 0:
            self.file_listbox.delete(0, tk.END)

        list_file = self.controller.client.fetch_peers()
        list_file = list_file == None and [] or list_file

        for (ip, online) in list_file:
            self.file_listbox.insert(tk.END, ip + " - " + ("Online" if online else "Offline"))

    def ping(self):
        selected_index = self.file_listbox.curselection()

        if not selected_index:
            return

        text = self.file_listbox.get(selected_index) 

        hostname = text.split("-")[0].strip()

        ping_count = self.controller.client.ping(hostname)

        # Show popup
        self.popup = tk.Toplevel(self.parent,padx=10,pady=10)
        self.popup.geometry("400x300")
        self.popup.title("Ping result of " + hostname)

        if ping_count == None:
            tk.Label(self.popup, text="Ping failed").pack(pady=10)
        else:
            tk.Label(self.popup, text="Ping count: " + str(ping_count)).pack(pady=10)

        close_button = tk.Button(self.popup, text="Close", command=self.popup.destroy)
        close_button.pack(pady=10)

    def discover(self):
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            return

        text = self.file_listbox.get(selected_index) 

        hostname = text.split("-")[0].strip()   

        list_file = self.controller.client.discover(hostname)

        # Show popup
        self.popup = tk.Toplevel(self.parent,padx=10,pady=10)
        self.popup.geometry("400x300")
        self.popup.title("Files of " + hostname)

        if list_file == None or len(list_file) == 0:
            tk.Label(self.popup, text="No files found").pack(pady=10)
        else:
            disc_file_listbox = tk.Listbox(self.popup, selectmode=tk.SINGLE)
            disc_file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10,pady=10)

            for file in list_file:
                disc_file_listbox.insert(tk.END, file)

        close_button = tk.Button(self.popup, text="Close", command=self.popup.destroy)
        close_button.pack(pady=10)
