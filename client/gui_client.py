import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import threading
import socket
import time

# Import client logic
from client import Client


class PeerSelectionDialog(tk.Toplevel):
    """Popup dialog for selecting peer to download from"""
    def __init__(self, parent, file_name, peer_options):
        super().__init__(parent)
        self.title(f"Select Peer - {file_name}")
        self.geometry("600x400")
        self.resizable(False, False)
        
        self.selected_peer = None
        self.peer_options = peer_options
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets(file_name)
        
        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def create_widgets(self, file_name):
        # Header
        header_frame = ttk.Frame(self, padding=15)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(
            header_frame,
            text=f"Select peer to download: {file_name}",
            font=('Helvetica', 12, 'bold')
        ).pack()
        
        # Peer list
        list_frame = ttk.Frame(self, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.peer_tree = ttk.Treeview(
            list_frame,
            columns=("hostname", "ip", "port", "path"),
            show="headings",
            selectmode="browse",
            yscrollcommand=scrollbar.set
        )
        
        self.peer_tree.heading("hostname", text="Hostname")
        self.peer_tree.heading("ip", text="IP Address")
        self.peer_tree.heading("port", text="Port")
        self.peer_tree.heading("path", text="File Path")
        
        self.peer_tree.column("hostname", width=120)
        self.peer_tree.column("ip", width=120)
        self.peer_tree.column("port", width=80)
        self.peer_tree.column("path", width=200)
        
        scrollbar.config(command=self.peer_tree.yview)
        self.peer_tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate peers
        for idx, peer_info in self.peer_options.items():
            # peer_info format: "hostname ip port file_path file_name"
            parts = peer_info.split()
            if len(parts) >= 4:
                hostname, ip, port, path = parts[0], parts[1], parts[2], parts[3]
                self.peer_tree.insert("", "end", iid=str(idx), values=(hostname, ip, port, path))
        
        # Double-click to select
        self.peer_tree.bind("<Double-Button-1>", self.on_peer_double_click)
        
        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Download",
            command=self.on_download_click,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel_click,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        # Info label
        ttk.Label(
            button_frame,
            text="💡 Double-click a peer or select and click Download",
            font=('Helvetica', 9, 'italic')
        ).pack(side=tk.RIGHT, padx=5)
    
    def on_peer_double_click(self, event):
        """Handle double-click on peer"""
        self.on_download_click()
    
    def on_download_click(self):
        """Handle download button click"""
        selection = self.peer_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a peer to download from.")
            return
        
        peer_idx = int(selection[0])
        self.selected_peer = peer_idx
        self.destroy()
    
    def on_cancel_click(self):
        """Handle cancel button click"""
        self.selected_peer = None
        self.destroy()
    
    def get_selection(self):
        """Return selected peer index"""
        return self.selected_peer


class ClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Sharing - Client GUI")
        self.geometry("1000x700")
        
        # Color scheme
        self.colors = {
            'bg': '#f0f4f8',
            'primary': '#2c5f9e',
            'secondary': '#4a90d9',
            'accent': '#5cb85c',
            'danger': '#d9534f',
            'warning': '#f0ad4e',
            'frame_bg': '#ffffff',
            'text': '#2c3e50',
            'log_bg': '#1e272e',
            'log_fg': '#00ff00',
            'tree_bg': '#fafafa',
            'tree_select': '#d4e6f5'
        }
        
        self.configure(bg=self.colors['bg'])
        
        # Initialize client instance
        self.client_instance = None
        self.client_thread = None
        self.client_running = False

        # Style
        self.setup_styles()
        self.create_widgets()
        
        # Populate default values
        self.populate_defaults()
        
        # Start periodic UI update
        self.update_ui()

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
        
        style.configure('Core.TLabelframe', background=self.colors['frame_bg'],
                       borderwidth=2, relief='solid')
        style.configure('Core.TLabelframe.Label', background=self.colors['frame_bg'],
                       foreground=self.colors['accent'], font=('Helvetica', 10, 'bold'))
        
        # Configure button styles
        style.configure('Primary.TButton', background=self.colors['primary'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=8, borderwidth=0)
        style.map('Primary.TButton', background=[('active', '#234a7d')])
        
        style.configure('Secondary.TButton', background=self.colors['secondary'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=8, borderwidth=0)
        style.map('Secondary.TButton', background=[('active', '#3a7abc')])
        
        style.configure('Success.TButton', background=self.colors['accent'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=8, borderwidth=0)
        style.map('Success.TButton', background=[('active', '#4a9a4a')])
        
        style.configure('Danger.TButton', background=self.colors['danger'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=8, borderwidth=0)
        style.map('Danger.TButton', background=[('active', '#c9433f')])
        
        style.configure('Warning.TButton', background=self.colors['warning'],
                       foreground='white', font=('Helvetica', 9, 'bold'),
                       padding=6, borderwidth=0)
        style.map('Warning.TButton', background=[('active', '#d99a3e')])
        
        # Configure label and entry styles
        style.configure('TLabel', background=self.colors['frame_bg'],
                       foreground=self.colors['text'], font=('Helvetica', 9))
        style.configure('TEntry', fieldbackground='white', font=('Helvetica', 9))
        
        # Configure Treeview styles
        style.configure('Treeview', background=self.colors['tree_bg'],
                       fieldbackground=self.colors['tree_bg'],
                       foreground=self.colors['text'], font=('Helvetica', 9))
        style.configure('Treeview.Heading', background=self.colors['primary'],
                       foreground='white', font=('Helvetica', 9, 'bold'))
        style.map('Treeview', background=[('selected', self.colors['tree_select'])])

    def populate_defaults(self):
        """Populate default values in entry fields"""
        # Get local hostname
        try:
            hostname = socket.gethostname()
            self.client_hostname_entry.insert(0, hostname)
        except:
            pass
        
        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            self.client_ip_entry.insert(0, local_ip)
        except:
            pass
        
        # Default server address
        self.server_addr_entry.insert(0, "10.128.17.239:7734")

    def start_client(self):
        """Start client in separate thread"""
        if self.client_running:
            self.log_message("⚠️ Client is already running")
            return
            
        hostname = self.client_hostname_entry.get().strip()
        server_addr = self.server_addr_entry.get().strip()
        
        if not hostname:
            self.log_message("⚠️ Please enter a hostname")
            return
        
        if not server_addr:
            self.log_message("⚠️ Please enter server address")
            return
        
        try:
            # Parse server address
            if ':' in server_addr:
                server_host, server_port = server_addr.split(':')
                server_port = int(server_port)
            else:
                server_host = server_addr
                server_port = 7734
            
            self.client_instance = Client(
                hostname=hostname,
                server_host=server_host,
                server_port=server_port
            )
            
            # Redirect client output
            self.redirect_client_output()
            
            self.client_thread = threading.Thread(target=self.run_client, daemon=True)
            self.client_thread.start()
            
            self.client_running = True
            self.log_message(f"Client '{hostname}' started successfully")
            self.log_message(f"Connecting to server: {server_host}:{server_port}")
            
            # Update upload port when available
            self.after(2000, self.update_upload_port)
            
        except Exception as e:
            self.log_message(f"Error starting client: {e}")
    
    def redirect_client_output(self):
        """Redirect client's print statements to GUI"""
        import builtins
        original_print = builtins.print
        
        def gui_print(*args, **kwargs):
            message = ' '.join(map(str, args))
            # Clean up message
            message = message.replace('> ', '').replace('Select option > ', '').strip()
            # Skip peer selection prompts - we'll handle them with popup
            if message and not message.startswith('\r') and 'Select option' not in message and 'Select peer' not in message:
                self.after(0, lambda msg=message: self.log_message(msg))
        
        builtins.print = gui_print
    
    def run_client(self):
        """Run client without CLI"""
        try:
            print(f'Start connecting to the server on {self.client_instance.server_host}:{self.client_instance.server_port}')
            
            self.client_instance.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            if not self.client_instance.hostname:
                raise Exception('Hostname is empty')
            
            self.client_instance.server.connect((self.client_instance.server_host, self.client_instance.server_port))
            
            # Init upload thread
            self.client_instance.init_upload_thread = threading.Thread(target=self.client_instance.init_upload)
            self.client_instance.init_upload_thread.start()
            
            # Wait for the upload port to be set
            timeout = 5
            while not self.client_instance.upload_port and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
            
            if not self.client_instance.upload_port:
                raise Exception("Failed to initialize upload port")
            
            self.client_instance.set_host_addresses()
            
            print(f'Start listening for peers on port {self.client_instance.upload_port}')
            
            # Don't start CLI thread - GUI handles commands
            
            # Listen for server responses
            while self.client_running:
                try:
                    data = self.client_instance.server.recv(1024).decode()
                    
                    if data:
                        from client_helper import parse_server_response
                        method, payload = parse_server_response(data)
                        
                        if method == 'print':
                            print(data)
                        elif method == 'display_peer_options':
                            # Handle peer selection via GUI popup
                            self.after(0, lambda p=payload: self.show_peer_selection_dialog(p))
                        elif hasattr(self.client_instance, method) and callable(getattr(self.client_instance, method)):
                            getattr(self.client_instance, method)(payload)
                            
                except Exception as e:
                    if self.client_running:
                        print(f"Connection error: {e}")
                    break
                    
        except Exception as e:
            self.log_message(f"Client error: {e}")
            self.client_running = False

    def show_peer_selection_dialog(self, payload):
        """Show popup dialog for peer selection"""
        file_name, options = payload
        
        if len(options) == 0:
            messagebox.showinfo("No Peers", f"No peer has file {file_name}.")
            return
        
        # Build peer options dict - exactly like in client.py display_peer_options
        peer_options = {}
        for i in range(len(options)):
            peer_options[i] = options[i] + ' ' + file_name
        
        # Show dialog
        dialog = PeerSelectionDialog(self, file_name, peer_options)
        self.wait_window(dialog)
        
        # Get selection
        selected_idx = dialog.get_selection()
        
        if selected_idx is not None:
            # Download from selected peer
            # peer_info format: "hostname host port file_path file_name"
            peer_info_str = peer_options[selected_idx]
            peer_info = peer_info_str.split()
            
            if len(peer_info) >= 5:
                hostname = peer_info[0]
                host = peer_info[1]
                port = peer_info[2]
                file_path = peer_info[3]
                fname = peer_info[4]
                
                self.log_message(f"📥 Downloading {fname} from {hostname} ({host}:{port})...")
                
                # Call download method with correct tuple format
                threading.Thread(
                    target=self.client_instance.download_from_peer,
                    args=((hostname, host, port, file_path, fname),),
                    daemon=True
                ).start()
            else:
                self.log_message(f"❌ Invalid peer data format")
        else:
            self.log_message(f"❌ Download cancelled for {file_name}")

    def update_upload_port(self):
        """Update upload port field when available"""
        if self.client_instance and self.client_instance.upload_port:
            self.upload_port_entry.config(state='normal')
            self.upload_port_entry.delete(0, tk.END)
            self.upload_port_entry.insert(0, str(self.client_instance.upload_port))
            self.upload_port_entry.config(state='readonly')

    def update_ui(self):
        """Periodically update UI with client data"""
        # Update peers and files trees if needed
        
        # Schedule next update
        self.after(2000, self.update_ui)

    # ============ CALLBACK IMPLEMENTATIONS ============
    def on_publish_cli(self):
        """Publish the file using the paths in the entry fields"""
        if not self.client_instance:
            self.start_client()
            # Wait a bit for client to initialize
            self.after(2000, self.on_publish_cli)
            return
        
        lname = self.cli_lname_entry.get().strip()
        fname = self.cli_fname_entry.get().strip()
        
        if not lname or not fname:
            self.log_message("⚠️ Please provide both local path and filename")
            return
        
        try:
            # Check if file exists
            if not os.path.exists(lname):
                self.log_message(f"❌ File not found: {lname}")
                return
            
            # Get script directory (client folder)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            destination_path = os.path.join(script_dir, fname)
            
            # Copy file to client directory if source is different
            if os.path.abspath(lname) != os.path.abspath(destination_path):
                import shutil
                shutil.copy2(lname, destination_path)
                self.log_message(f"📋 Copied file to: {destination_path}")
            
            # Publish from current directory
            self.client_instance.publish_file_info((".", fname))
            self.log_message(f"📤 Published: {fname} from current directory")
            
        except Exception as e:
            self.log_message(f"❌ Error publishing file: {e}")
            import traceback
            self.log_message(traceback.format_exc())
    
    def on_browse_local_file(self):
        """Browse button handler for local file selection"""
        file_path = filedialog.askopenfilename(
            title="Select Local File",
            initialdir=os.path.expanduser("~"),
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("PDF Files", "*.pdf"),
                ("Image Files", "*.png *.jpg *.jpeg *.gif"),
                ("Documents", "*.doc *.docx")
            ]
        )
        
        if file_path:
            self.cli_lname_entry.delete(0, tk.END)
            self.cli_lname_entry.insert(0, file_path)
            
            # Auto-fill remote name with just the filename
            filename = os.path.basename(file_path)
            self.cli_fname_entry.delete(0, tk.END)
            self.cli_fname_entry.insert(0, filename)
            
            self.log_message(f"Selected file: {file_path}")

    def on_fetch_cli(self):
        if not self.client_instance:
            self.log_message("⚠️ Client not started. Please start client first.")
            return
        
        fname = self.cli_fetch_fname_entry.get().strip()
        if not fname:
            self.log_message("⚠️ Please provide filename to fetch")
            return
        
        try:
            self.client_instance.fetch_file_info(fname)
            self.log_message(f"📥 Fetching file: {fname}")
        except Exception as e:
            self.log_message(f"❌ Error fetching file: {e}")

    def on_list_peers_cli(self):
        if not self.client_instance:
            self.log_message("⚠️ Client not started.")
            return
        
        try:
            self.client_instance.list_peers()
            self.log_message("👥 Listing peers...")
        except Exception as e:
            self.log_message(f"❌ Error listing peers: {e}")

    def on_list_files_cli(self):
        if not self.client_instance:
            self.log_message("⚠️ Client not started.")
            return
        
        try:
            self.client_instance.list_files()
            self.log_message("📂 Listing files...")
        except Exception as e:
            self.log_message(f"❌ Error listing files: {e}")

    def on_exit_client(self):
        self.log_message("🚪 Exiting client...")
        self.client_running = False
        if self.client_instance:
            try:
                self.client_instance.server.close()
            except:
                pass
        self.after(500, self.destroy)

    def on_publish_file_info(self):
        self.log_message("📝 Use CLI Publish button above")

    def on_download_from_peer(self):
        self.log_message("⬇️ Use Fetch command to download files")

    def on_list_peers_core(self):
        self.on_list_peers_cli()

    def on_list_files_core(self):
        self.on_list_files_cli()
    
    def log_message(self, message):
        """Helper method to log messages"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    # ================== BUILD CLIENT UI ==================
    def create_widgets(self):
        # Thông tin client
        info_frame = ttk.LabelFrame(self, text="Client Info", style='Info.TLabelframe', padding=15)
        info_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        ttk.Label(info_frame, text="Hostname:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.client_hostname_entry = ttk.Entry(info_frame, width=20)
        self.client_hostname_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(info_frame, text="Local IP:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.client_ip_entry = ttk.Entry(info_frame, width=20)
        self.client_ip_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(info_frame, text="Server Address:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.server_addr_entry = ttk.Entry(info_frame, width=20)
        self.server_addr_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(info_frame, text="Upload Port:").grid(
            row=1, column=2, padx=5, pady=5, sticky="e"
        )
        self.upload_port_entry = ttk.Entry(info_frame, width=20, state='readonly')
        self.upload_port_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Add Start Client button
        start_button = ttk.Button(info_frame, text="Start Client", 
                                 command=self.start_client, style='Success.TButton')
        start_button.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        # CLI commands cho client
        cli_frame = ttk.LabelFrame(self, text="Client CLI Commands", style='CLI.TLabelframe', padding=15)
        cli_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # publish lname fname
        ttk.Label(cli_frame, text="Local path (lname):").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        
        # Frame for entry and browse button
        lname_frame = ttk.Frame(cli_frame, style='CLI.TLabelframe')
        lname_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.cli_lname_entry = ttk.Entry(lname_frame, width=25)
        self.cli_lname_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(lname_frame, text="Browse", 
                                   command=self.on_browse_local_file,
                                   style='Primary.TButton', width=10)
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Label(cli_frame, text="Remote name (fname):").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.cli_fname_entry = ttk.Entry(cli_frame, width=25)
        self.cli_fname_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        publish_button = ttk.Button(cli_frame, text="Publish File", 
                                    command=self.on_publish_cli, style='Success.TButton')
        publish_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # fetch fname
        ttk.Label(cli_frame, text="File to fetch (fname):").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        self.cli_fetch_fname_entry = ttk.Entry(cli_frame, width=25)
        self.cli_fetch_fname_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        fetch_button = ttk.Button(cli_frame, text="Fetch File", 
                                 command=self.on_fetch_cli, style='Success.TButton')
        fetch_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # list peers, list files, exit
        list_peers_button = ttk.Button(
            cli_frame, text="List Peers", command=self.on_list_peers_cli, 
            style='Primary.TButton'
        )
        list_peers_button.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        list_files_button = ttk.Button(
            cli_frame, text="List Files", command=self.on_list_files_cli,
            style='Primary.TButton'
        )
        list_files_button.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        exit_button = ttk.Button(cli_frame, text="Exit", command=self.on_exit_client,
                                style='Danger.TButton')
        exit_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        cli_frame.columnconfigure(1, weight=1)


        # Log client
        log_frame = ttk.LabelFrame(self, text="Client Log", style='Core.TLabelframe', padding=10)
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
    parser.add_argument('--hostname', dest='hostname', type=str, help='Client hostname')
    parser.add_argument('server_host', nargs='?', default=None, help='Server IP address')
    
    args = parser.parse_args()
    
    app = ClientGUI()
    
    # Pre-fill hostname if provided
    if args.hostname:
        app.client_hostname_entry.delete(0, tk.END)
        app.client_hostname_entry.insert(0, args.hostname)
    
    # Pre-fill server address if provided
    if args.server_host:
        app.server_addr_entry.delete(0, tk.END)
        app.server_addr_entry.insert(0, f"{args.server_host}:7734")
    
    app.mainloop()