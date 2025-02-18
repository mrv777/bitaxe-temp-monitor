import requests
import time
from config import load_config

# Global Running Flag
running = True

# Get information from the Bitaxe
def get_bitaxe_board_version(bitaxe_ip, log_callback):
    """Fetch the Bitaxe board version from the miner's API"""
    try:
        response = requests.get(f"http://{bitaxe_ip}/api/system/info", timeout=10)
        response.raise_for_status()
        data = response.json()
        log_callback(f"{bitaxe_ip} -> {data.get("boardVersion")}", "success")
        return data.get("boardVersion", "unknown")  # Get board version or return 'unknown'
    except requests.exceptions.RequestException as e:
        return f"Error fetching system info from {bitaxe_ip}: {e}"
    

# Get information from the Bitaxe
def get_system_info(bitaxe_ip):
    """Fetch system info from Bitaxe API."""
    try:
        response = requests.get(f"http://{bitaxe_ip}/api/system/info", timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return f"Error fetching system info from {bitaxe_ip}: {e}"


# Set Bitaxe settings to settings from autotuning (monitor_and_adjust)
def set_system_settings(bitaxe_ip, core_voltage, frequency):
    """Set system parameters via Bitaxe API."""
    settings = {"coreVoltage": core_voltage, "frequency": frequency}
    try:
        response = requests.patch(f"http://{bitaxe_ip}/api/system", json=settings, timeout=10)
        response.raise_for_status()
        return f"{bitaxe_ip} -> Applied settings: Voltage = {core_voltage}mV, Frequency = {frequency}MHz"
    except requests.exceptions.RequestException as e:
        return f"{bitaxe_ip} -> Error setting system settings: {e}"


def monitor_and_adjust(bitaxe_ip, interval, log_callback):
    """Monitor and auto-adjust miner settings for a specific Bitaxe miner."""
    
    #Detect the board version for this specific miner
    board_version = get_bitaxe_board_version(bitaxe_ip, log_callback)
    
    config = load_config(board_version)

    log_callback(f"Detected {bitaxe_ip} as {config.get("bitaxe_model","")} ({board_version})", "info")

    log_callback(f"Starting autotuning for {bitaxe_ip}", "success")

    VOLTAGE_STEP = config["voltage_step"]
    FREQUENCY_STEP = config["frequency_step"]
    MIN_ALLOWED_VOLTAGE = config["min_allowed_voltage"]
    MAX_ALLOWED_VOLTAGE = config["max_allowed_voltage"]
    MIN_ALLOWED_FREQUENCY = config["min_allowed_frequency"]
    MAX_ALLOWED_FREQUENCY = config["max_allowed_frequency"]
    DEFAULT_TARGET_TEMP = config["default_target_temp"]
    DEFAULT_FREQUENCY = config["default_frequency"]
    DEFAULT_VOLTAGE = config["default_voltage"]
    CUSTOM_STARTING_FREQUENCY = config["custom_starting_frequency"]
    CUSTOM_STARTING_VOLTAGE = config["custom_starting_voltage"]
    TEMP_TOLERANCE = config["temp_tolerance"]
    POWER_LIMIT = config["power_limit"]

    log_callback(f"{bitaxe_ip} -> Using {board_version} config: Voltage [{MIN_ALLOWED_VOLTAGE}-{MAX_ALLOWED_VOLTAGE}]mV, Frequency [{MIN_ALLOWED_FREQUENCY}-{MAX_ALLOWED_FREQUENCY}]MHz, Target Temperature [{DEFAULT_TARGET_TEMP}]", "success")

    # start from custom frequency and voltage if it is set in config
    if CUSTOM_STARTING_FREQUENCY is None:
        new_frequency = DEFAULT_FREQUENCY
    else:
        new_frequency = CUSTOM_STARTING_FREQUENCY

    if CUSTOM_STARTING_VOLTAGE is None:
        new_voltage = DEFAULT_VOLTAGE
    else:
        new_voltage = CUSTOM_STARTING_VOLTAGE

    set_system_settings(bitaxe_ip, new_voltage, new_frequency)

    while running:
        info = get_system_info(bitaxe_ip)
        if not running:
            break
        
        if isinstance(info, str):
            log_callback(info, "error")
            time.sleep(interval)
            continue

        temp, hash_rate, power_consumption, current_frequency, current_voltage = (
            info.get("temp", 0), 
            info.get("hashRate", 0), 
            info.get("power", 0),
            info.get("frequency",0),
            info.get("coreVoltage",0))
        
        log_callback(f"{bitaxe_ip} -> Temp: {temp}°C | Hashrate: {int(hash_rate)} GH/s | Power: {round(power_consumption,2)}W | Frequency: {current_frequency} | Voltage: {current_voltage}", "success")

        # Adjust settings based on conditions
        # **STEP-DOWN LOGIC (Protection First)**
        if temp is None or power_consumption > POWER_LIMIT or temp > DEFAULT_TARGET_TEMP:
            log_callback(f"{bitaxe_ip} -> Overheating or Power Limit Exceeded! Lowering settings.", "error")
            
            # Reduce voltage first (to lower power consumption)
            if current_voltage - VOLTAGE_STEP >= MIN_ALLOWED_VOLTAGE:
                new_voltage -= VOLTAGE_STEP
                log_callback(f"{bitaxe_ip} -> Lowering voltage to {new_voltage}mV.", "warning")

            # If voltage cannot go lower, then reduce frequency
            elif current_frequency - FREQUENCY_STEP >= MIN_ALLOWED_FREQUENCY:
                new_frequency -= FREQUENCY_STEP
                log_callback(f"{bitaxe_ip} -> Lowering frequency to {new_frequency}MHz.", "warning")

            # If voltage and frequency are already at minimum, log a warning
            else:
                log_callback(f"{bitaxe_ip} -> Minimum settings reached! Holding state.", "error")

        # **STEP-UP LOGIC (Performance Tuning)**
        elif temp < (DEFAULT_TARGET_TEMP - 3) and power_consumption < (POWER_LIMIT * 0.9):
            log_callback(f"{bitaxe_ip} -> Temp {temp}°C is low. Trying to optimize.", "warning")

            # Ensure voltage is not stuck at low values
            if current_voltage < (MAX_ALLOWED_VOLTAGE * 0.9):  
                new_voltage += VOLTAGE_STEP
                log_callback(f"{bitaxe_ip} -> Increasing voltage to {new_voltage}mV for stability.", "info")

            # Increase frequency only when voltage is already high enough
            elif current_frequency + FREQUENCY_STEP <= MAX_ALLOWED_FREQUENCY:
                new_frequency += FREQUENCY_STEP
                log_callback(f"{bitaxe_ip} -> Increasing frequency to {new_frequency}MHz.", "info")

            # If already at max safe settings, log it
            else:
                log_callback(f"{bitaxe_ip} -> Already at maximum safe settings.", "info")

        # **HASHRATE RECOVERY (Fine-Tuning Stability)**
        elif hash_rate < 1600:
            log_callback(f"{bitaxe_ip} -> Hashrate underperforming! Adjusting voltage.", "warning")
            if current_voltage + VOLTAGE_STEP <= MAX_ALLOWED_VOLTAGE:
                new_voltage += VOLTAGE_STEP  # TRY BOOSTING VOLTAGE TO IMPROVE STABILITY
            else:
                log_callback(f"{bitaxe_ip} -> Voltage maxed, keeping current settings.", "warning")

        else:
            log_callback(f"{bitaxe_ip} -> Stable. No adjustment needed.", "success")
        
        # **Apply settings only if changed**
        if new_voltage != current_voltage or new_frequency != current_frequency:
            applied_settings = set_system_settings(bitaxe_ip, new_voltage, new_frequency)
            current_voltage, current_frequency = new_voltage, new_frequency

        log_callback(set_system_settings(bitaxe_ip, current_voltage, current_frequency), "info")
        time.sleep(interval)

    log_callback(f"{bitaxe_ip} -> autotuning stopped.", "warning")

def stop_autotuning():
    """Stops all autotuning threads."""
    global running
    running = False
