import tkinter as tk
from tkinter import scrolledtext
import threading
from autotune import monitor_and_adjust, stop_autotuning

class BitaxeGammaautotuningApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bitaxe Auto-Tuner")
        self.running = False
        self.threads = []
        self.autotuning_status = {}

        # IP Address Entry
        tk.Label(self.root, text="Enter IPs (comma-separated):").grid(row=0, column=0)
        self.ip_entry = tk.Entry(self.root, width=50)
        self.ip_entry.insert(0, "192.168.0.101")
        self.ip_entry.grid(row=0, column=1, columnspan=2)

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

        # autotuning Interval Entry
        tk.Label(self.root, text="Interval (sec):").grid(row=2, column=2)
        self.interval_entry = tk.Entry(self.root, width=10)
        self.interval_entry.insert(0, "5")
        self.interval_entry.grid(row=2, column=3)

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

        # Log Output
        self.log_output = scrolledtext.ScrolledText(self.root, width=100, height=20)
        self.log_output.grid(row=5, column=0, columnspan=4)

    def log_message(self, message, level="info"):
        """Logs messages to the UI."""
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
        ip_addresses = [ip.strip() for ip in ip_addresses if ip.stripl()] #trimming IP's??

        if not ip_addresses:
            self.log_message("Enter at least one IP.","error")
            return
        
        self.log_message(f"Starting autotuning for {len(ip_addresses)} miners...", "success")

        # voltage, frequency = int(self.voltage_entry.get()), int(self.frequency_entry.get())
        # target_temp, interval = int(self.target_temp_entry.get()), int(self.interval_entry.get())
        # power_limit = int(self.power_limit_entry.get())
        interval = int(self.interval_entry.get())

        self.log_message(f"Starting autotuning for: {', '.join(ip_addresses)}", "success")

        for ip in ip_addresses:
            self.autotuning_status[ip] = True
            thread = threading.Thread(target=monitor_and_adjust, args=(ip, interval, self.log_message))
            thread.start()
            self.threads.append(thread)

    def stop_autotuning(self):
        """Stops autotuning miners."""
        self.running = False
        stop_autotuning()
        self.log_message("Stopping autotuning...", "warning")

    def run(self):
        """Runs the Tkinter event loop."""
        self.root.mainloop()
