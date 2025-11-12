import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import threading
import sys
from io import StringIO

# Import server logic
from server import Server


class ServerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Sharing - Server GUI")
        self.geometry("1000x700")
        
        # Color scheme
        self.colors = {
            'bg': '#ecf0f1',
            'primary': '#34495e',
            'secondary': '#3498db',
            'accent': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'frame_bg': '#ffffff',
            'text': '#2c3e50',
            'log_bg': '#2c3e50',
            'log_fg': '#ecf0f1',
            'tree_bg': '#fdfefe',
            'tree_select': '#d6eaf8'
        }
        
        self.configure(bg=self.colors['bg'])

        # Initialize server instance
        self.server_instance = None
        self.server_thread = None
        
        # Style
        self.setup_styles()
        self.create_widgets()
        
        # Start server automatically
        self.start_server()
        
        # Start periodic UI update
        self.update_ui()

    def start_server(self):
        """Start server in separate thread"""
        try:
            # Bind to all interfaces (0.0.0.0) instead of empty string
            self.server_instance = Server(server_host="0.0.0.0", server_port=7734)
            
            # Monkey patch the server to disable CLI and redirect print
            self.redirect_server_output()
            
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()
            self.log_message("✅ Server started successfully on 0.0.0.0:7734")
        except Exception as e:
            self.log_message(f"❌ Error starting server: {e}")
    
    def redirect_server_output(self):
        """Redirect server's print statements to GUI"""
        original_print = print
        
        def gui_print(*args, **kwargs):
            message = ' '.join(map(str, args))
            # Remove prompt symbols and clean up message
            message = message.replace('> ', '').strip()
            if message:
                self.after(0, lambda: self.log_message(message))
        
        # Store original in server instance
        self.server_instance._original_print = original_print
        
        # Replace print in server's context
        import builtins
        builtins.print = gui_print
    
    def run_server(self):
        """Run server without CLI"""
        try:
            import socket  # Import socket here
            
            print(f'Starting the server on {self.server_instance.server_host}:{self.server_instance.server_port}')

            self.server_instance.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Allow reuse of address to avoid "Address already in use" error
            self.server_instance.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            self.server_instance.server.bind((self.server_instance.server_host, self.server_instance.server_port))
            self.server_instance.server.listen(5)
            
            # Don't start CLI thread - GUI handles commands
            
            while True:
                try:
                    client, address = self.server_instance.server.accept()
                    print(f'Client {address[0]}:{address[1]} connected.')
                    
                    self.server_instance.client_socket_lists[address] = client

                    # Create thread to handle each client connection
                    client_handler = threading.Thread(
                        target=self.server_instance.handle_client_connection,
                        args=(client, address)
                    )
                    client_handler.start()
                    
                except Exception as e:
                    print(f'Server error: {e}')
                    break
                    
        except Exception as e:
            self.log_message(f"❌ Server error: {e}")

    def update_ui(self):
        """Periodically update UI with server data"""
        if self.server_instance:
            # Update clients tree
            self.update_clients_tree()
            # Update files tree
            self.update_files_tree()
        
        # Schedule next update
        self.after(1000, self.update_ui)

    def update_clients_tree(self):
        """Update connected clients treeview"""
        # Clear existing items
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        if self.server_instance:
            for client_name, client_info in self.server_instance.client_name_lists.items():
                status = "🟢 Online"
                self.clients_tree.insert("", "end", values=(
                    client_name,
                    client_info['host'],
                    client_info['upload_port'],
                    status
                ))

    def update_files_tree(self):
        """Update files treeview"""
        # Clear existing items
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        if self.server_instance:
            for file_name, file_refs in self.server_instance.file_references.items():
                for uploader_addr, file_path in file_refs:
                    client_name = self.server_instance.get_client_name(uploader_addr)
                    self.files_tree.insert("", "end", values=(
                        file_name,
                        client_name or uploader_addr[0],
                        "N/A"  # Size not tracked
                    ))

    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    # ============ CALLBACK PLACEHOLDERS (gắn logic sau) ============
    def on_ping(self):
        hostname = self.server_hostname_entry.get().strip()
        if not hostname:
            self.log_message("⚠️ Please enter a hostname")
            return
        
        if self.server_instance:
            try:
                self.server_instance.ping_client(hostname)
                self.log_message(f"📡 Pinged client: {hostname}")
            except Exception as e:
                self.log_message(f"❌ Error pinging client: {e}")

    def on_discover(self):
        hostname = self.server_hostname_entry.get().strip()
        if not hostname:
            self.log_message("⚠️ Please enter a hostname")
            return
        
        if self.server_instance:
            try:
                self.server_instance.discover_client(hostname)
                self.log_message(f"🔍 Discovered files from: {hostname}")
            except Exception as e:
                self.log_message(f"❌ Error discovering client: {e}")

    def on_list_clients(self):
        if self.server_instance:
            client_count = len(self.server_instance.client_name_lists)
            self.log_message(f"📋 Total clients connected: {client_count}")
            if client_count == 0:
                self.log_message("   (No clients connected)")
            else:
                for client_name, client_info in self.server_instance.client_name_lists.items():
                    self.log_message(f"   • {client_name} - {client_info['host']}:{client_info['port']}")

    def on_exit_server(self):
        if self.server_instance:
            self.log_message("🚪 Shutting down server...")
            self.server_instance.shutdown()
        self.destroy()

    def on_set_client_addresses(self):
        self.log_message("⚙️ set_client_addresses - handled internally by server")

    def on_publish_filename(self):
        self.log_message("⚙️ publish_filename - handled internally by server")

    def on_fetch_peers(self):
        self.log_message("⚙️ fetch_peers - handled internally by server")

    def on_fetch_available_peers(self):
        self.log_message("⚙️ fetch_available_peers - handled internally by server")

    def on_fetch_all_available_files(self):
        if self.server_instance:
            file_count = len(self.server_instance.file_references)
            self.log_message(f"📂 Total files available: {file_count}")

    def on_test_connection(self):
        self.log_message("🔌 test_connection - handled internally by server")

    def on_remove_client(self):
        self.log_message("❌ remove_client - handled internally by server")

    def setup_styles(self):
        """Configure custom styles for widgets"""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        
        # Configure frame styles
        style.configure('Info.TLabelframe', background=self.colors['frame_bg'], 
                       borderwidth=2, relief='solid')
        style.configure('Info.TLabelframe.Label', background=self.colors['frame_bg'],
                       foreground=self.colors['primary'], font=('Helvetica', 11, 'bold'))
        
        style.configure('CLI.TLabelframe', background=self.colors['frame_bg'],
                       borderwidth=2, relief='solid')
        style.configure('CLI.TLabelframe.Label', background=self.colors['frame_bg'],
                       foreground=self.colors['secondary'], font=('Helvetica', 10, 'bold'))
        
        style.configure('Internal.TLabelframe', background=self.colors['frame_bg'],
                       borderwidth=2, relief='solid')
        style.configure('Internal.TLabelframe.Label', background=self.colors['frame_bg'],
                       foreground=self.colors['accent'], font=('Helvetica', 10, 'bold'))
        
        # Configure button styles
        style.configure('Primary.TButton', background=self.colors['primary'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=8, borderwidth=0)
        style.map('Primary.TButton', background=[('active', '#2c3e50')])
        
        style.configure('Secondary.TButton', background=self.colors['secondary'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=8, borderwidth=0)
        style.map('Secondary.TButton', background=[('active', '#2980b9')])
        
        style.configure('Success.TButton', background=self.colors['accent'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=8, borderwidth=0)
        style.map('Success.TButton', background=[('active', '#229954')])
        
        style.configure('Danger.TButton', background=self.colors['danger'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=8, borderwidth=0)
        style.map('Danger.TButton', background=[('active', '#c0392b')])
        
        style.configure('Warning.TButton', background=self.colors['warning'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=6, borderwidth=0)
        style.map('Warning.TButton', background=[('active', '#e67e22')])
        
        # Configure label and entry styles
        style.configure('TLabel', background=self.colors['frame_bg'],
                       foreground=self.colors['text'], font=('Helvetica', 9))
        style.configure('Status.TLabel', background=self.colors['frame_bg'],
                       foreground=self.colors['accent'], font=('Helvetica', 10, 'bold'))
        style.configure('TEntry', fieldbackground='white', font=('Helvetica', 9))
        
        # Configure Treeview styles
        style.configure('Treeview', background=self.colors['tree_bg'],
                       fieldbackground=self.colors['tree_bg'],
                       foreground=self.colors['text'], font=('Helvetica', 9))
        style.configure('Treeview.Heading', background=self.colors['primary'],
                       foreground='white', font=('Helvetica', 9, 'bold'))
        style.map('Treeview', background=[('selected', self.colors['tree_select'])])

    # ================== BUILD SERVER UI ==================
    def create_widgets(self):
        # Khung thông tin server / trạng thái
        info_frame = ttk.LabelFrame(self, text="🖥️ Server Info / Status", 
                                   style='Info.TLabelframe', padding=15)
        info_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.server_status_var = tk.StringVar(value="🟢 Server status: Running")
        status_label = ttk.Label(info_frame, textvariable=self.server_status_var, 
                                style='Status.TLabel')
        status_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Khung CLI commands
        cli_frame = ttk.LabelFrame(self, text="💻 Server CLI Commands", 
                                  style='CLI.TLabelframe', padding=15)
        cli_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Ping / discover
        ttk.Label(cli_frame, text="Hostname (ping/discover):").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.server_hostname_entry = ttk.Entry(cli_frame, width=25)
        self.server_hostname_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ping_button = ttk.Button(cli_frame, text="📡 Ping", command=self.on_ping,
                                style='Secondary.TButton')
        ping_button.grid(row=0, column=2, padx=5, pady=5)

        discover_button = ttk.Button(cli_frame, text="🔍 Discover", command=self.on_discover,
                                    style='Secondary.TButton')
        discover_button.grid(row=0, column=3, padx=5, pady=5)

        # List, Exit
        list_button = ttk.Button(cli_frame, text="📋 List Clients", command=self.on_list_clients,
                                style='Primary.TButton')
        list_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        exit_button = ttk.Button(cli_frame, text="🚪 Exit Server", command=self.on_exit_server,
                                style='Danger.TButton')
        exit_button.grid(row=1, column=3, padx=5, pady=5, sticky="e")

        cli_frame.columnconfigure(1, weight=1)

        # Khung Internal Methods
        internal_frame = ttk.LabelFrame(self, text="⚙️ Server Internal Functions", 
                                       style='Internal.TLabelframe', padding=15)
        internal_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Button(
            internal_frame, text="🔧 Set Client Addresses", command=self.on_set_client_addresses,
            style='Warning.TButton'
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ttk.Button(
            internal_frame, text="📝 Publish Filename", command=self.on_publish_filename,
            style='Warning.TButton'
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(
            internal_frame, text="👥 Fetch Peers", command=self.on_fetch_peers,
            style='Warning.TButton'
        ).grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        ttk.Button(
            internal_frame,
            text="✅ Fetch Available Peers",
            command=self.on_fetch_available_peers,
            style='Warning.TButton'
        ).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(
            internal_frame,
            text="📂 Fetch All Available Files",
            command=self.on_fetch_all_available_files,
            style='Warning.TButton'
        ).grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        ttk.Button(
            internal_frame, text="🔌 Test Connection", command=self.on_test_connection,
            style='Warning.TButton'
        ).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(
            internal_frame, text="❌ Remove Client", command=self.on_remove_client,
            style='Danger.TButton'
        ).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        for col in range(2):
            internal_frame.columnconfigure(col, weight=1)

        # Khung danh sách clients
        clients_frame = ttk.LabelFrame(self, text="👥 Connected Clients", 
                                      style='CLI.TLabelframe', padding=10)
        clients_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.clients_tree = ttk.Treeview(
            clients_frame,
            columns=("hostname", "ip", "port", "status"),
            show="headings",
            height=8,
        )
        self.clients_tree.heading("hostname", text="Hostname")
        self.clients_tree.heading("ip", text="IP")
        self.clients_tree.heading("port", text="Upload Port")
        self.clients_tree.heading("status", text="Status")

        self.clients_tree.column("hostname", width=100)
        self.clients_tree.column("ip", width=100)
        self.clients_tree.column("port", width=90)
        self.clients_tree.column("status", width=80)

        self.clients_tree.pack(fill="both", expand=True)

        # Khung danh sách file
        files_frame = ttk.LabelFrame(self, text="📁 Files on Selected Client / All Files", 
                                    style='Internal.TLabelframe', padding=10)
        files_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        self.files_tree = ttk.Treeview(
            files_frame,
            columns=("fname", "owner", "size"),
            show="headings",
            height=8,
        )
        self.files_tree.heading("fname", text="Filename")
        self.files_tree.heading("owner", text="Owner Host")
        self.files_tree.heading("size", text="Size")

        self.files_tree.column("fname", width=150)
        self.files_tree.column("owner", width=100)
        self.files_tree.column("size", width=80)

        self.files_tree.pack(fill="both", expand=True)

        # Khung log
        log_frame = ttk.LabelFrame(self, text="📊 Server Log", style='Info.TLabelframe', padding=10)
        log_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.log_text = ScrolledText(log_frame, height=8, state="normal",
                                     bg=self.colors['log_bg'], fg=self.colors['log_fg'],
                                     font=('Consolas', 9), insertbackground='white')
        self.log_text.pack(fill="both", expand=True)

        # Cấu hình co giãn
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('server_host', nargs='?', default='', help='Server bind address (leave empty for all interfaces)')
    
    args = parser.parse_args()
    
    app = ServerGUI()
    
    # Update server instance with provided host
    if hasattr(app, 'server_instance') and app.server_instance:
        app.server_instance.server_host = args.server_host
    
    app.mainloop()