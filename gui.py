import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import threading
from autotune import monitor_and_adjust, stop_autotuning

class BitaxeGammaautotuningApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bitaxe Auto-Tuner")
        self.root.geometry("1200x700")  # Default window size
        self.root.state('zoomed')  # Start in maximized mode
        self.root.resizable(True, True)  # Allow resizing both ways

        self.running = False
        self.threads = []
        self.autotuning_status = {}

        # Enable Full-Screen Toggle (Press F11)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Configure grid resizing
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)
        self.root.rowconfigure(5, weight=1)  # Log section grows dynamically

        # === UI Layout === #
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        # === Title Section === #
        tk.Label(top_frame, text="Bitaxe Autotuner", font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        # === Input Section === #
        input_frame = tk.Frame(self.root)
        input_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        # IP Address Entry
        tk.Label(self.root, text="Enter IPs (comma-separated):").grid(row=0, column=0)
        self.ip_entry = tk.Entry(self.root, width=50)
        self.ip_entry.insert(0, "192.168.0.101,192.168.0.107")
        self.ip_entry.grid(row=0, column=1, columnspan=3, sticky="ew")

        # # Voltage Entry
        # tk.Label(self.root, text="Voltage (mV):").grid(row=1, column=0)
        # self.voltage_entry = tk.Entry(self.root, width=10)
        # self.voltage_entry.insert(0, "1150")
        # self.voltage_entry.grid(row=1, column=1)

        # # Frequency Entry
        # tk.Label(self.root, text="Frequency (MHz):").grid(row=1, column=2)
        # self.frequency_entry = tk.Entry(self.root, width=10)
        # self.frequency_entry.insert(0, "525")
        # self.frequency_entry.grid(row=1, column=3)

        # # Target Temperature Entry
        # tk.Label(self.root, text="Target Temp (°C):").grid(row=2, column=0)
        # self.target_temp_entry = tk.Entry(self.root, width=10)
        # self.target_temp_entry.insert(0, "60")
        # self.target_temp_entry.grid(row=2, column=1)

        # Interval Entry
        tk.Label(input_frame, text="Interval (sec):").grid(row=2, column=2, sticky="w")
        self.interval_entry = tk.Entry(input_frame, width=10)
        self.interval_entry.insert(0, "5")
        self.interval_entry.grid(row=2, column=3, sticky="ew")

        # # Power Limit Entry
        # tk.Label(self.root, text="Power Limit (W):").grid(row=3, column=0)
        # self.power_limit_entry = tk.Entry(self.root, width=10)
        # self.power_limit_entry.insert(0, "25")
        # self.power_limit_entry.grid(row=3, column=1)

        # Buttons
        self.start_button = tk.Button(self.root, text="Start autotuning", command=self.start_autotuning)
        self.start_button.grid(row=4, column=0, columnspan=2)

        self.stop_button = tk.Button(self.root, text="Stop autotuning", command=self.stop_autotuning)
        self.stop_button.grid(row=4, column=2, columnspan=2)

        # === Log Output (Expands Dynamically) === #
        self.log_output = scrolledtext.ScrolledText(self.root, width=100, height=20)
        self.log_output.grid(row=5, column=0, columnspan=4, sticky="nsew")

    def toggle_fullscreen(self, event=None):
        """Toggle full-screen mode."""
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def exit_fullscreen(self, event=None):
        """Exit full-screen mode."""
        self.root.attributes("-fullscreen", False)

    def log_message(self, message, level="info"):
        """Logs messages to the UI."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] {message}"
        colors = {"success": "green", "warning": "orange", "error": "red", "info": "black"}
        self.log_output.insert(tk.END, message + "\n", level)
        self.log_output.tag_config(level, foreground=colors[level])
        self.log_output.yview(tk.END)

    def start_autotuning(self):
        """Starts autotuning miners."""
        self.running = True
        self.autotuning_status.clear()
        self.threads.clear()

        ip_addresses = self.ip_entry.get().split(",")
        ip_addresses = [ip.strip() for ip in ip_addresses if ip.strip()] # clean whitespace

        if not ip_addresses:
            self.log_message("Enter at least one IP.","error")
            return
        
        self.log_message(f"Starting autotuning for {len(ip_addresses)} miners...", "success")

        interval = int(self.interval_entry.get())

        for ip in ip_addresses:
            self.autotuning_status[ip] = True
            self.log_message(f"Starting autotuning for: {ip}", "info")
            thread = threading.Thread(target=self.autotune_single_ip,args=(ip, interval))
            # thread = threading.Thread(target=monitor_and_adjust, args=(ip, interval, self.log_message))
            thread.start()
            self.threads.append(thread)

    def autotune_single_ip(self, ip, interval):
        """Runs auto-tuning for a single miner IP"""
        self.log_message(f"Detecting model for {ip}...","info")
        monitor_and_adjust(ip, interval, self.log_message)

    def stop_autotuning(self):
        """Stops autotuning miners."""
        self.running = False
        stop_autotuning()
        self.log_message("Stopping autotuning...", "warning")

    def run(self):
        """Runs the Tkinter event loop."""
        self.root.mainloop()
