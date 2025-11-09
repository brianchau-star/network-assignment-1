import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import sys

from client import Client
from client_helper import parse_client_cmd, parse_server_response, MyException

class P2PClientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P2P File Sharing Client")
        self.root.geometry("900x700")
        
        # Client instance - using ORIGINAL Client class
        self.client = None
        self.client_thread = None
        self.connected = False
        
        # Output queue for thread communication
        self.output_queue = queue.Queue()
        
        # Peer selection state
        self.peer_options = {}
        
        self.setup_ui()
        self.process_output_queue()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Connection inputs
        input_frame = ttk.Frame(conn_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Hostname:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.hostname_var = tk.StringVar()
        hostname_entry = ttk.Entry(input_frame, textvariable=self.hostname_var, width=15)
        hostname_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(input_frame, text="Server IP:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.server_ip_var = tk.StringVar(value="10.128.17.239")
        ip_entry = ttk.Entry(input_frame, textvariable=self.server_ip_var, width=15)
        ip_entry.grid(row=0, column=3, padx=(0, 15))
        
        ttk.Label(input_frame, text="Port:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.server_port_var = tk.StringVar(value="7734")
        port_entry = ttk.Entry(input_frame, textvariable=self.server_port_var, width=8)
        port_entry.grid(row=0, column=5, padx=(0, 15))
        
        self.connect_btn = ttk.Button(input_frame, text="Connect", command=self.connect)
        self.connect_btn.grid(row=0, column=6, padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(input_frame, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_btn.grid(row=0, column=7)
        
        # Status
        self.status_var = tk.StringVar(value="Not connected")
        self.status_label = ttk.Label(conn_frame, textvariable=self.status_var, foreground="red")
        self.status_label.pack(pady=(10, 0))
        
        # File operations frame
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Publish file
        publish_frame = ttk.Frame(file_frame)
        publish_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(publish_frame, text="Publish File:").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(publish_frame, textvariable=self.file_path_var, width=60)
        file_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        
        ttk.Button(publish_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(publish_frame, text="Publish", command=self.publish_file).pack(side=tk.LEFT)
        
        # Fetch file
        fetch_frame = ttk.Frame(file_frame)
        fetch_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(fetch_frame, text="Fetch File:").pack(side=tk.LEFT)
        self.fetch_file_var = tk.StringVar()
        fetch_entry = ttk.Entry(fetch_frame, textvariable=self.fetch_file_var, width=30)
        fetch_entry.pack(side=tk.LEFT, padx=(10, 10))
        
        ttk.Button(fetch_frame, text="Fetch", command=self.fetch_file).pack(side=tk.LEFT)
        
        # Action buttons
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="List Peers", command=self.list_peers).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="List Files", command=self.list_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT)
        
        # Peer selection frame (hidden by default)
        self.peer_frame = ttk.LabelFrame(main_frame, text="Select Peer", padding="10")
        
        self.peer_listbox = tk.Listbox(self.peer_frame, height=6)
        self.peer_listbox.pack(fill=tk.X, pady=(0, 10))
        
        peer_btn_frame = ttk.Frame(self.peer_frame)
        peer_btn_frame.pack()
        
        ttk.Button(peer_btn_frame, text="Download", command=self.download_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(peer_btn_frame, text="Cancel", command=self.hide_peer_selection).pack(side=tk.LEFT)
        
        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=20, width=100)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
    def connect(self):
        """Connect to server using ORIGINAL Client class"""
        hostname = self.hostname_var.get().strip()
        server_ip = self.server_ip_var.get().strip()
        
        if not hostname:
            messagebox.showerror("Error", "Please enter hostname")
            return
        if not server_ip:
            messagebox.showerror("Error", "Please enter server IP")
            return
        
        try:
            server_port = int(self.server_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid port")
            return
        
        try:
            # Create ORIGINAL Client instance
            self.client = Client(
                hostname=hostname,
                server_host=server_ip,
                server_port=server_port
            )
            
            # Patch client methods for GUI interaction
            self.patch_client_for_gui()
            
            # Start client in thread
            self.client_thread = threading.Thread(target=self.run_client, daemon=True)
            self.client_thread.start()
            
            # Update UI
            self.connected = True
            self.status_var.set("Connected")
            self.status_label.config(foreground="green")
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            
            self.append_output(f"Connecting as {hostname} to {server_ip}:{server_port}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")
    
    def patch_client_for_gui(self):
        """Patch client methods to work with GUI"""
        
        # Store original methods
        original_display_peer_options = self.client.display_peer_options
        
        def gui_display_peer_options(payload):
            """Override display_peer_options for GUI"""
            file_name, options = payload
            
            # Update client state as in original
            self.client.peer_options = {}
            
            if len(options) == 0:
                self.append_output(f'No peer has file {file_name}.')
                return
            
            # Set up peer options as in original
            for i in range(len(options)):
                self.client.peer_options[i] = options[i] + ' ' + file_name
            
            self.client.is_selecting_peer = True
            
            # Show in GUI
            self.show_peer_selection(file_name, options)
        
        # Override method
        self.client.display_peer_options = gui_display_peer_options
    
    def run_client(self):
        """Run ORIGINAL client.start() method"""
        try:
            self.client.start()
        except Exception as e:
            self.append_output(f"Client error: {e}")
    
    def disconnect(self):
        """Disconnect from server"""
        if self.client:
            try:
                self.client.shutdown()
            except:
                pass
        
        self.connected = False
        self.status_var.set("Disconnected")
        self.status_label.config(foreground="red")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.hide_peer_selection()
        
        self.append_output("Disconnected from server")
    
    def browse_file(self):
        """Browse for file to publish"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_var.set(file_path)
    
    def publish_file(self):
        """Publish file using ORIGINAL method"""
        if not self.connected or not self.client:
            messagebox.showerror("Error", "Not connected")
            return
        
        file_path = self.file_path_var.get().strip()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
        
        try:
            # Parse like original logic
            directory = os.path.dirname(file_path) or "."
            filename = os.path.basename(file_path)
            
            # Call ORIGINAL method
            self.client.publish_file_info((directory, filename))
            self.append_output(f"Published: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Publish failed: {e}")
    
    def fetch_file(self):
        """Fetch file using ORIGINAL method"""
        if not self.connected or not self.client:
            messagebox.showerror("Error", "Not connected")
            return
        
        file_name = self.fetch_file_var.get().strip()
        if not file_name:
            messagebox.showerror("Error", "Enter file name")
            return
        
        try:
            # Call ORIGINAL method
            self.client.fetch_file_info(file_name)
            self.append_output(f"Searching for: {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Fetch failed: {e}")
    
    def list_peers(self):
        """List peers using ORIGINAL method"""
        if not self.connected or not self.client:
            messagebox.showerror("Error", "Not connected")
            return
        try:
            self.client.list_peers()
        except Exception as e:
            messagebox.showerror("Error", f"List peers failed: {e}")
    
    def list_files(self):
        """List files using ORIGINAL method"""
        if not self.connected or not self.client:
            messagebox.showerror("Error", "Not connected")
            return
        try:
            self.client.list_files()
        except Exception as e:
            messagebox.showerror("Error", f"List files failed: {e}")
    
    def show_peer_selection(self, file_name, options):
        """Show peer selection GUI"""
        self.peer_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.peer_listbox.delete(0, tk.END)
        self.peer_options = {}
        
        self.append_output(f"Select peer to download {file_name}:")
        
        for i, option in enumerate(options):
            self.peer_options[i] = option + ' ' + file_name
            hostname, host, port, file_path = option.split()
            display = f"{i}: {hostname} ({host}:{port}) - {file_path}"
            self.peer_listbox.insert(tk.END, display)
            self.append_output(display)
    
    def hide_peer_selection(self):
        """Hide peer selection"""
        self.peer_frame.pack_forget()
        self.peer_options = {}
        if self.client:
            self.client.is_selecting_peer = False
    
    def download_selected(self):
        """Download from selected peer using ORIGINAL method"""
        selection = self.peer_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a peer")
            return
        
        index = selection[0]
        if index in self.peer_options:
            try:
                payload = tuple(self.peer_options[index].split())
                
                # Call ORIGINAL method
                self.client.download_from_peer(payload)
                self.append_output("Starting download...")
                self.hide_peer_selection()
                
                # Reset client state as in original
                self.client.is_selecting_peer = False
                self.client.peer_options = {}
                
            except Exception as e:
                messagebox.showerror("Error", f"Download failed: {e}")
    
    def process_output_queue(self):
        """Process output from other threads"""
        try:
            while True:
                text = self.output_queue.get_nowait()
                self.append_output_direct(text)
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_output_queue)
    
    def append_output(self, text):
        """Thread-safe output append"""
        self.output_queue.put(text)
    
    def append_output_direct(self, text):
        """Direct append to output"""
        import time
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.output_text.insert(tk.END, f"[{timestamp}] {text}\n")
        self.output_text.see(tk.END)
    
    def clear_output(self):
        """Clear output"""
        self.output_text.delete(1.0, tk.END)
    
    def run(self):
        """Run GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window close"""
        if self.connected:
            self.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    app = P2PClientGUI()
    app.run()