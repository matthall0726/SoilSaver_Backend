import json
import os
import signal
import subprocess
import time


def run_script(script_name):
    """Execute a Python script with sudo if necessary."""
    subprocess.run(['sudo', 'python3', script_name], check=True)

def read_device_config(file_path='deviceInformation.json'):
    """Reads the device configuration from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Configuration file not found.")
        return None

def main():
    config = read_device_config()

    if config is None:
        print("Failed to load device configuration. Exiting...")
        return

    if not config.get('setup', False):
        shutdown_signal_path = "shutdown_signal.txt"
        print("Setup is not completed. Running accessPoint.py and flaskServer.py...")
        subprocess.run(['sudo', 'python3', 'accessPoint.py'], check=True)
        process = subprocess.Popen(['python3', 'flaskServer.py'])
        print("Monitoring for shutdown signal...")
        while not os.path.exists(shutdown_signal_path):
            time.sleep(1)  # Check every second

        os.remove(shutdown_signal_path)
        print("Shutdown signal detected. Stopping Flask server...")
        process.send_signal(signal.SIGINT)  # Send SIGINT (Ctrl-C)
        process.wait()  # Wait for the process to terminate

        subprocess.run(['python3', 'mqttClient.py'], check=True)


    else:
        # If setup has been completed, run mqtt.py
        print("Setup is already completed. Running mqtt.py...")
        subprocess.run(['python3', 'mqttClient.py'], check=True)

if __name__ == "__main__":
    main()
