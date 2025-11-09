import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import sys
import os
import queue
from io import StringIO

from server import Server
from server_helper import parse_server_cmd, MyException

class P2PServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P2P File Sharing Server")
        self.root.geometry("900x700")
        
        # Server instance
        self.server = None
        self.server_running = False
        self.server_thread = None
        
        # Queue for thread communication
        self.output_queue = queue.Queue()
        
        self.setup_ui()
        self.process_output_queue()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Server control frame
        control_frame = ttk.LabelFrame(main_frame, text="Server Control", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # IP and Port inputs
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Server IP:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.server_ip_var = tk.StringVar(value="10.128.17.239")
        ip_entry = ttk.Entry(input_frame, textvariable=self.server_ip_var, width=20)
        ip_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(input_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.server_port_var = tk.StringVar(value="7734")
        port_entry = ttk.Entry(input_frame, textvariable=self.server_port_var, width=10)
        port_entry.grid(row=0, column=3, padx=(0, 20))
        
        # Control buttons
        self.start_btn = ttk.Button(input_frame, text="Start Server", command=self.start_server)
        self.start_btn.grid(row=0, column=4, padx=(0, 10))
        
        self.stop_btn = ttk.Button(input_frame, text="Stop Server", command=self.stop_server, state="disabled")
        self.stop_btn.grid(row=0, column=5)
        
        # Status
        self.status_var = tk.StringVar(value="Server stopped")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var, foreground="red")
        self.status_label.pack(pady=(10, 0))
        
        # Commands frame
        cmd_frame = ttk.LabelFrame(main_frame, text="Server Commands", padding="10")
        cmd_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Command input
        cmd_input_frame = ttk.Frame(cmd_frame)
        cmd_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cmd_input_frame, text="Command:").pack(side=tk.LEFT)
        self.command_var = tk.StringVar()
        self.command_entry = ttk.Entry(cmd_input_frame, textvariable=self.command_var, width=50)
        self.command_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.command_entry.bind('<Return>', lambda e: self.execute_command())
        
        ttk.Button(cmd_input_frame, text="Execute", command=self.execute_command).pack(side=tk.LEFT)
        
        # Quick buttons
        quick_frame = ttk.Frame(cmd_frame)
        quick_frame.pack(fill=tk.X)
        
        ttk.Button(quick_frame, text="List Clients", command=lambda: self.quick_command("list")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_frame, text="Ping Client", command=self.ping_client_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_frame, text="Discover Client", command=self.discover_client_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT)
        
        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="Server Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Output text
        self.output_text = scrolledtext.ScrolledText(output_frame, height=25, width=100)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
    def start_server(self):
        """Start server using original Server class"""
        if self.server_running:
            return
            
        try:
            server_ip = self.server_ip_var.get().strip()
            server_port = int(self.server_port_var.get().strip())
            
            # Create server instance using ORIGINAL code
            self.server = Server(server_host=server_ip, server_port=server_port)
            
            # Redirect print to capture server output
            self.redirect_output()
            
            # Start server in thread
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()
            
            # Update UI
            self.server_running = True
            self.status_var.set(f"Server running on {server_ip}:{server_port}")
            self.status_label.config(foreground="green")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            self.append_output(f"GUI: Starting server on {server_ip}:{server_port}")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def redirect_output(self):
        """Redirect print output to GUI"""
        original_stdout = sys.stdout
        
        class OutputCapture:
            def __init__(self, gui):
                self.gui = gui
                self.original_stdout = original_stdout
                
            def write(self, text):
                if text.strip():  # Only add non-empty text
                    self.gui.output_queue.put(text.rstrip())
                # Also write to original stdout for debugging
                self.original_stdout.write(text)
                
            def flush(self):
                self.original_stdout.flush()
        
        sys.stdout = OutputCapture(self)
    
    def run_server(self):
        """Run the original server.start() method"""
        try:
            self.server.start()
        except Exception as e:
            self.output_queue.put(f"Server error: {e}")
    
    def stop_server(self):
        """Stop server"""
        if not self.server_running:
            return
            
        try:
            if self.server:
                self.server.shutdown()
        except:
            pass
        
        # Update UI
        self.server_running = False
        self.status_var.set("Server stopped")
        self.status_label.config(foreground="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        self.append_output("GUI: Server stopped")
    
    def execute_command(self):
        """Execute server command using ORIGINAL logic"""
        if not self.server_running or not self.server:
            messagebox.showerror("Error", "Server is not running")
            return
            
        command = self.command_var.get().strip()
        if not command:
            return
        
        try:
            # Use ORIGINAL parse_server_cmd
            method, payload = parse_server_cmd(command)
            
            # Call ORIGINAL server method
            if hasattr(self.server, method) and callable(getattr(self.server, method)):
                # Execute in separate thread to not block GUI
                def execute_method():
                    try:
                        self.append_output(f"GUI> {command}")
                        getattr(self.server, method)(payload)
                    except Exception as e:
                        self.output_queue.put(f"Command error: {e}")
                
                thread = threading.Thread(target=execute_method, daemon=True)
                thread.start()
            
            self.command_var.set("")  # Clear command
            
        except MyException as e:
            messagebox.showerror("Error", f"Invalid command: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Command failed: {e}")
    
    def quick_command(self, cmd):
        """Execute quick command"""
        self.command_var.set(cmd)
        self.execute_command()
    
    def ping_client_dialog(self):
        """Dialog to ping client"""
        if not self.server_running:
            messagebox.showerror("Error", "Server is not running")
            return
            
        client_name = simpledialog.askstring("Ping Client", "Enter client name:")
        if client_name:
            self.command_var.set(f"ping {client_name}")
            self.execute_command()
    
    def discover_client_dialog(self):
        """Dialog to discover client files"""
        if not self.server_running:
            messagebox.showerror("Error", "Server is not running")
            return
            
        client_name = simpledialog.askstring("Discover Client", "Enter client name:")
        if client_name:
            self.command_var.set(f"discover {client_name}")
            self.execute_command()
    
    def process_output_queue(self):
        """Process output from server thread"""
        try:
            while True:
                text = self.output_queue.get_nowait()
                self.append_output_direct(text)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_output_queue)
    
    def append_output(self, text):
        """Add text to output (thread-safe)"""
        self.output_queue.put(text)
    
    def append_output_direct(self, text):
        """Directly append to output text widget"""
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
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_server()
    
    def on_closing(self):
        """Handle window closing"""
        if self.server_running:
            self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    app = P2PServerGUI()
    app.run()