"""
Nova AI Launcher - GUI launcher for backend services
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import sys
import os
import json
from pathlib import Path
from datetime import datetime

class NovaLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Nova AI Launcher")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Store process handles
        self.backend_process = None
        self.discord_process = None
        self.frontend_process = None
        
        # Config file path
        self.config_file = Path.home() / ".nova_launcher_config.json"
        self.backend_dir = self.load_config()
        
        # Set icon if exists
        icon_path = Path(__file__).parent.parent / "frontend" / "favicon.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(icon_path)
            except:
                pass
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        bg_color = "#1e1e2e"
        fg_color = "#cdd6f4"
        accent_color = "#89b4fa"
        button_bg = "#313244"
        
        self.root.configure(bg=bg_color)
        
        # Title
        title_frame = tk.Frame(root, bg=bg_color)
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 Nova AI Launcher",
            font=("Segoe UI", 24, "bold"),
            bg=bg_color,
            fg=accent_color
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Select services to launch",
            font=("Segoe UI", 10),
            bg=bg_color,
            fg=fg_color
        )
        subtitle_label.pack()
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(root)
        notebook.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Style the notebook
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], background=button_bg, foreground=fg_color)
        style.map('TNotebook.Tab', background=[('selected', accent_color)], foreground=[('selected', bg_color)])
        
        # Tab 1: Launcher Controls
        launcher_tab = tk.Frame(notebook, bg=bg_color)
        notebook.add(launcher_tab, text="🚀 Launcher")
        
        # Tab 2: Nova Monitor
        monitor_tab = tk.Frame(notebook, bg=bg_color)
        notebook.add(monitor_tab, text="🤖 Nova Monitor")
        
        # === LAUNCHER TAB CONTENT ===
        
        # Backend directory config section
        config_frame = tk.Frame(launcher_tab, bg=bg_color)
        config_frame.pack(pady=10, padx=20, fill="x")
        
        config_label = tk.Label(
            config_frame,
            text="⚙️ Backend Directory:",
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg=fg_color,
            anchor="w"
        )
        config_label.pack(fill="x")
        
        dir_input_frame = tk.Frame(config_frame, bg=bg_color)
        dir_input_frame.pack(fill="x", pady=5)
        
        self.dir_entry = tk.Entry(
            dir_input_frame,
            font=("Segoe UI", 9),
            bg="#181825",
            fg="#cdd6f4",
            relief="flat",
            bd=5
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.dir_entry.insert(0, str(self.backend_dir))
        
        browse_btn = tk.Button(
            dir_input_frame,
            text="📁 Browse",
            bg="#313244",
            fg="#cdd6f4",
            activebackground="#45475a",
            font=("Segoe UI", 9),
            width=10,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.browse_directory
        )
        browse_btn.pack(side="left")
        
        # Status indicators
        status_frame = tk.Frame(launcher_tab, bg=bg_color)
        status_frame.pack(pady=10, padx=20, fill="x")
        
        # Backend status
        self.backend_status_label = tk.Label(
            status_frame,
            text="● Backend: Stopped",
            font=("Segoe UI", 10),
            bg=bg_color,
            fg="#f38ba8",
            anchor="w"
        )
        self.backend_status_label.pack(fill="x", pady=2)
        
        # Frontend status
        self.frontend_status_label = tk.Label(
            status_frame,
            text="● Frontend: Stopped",
            font=("Segoe UI", 10),
            bg=bg_color,
            fg="#f38ba8",
            anchor="w"
        )
        self.frontend_status_label.pack(fill="x", pady=2)
        
        # Discord bot status
        self.discord_status_label = tk.Label(
            status_frame,
            text="● Discord Bot: Stopped",
            font=("Segoe UI", 10),
            bg=bg_color,
            fg="#f38ba8",
            anchor="w"
        )
        self.discord_status_label.pack(fill="x", pady=2)
        
        # Button frame
        button_frame = tk.Frame(launcher_tab, bg=bg_color)
        button_frame.pack(pady=20, padx=20)
        
        # Style buttons
        button_style = {
            "font": ("Segoe UI", 11, "bold"),
            "width": 20,
            "height": 2,
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }
        
        # Launch Backend button
        self.backend_btn = tk.Button(
            button_frame,
            text="🚀 Launch Backend",
            bg="#a6e3a1",
            fg="#1e1e2e",
            activebackground="#94d38d",
            command=self.launch_backend,
            **button_style
        )
        self.backend_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Launch Discord Bot button
        self.discord_btn = tk.Button(
            button_frame,
            text="💬 Launch Discord Bot",
            bg="#89b4fa",
            fg="#1e1e2e",
            activebackground="#7aa2e8",
            command=self.launch_discord,
            **button_style
        )
        self.discord_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Launch Both button
        self.both_btn = tk.Button(
            button_frame,
            text="⚡ Launch Both",
            bg="#f9e2af",
            fg="#1e1e2e",
            activebackground="#e8d19d",
            command=self.launch_both,
            **button_style
        )
        self.both_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Stop buttons
        stop_frame = tk.Frame(launcher_tab, bg=bg_color)
        stop_frame.pack(pady=10, padx=20)
        
        self.stop_backend_btn = tk.Button(
            stop_frame,
            text="⏹ Stop Backend",
            bg="#f38ba8",
            fg="#1e1e2e",
            activebackground="#e27a97",
            command=self.stop_backend,
            state="disabled",
            font=("Segoe UI", 9),
            width=15,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2"
        )
        self.stop_backend_btn.grid(row=0, column=0, padx=5)
        
        self.stop_discord_btn = tk.Button(
            stop_frame,
            text="⏹ Stop Discord Bot",
            bg="#f38ba8",
            fg="#1e1e2e",
            activebackground="#e27a97",
            command=self.stop_discord,
            state="disabled",
            font=("Segoe UI", 9),
            width=15,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2"
        )
        self.stop_discord_btn.grid(row=0, column=1, padx=5)
        
        self.stop_all_btn = tk.Button(
            stop_frame,
            text="⏹ Stop All",
            bg="#f38ba8",
            fg="#1e1e2e",
            activebackground="#e27a97",
            command=self.stop_all,
            state="disabled",
            font=("Segoe UI", 9, "bold"),
            width=15,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2"
        )
        self.stop_all_btn.grid(row=0, column=2, padx=5)
        
        # Refresh button
        self.refresh_btn = tk.Button(
            stop_frame,
            text="🔄 Refresh Status",
            bg="#94e2d5",
            fg="#1e1e2e",
            activebackground="#83d1c4",
            command=self.force_refresh_status,
            font=("Segoe UI", 9),
            width=15,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2"
        )
        self.refresh_btn.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        
        # Log frame (in launcher tab)
        log_label = tk.Label(
            launcher_tab,
            text="📋 Console Output",
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        log_label.pack(pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            launcher_tab,
            height=8,
            bg="#181825",
            fg="#cdd6f4",
            font=("Consolas", 9),
            wrap=tk.WORD,
            relief="flat",
            bd=0
        )
        self.log_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # === NOVA MONITOR TAB CONTENT ===
        
        # Monitor header
        monitor_header = tk.Label(
            monitor_tab,
            text="📊 Nova Activity Monitor",
            font=("Segoe UI", 14, "bold"),
            bg=bg_color,
            fg=accent_color
        )
        monitor_header.pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(monitor_tab, bg=bg_color)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        # Stats labels
        self.stats_labels = {}
        stats_info = [
            ("conversations", "💬 Active Conversations: 0"),
            ("last_message", "💭 Last Message: N/A"),
            ("uptime", "⏱️ Uptime: 0:00:00"),
            ("memory_usage", "🧠 Learned Facts: 0"),
        ]
        
        for key, text in stats_info:
            label = tk.Label(
                stats_frame,
                text=text,
                font=("Segoe UI", 10),
                bg=bg_color,
                fg=fg_color,
                anchor="w"
            )
            label.pack(fill="x", pady=3)
            self.stats_labels[key] = label
        
        # Activity log
        activity_label = tk.Label(
            monitor_tab,
            text="📝 Recent Activity",
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        activity_label.pack(pady=(10, 5))
        
        self.activity_text = scrolledtext.ScrolledText(
            monitor_tab,
            height=12,
            bg="#181825",
            fg="#cdd6f4",
            font=("Consolas", 9),
            wrap=tk.WORD,
            relief="flat",
            bd=0
        )
        self.activity_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Refresh button
        refresh_btn = tk.Button(
            monitor_tab,
            text="🔄 Refresh Stats",
            bg="#313244",
            fg="#cdd6f4",
            activebackground="#45475a",
            font=("Segoe UI", 10),
            width=20,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.refresh_monitor
        )
        refresh_btn.pack(pady=10)
        
        # Initial log message
        self.log_message("Nova AI Launcher initialized")
        self.log_message(f"Backend directory: {self.backend_dir}")
        
        # Start monitor refresh loop
        self.start_time = datetime.now()
        self.refresh_monitor()
        self.schedule_monitor_refresh()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_config(self):
        """Load backend directory from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    backend_dir = Path(config.get('backend_dir', ''))
                    if backend_dir.exists():
                        return backend_dir
        except:
            pass
        
        # Default: try to find backend directory
        if getattr(sys, 'frozen', False):
            # Running as exe - default to h:\TheAI\backend
            default_dir = Path("h:/TheAI/backend")
        else:
            # Running as script
            default_dir = Path(__file__).parent
        
        return default_dir if default_dir.exists() else Path.home()
    
    def save_config(self):
        """Save backend directory to config file"""
        try:
            config = {'backend_dir': str(self.backend_dir)}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            self.log_message(f"⚠️ Could not save config: {e}")
    
    def browse_directory(self):
        """Browse for backend directory"""
        directory = filedialog.askdirectory(
            title="Select Backend Directory",
            initialdir=self.backend_dir
        )
        if directory:
            self.backend_dir = Path(directory)
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, str(self.backend_dir))
            self.save_config()
            self.log_message(f"✅ Backend directory set to: {self.backend_dir}")
    
    def log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()
    
    def force_refresh_status(self):
        """Force refresh status by checking if processes actually exist"""
        self.log_message("🔄 Refreshing process status...")
        
        # Poll all processes to update their status
        if self.backend_process:
            self.backend_process.poll()
            if self.backend_process.poll() is not None:
                self.backend_process = None
                self.log_message("✓ Backend process cleared (not running)")
        
        if self.frontend_process:
            self.frontend_process.poll()
            if self.frontend_process.poll() is not None:
                self.frontend_process = None
                self.log_message("✓ Frontend process cleared (not running)")
        
        if self.discord_process:
            self.discord_process.poll()
            if self.discord_process.poll() is not None:
                self.discord_process = None
                self.log_message("✓ Discord process cleared (not running)")
        
        self.update_status()
        self.log_message("✅ Status refresh complete")
    
    def update_status(self):
        """Update status labels"""
        if self.backend_process and self.backend_process.poll() is None:
            self.backend_status_label.config(text="● Backend: Running", fg="#a6e3a1")
            self.stop_backend_btn.config(state="normal")
        else:
            self.backend_status_label.config(text="● Backend: Stopped", fg="#f38ba8")
            self.stop_backend_btn.config(state="disabled")
            if self.backend_process and self.backend_process.poll() is not None:
                self.backend_process = None
        
        if self.frontend_process and self.frontend_process.poll() is None:
            self.frontend_status_label.config(text="● Frontend: Running", fg="#a6e3a1")
        else:
            self.frontend_status_label.config(text="● Frontend: Stopped", fg="#f38ba8")
            if self.frontend_process and self.frontend_process.poll() is not None:
                self.frontend_process = None
        
        if self.discord_process and self.discord_process.poll() is None:
            self.discord_status_label.config(text="● Discord Bot: Running", fg="#a6e3a1")
            self.stop_discord_btn.config(state="normal")
        else:
            self.discord_status_label.config(text="● Discord Bot: Stopped", fg="#f38ba8")
            self.stop_discord_btn.config(state="disabled")
            if self.discord_process and self.discord_process.poll() is not None:
                self.discord_process = None
        
        # Update stop all button
        if self.backend_process or self.discord_process or self.frontend_process:
            self.stop_all_btn.config(state="normal")
        else:
            self.stop_all_btn.config(state="disabled")
    
    def launch_backend(self):
        """Launch the FastAPI backend"""
        # Check if already running
        if self.backend_process:
            if self.backend_process.poll() is None:
                self.log_message("⚠️ Backend is already running")
                return
            else:
                # Process ended, clear it
                self.backend_process = None
        
        # Update backend_dir from entry field
        self.backend_dir = Path(self.dir_entry.get())
        self.save_config()
        
        # Verify directory exists
        if not self.backend_dir.exists():
            self.log_message(f"❌ Backend directory not found: {self.backend_dir}")
            messagebox.showerror("Directory Not Found", f"Backend directory does not exist:\n{self.backend_dir}")
            return
        
        if not (self.backend_dir / "main.py").exists():
            self.log_message(f"❌ main.py not found in: {self.backend_dir}")
            messagebox.showerror("File Not Found", f"main.py not found in:\n{self.backend_dir}")
            return
        
        self.log_message("🚀 Launching Backend...")
        self.log_message(f"Using directory: {self.backend_dir}")
        
        def run():
            try:
                # Find Python executable
                import shutil
                python_exe = shutil.which("python")
                if not python_exe:
                    python_exe = shutil.which("python3")
                if not python_exe:
                    python_exe = sys.executable
                
                self.log_message(f"Using Python: {python_exe}")
                
                # Use CREATE_NO_WINDOW on Windows to prevent console popup but avoid window-close errors
                creation_flags = 0
                if sys.platform == "win32":
                    creation_flags = 0x08000000  # CREATE_NO_WINDOW
                
                # Launch uvicorn
                self.backend_process = subprocess.Popen(
                    [python_exe, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
                    cwd=self.backend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=creation_flags
                )
                
                self.log_message("✅ Backend started on http://localhost:8000")
                self.root.after(100, self.update_status)
                
                # Also launch frontend
                self.root.after(1500, self.launch_frontend)
                
                # Read output
                try:
                    for line in self.backend_process.stdout:
                        self.log_message(f"[Backend] {line.strip()}")
                except:
                    pass
                
            except Exception as e:
                self.log_message(f"❌ Error launching backend: {e}")
                self.backend_process = None
                self.root.after(100, self.update_status)
        
        threading.Thread(target=run, daemon=True).start()
        self.root.after(500, self.update_status)
    
    def launch_frontend(self):
        """Launch the Vite frontend"""
        # Check if already running
        if self.frontend_process:
            if self.frontend_process.poll() is None:
                self.log_message("⚠️ Frontend is already running")
                return
            else:
                self.frontend_process = None
        
        # Get frontend directory
        frontend_dir = self.backend_dir.parent / "frontend"
        if not frontend_dir.exists():
            self.log_message(f"⚠️ Frontend directory not found: {frontend_dir}")
            return
        
        if not (frontend_dir / "package.json").exists():
            self.log_message(f"⚠️ package.json not found in: {frontend_dir}")
            return
        
        self.log_message("🌐 Launching Frontend...")
        self.log_message(f"Using directory: {frontend_dir}")
        
        def run():
            try:
                # Find npm executable
                import shutil
                npm_exe = shutil.which("npm")
                if not npm_exe:
                    self.log_message("❌ npm not found in PATH")
                    return
                
                self.log_message(f"Using npm: {npm_exe}")
                
                # Use CREATE_NO_WINDOW on Windows
                creation_flags = 0
                if sys.platform == "win32":
                    creation_flags = 0x08000000  # CREATE_NO_WINDOW
                
                # Launch vite dev server
                self.frontend_process = subprocess.Popen(
                    [npm_exe, "run", "dev"],
                    cwd=frontend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=creation_flags
                )
                
                self.log_message("✅ Frontend started on http://localhost:5173")
                self.root.after(100, self.update_status)
                
                # Read output
                try:
                    for line in self.frontend_process.stdout:
                        self.log_message(f"[Frontend] {line.strip()}")
                except:
                    pass
                
            except Exception as e:
                self.log_message(f"❌ Error launching frontend: {e}")
                self.frontend_process = None
                self.root.after(100, self.update_status)
        
        threading.Thread(target=run, daemon=True).start()
        self.root.after(500, self.update_status)
    
    def launch_discord(self):
        """Launch the Discord bot"""
        # Check if already running
        if self.discord_process:
            if self.discord_process.poll() is None:
                self.log_message("⚠️ Discord bot is already running")
                return
            else:
                # Process ended, clear it
                self.discord_process = None
        
        # Update backend_dir from entry field
        self.backend_dir = Path(self.dir_entry.get())
        self.save_config()
        
        # Verify directory exists
        if not self.backend_dir.exists():
            self.log_message(f"❌ Backend directory not found: {self.backend_dir}")
            messagebox.showerror("Directory Not Found", f"Backend directory does not exist:\n{self.backend_dir}")
            return
        
        if not (self.backend_dir / "discord_bot.py").exists():
            self.log_message(f"❌ discord_bot.py not found in: {self.backend_dir}")
            messagebox.showerror("File Not Found", f"discord_bot.py not found in:\n{self.backend_dir}")
            return
        
        self.log_message("💬 Launching Discord Bot...")
        self.log_message(f"Using directory: {self.backend_dir}")
        
        def run():
            try:
                # Find Python executable
                import shutil
                python_exe = shutil.which("python")
                if not python_exe:
                    python_exe = shutil.which("python3")
                if not python_exe:
                    python_exe = sys.executable
                
                self.log_message(f"Using Python: {python_exe}")
                
                # Use CREATE_NO_WINDOW on Windows to prevent console popup but avoid window-close errors
                creation_flags = 0
                if sys.platform == "win32":
                    creation_flags = 0x08000000  # CREATE_NO_WINDOW
                
                # Launch discord bot
                self.discord_process = subprocess.Popen(
                    [python_exe, "discord_bot.py"],
                    cwd=self.backend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=creation_flags
                )
                
                self.log_message("✅ Discord bot started")
                self.root.after(100, self.update_status)
                
                # Read output
                try:
                    for line in self.discord_process.stdout:
                        self.log_message(f"[Discord] {line.strip()}")
                except:
                    pass
                
            except Exception as e:
                self.log_message(f"❌ Error launching Discord bot: {e}")
                self.discord_process = None
                self.root.after(100, self.update_status)
        
        threading.Thread(target=run, daemon=True).start()
        self.root.after(500, self.update_status)
    
    def launch_both(self):
        """Launch both backend and Discord bot"""
        self.log_message("⚡ Launching all services...")
        self.launch_backend()
        self.root.after(1000, self.launch_discord)  # Delay Discord bot slightly
    
    def stop_backend(self):
        """Stop the backend"""
        if self.backend_process and self.backend_process.poll() is None:
            self.log_message("⏹ Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            self.backend_process = None
            self.log_message("✅ Backend stopped")
            
            # Also stop frontend
            if self.frontend_process:
                self.stop_frontend()
        self.update_status()
    
    def stop_frontend(self):
        """Stop the frontend"""
        if self.frontend_process and self.frontend_process.poll() is None:
            self.log_message("⏹ Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            self.frontend_process = None
            self.log_message("✅ Frontend stopped")
        self.update_status()
    
    def stop_discord(self):
        """Stop the Discord bot"""
        if self.discord_process and self.discord_process.poll() is None:
            self.log_message("⏹ Stopping Discord bot...")
            self.discord_process.terminate()
            try:
                self.discord_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.discord_process.kill()
            self.discord_process = None
            self.log_message("✅ Discord bot stopped")
        self.update_status()
    
    def stop_all(self):
        """Stop all services"""
        self.log_message("⏹ Stopping all services...")
        self.stop_backend()
        self.stop_frontend()
        self.stop_discord()
    
    def on_closing(self):
        """Handle window close event"""
        if self.backend_process or self.discord_process or self.frontend_process:
            response = messagebox.askyesno(
                "Confirm Exit",
                "Services are still running. Stop all services and exit?"
            )
            if response:
                self.stop_all()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def refresh_monitor(self):
        """Refresh Nova monitor stats"""
        try:
            # Update uptime
            if hasattr(self, 'start_time'):
                uptime = datetime.now() - self.start_time
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.stats_labels['uptime'].config(text=f"⏱️ Uptime: {hours}:{minutes:02d}:{seconds:02d}")
            
            # Try multiple possible database locations
            possible_db_paths = [
                self.backend_dir / "chatbot.db",
                self.backend_dir / "nova.db",
                self.backend_dir / "data" / "chatbot.db",
                self.backend_dir / "data" / "nova.db",
                Path("h:/TheAI/backend/chatbot.db"),
                Path("h:/TheAI/backend/nova.db"),
            ]
            
            db_path = None
            for path in possible_db_paths:
                if path.exists():
                    db_path = path
                    break
            
            if db_path and db_path.exists():
                import sqlite3
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    
                    # Check if tables exist
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    # Handle both 'conversations' and 'messages' table names
                    message_table = 'conversations' if 'conversations' in tables else 'messages' if 'messages' in tables else None
                    
                    if message_table:
                        # Get conversation count
                        cursor.execute(f"SELECT COUNT(DISTINCT session_id) FROM {message_table}")
                        conv_count = cursor.fetchone()[0]
                        self.stats_labels['conversations'].config(text=f"💬 Total Conversations: {conv_count}")
                        
                        # Get last message
                        cursor.execute(f"SELECT role, content, timestamp FROM {message_table} ORDER BY timestamp DESC LIMIT 1")
                        last_msg = cursor.fetchone()
                        if last_msg:
                            role, content, timestamp = last_msg
                            preview = content[:50] + "..." if len(content) > 50 else content
                            self.stats_labels['last_message'].config(text=f"💭 Last: [{role}] {preview}")
                        else:
                            self.stats_labels['last_message'].config(text=f"💭 Last Message: No messages yet")
                        
                        # Get recent activity
                        cursor.execute(f"""
                            SELECT role, content, timestamp 
                            FROM {message_table}
                            ORDER BY timestamp DESC 
                            LIMIT 10
                        """)
                        activities = cursor.fetchall()
                        
                        self.activity_text.delete(1.0, tk.END)
                        if activities:
                            for role, content, timestamp in activities:
                                preview = content[:80] + "..." if len(content) > 80 else content
                                self.activity_text.insert(tk.END, f"[{timestamp}] {role}: {preview}\n\n")
                        else:
                            self.activity_text.insert(tk.END, "No activity yet. Start chatting with Nova!\n")
                    else:
                        self.stats_labels['conversations'].config(text="💬 Database empty")
                    
                    # Get learned facts count
                    if 'learned_facts' in tables:
                        cursor.execute("SELECT COUNT(*) FROM learned_facts")
                        facts_count = cursor.fetchone()[0]
                        self.stats_labels['memory_usage'].config(text=f"🧠 Learned Facts: {facts_count}")
                    else:
                        self.stats_labels['memory_usage'].config(text=f"🧠 Learned Facts: 0")
                    
                    conn.close()
                except Exception as e:
                    self.activity_text.delete(1.0, tk.END)
                    self.activity_text.insert(tk.END, f"Error reading database: {e}\n")
                    self.log_message(f"⚠️ Monitor error: {e}")
            else:
                self.stats_labels['conversations'].config(text="💬 Database not found")
                self.stats_labels['last_message'].config(text="💭 Start the backend to create database")
                self.stats_labels['memory_usage'].config(text=f"🧠 Database not initialized")
                self.activity_text.delete(1.0, tk.END)
                self.activity_text.insert(tk.END, "Database not found. Make sure:\n")
                self.activity_text.insert(tk.END, "1. Backend directory is set correctly\n")
                self.activity_text.insert(tk.END, "2. Backend has been launched at least once\n")
                self.activity_text.insert(tk.END, f"3. Looking for: {self.backend_dir}/chatbot.db\n")
                self.activity_text.insert(tk.END, f"\nChecked locations:\n")
                for path in possible_db_paths:
                    self.activity_text.insert(tk.END, f"  - {path} {'✓' if path.exists() else '✗'}\n")
        except Exception as e:
            self.log_message(f"⚠️ Monitor refresh error: {e}")
    
    def schedule_monitor_refresh(self):
        """Schedule periodic monitor refresh"""
        self.refresh_monitor()
        self.root.after(5000, self.schedule_monitor_refresh)  # Refresh every 5 seconds


def main():
    root = tk.Tk()
    app = NovaLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
