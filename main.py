import json
import subprocess

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
        print("Setup is not completed. Running accessPoint.py and flaskServer.py...")
        run_script('accessPoint.py')
        run_script('flaskServer.py')

    else:
        # If setup has been completed, run mqtt.py
        print("Setup is already completed. Running mqtt.py...")
        run_script('mqttClient.py')

if __name__ == "__main__":
    main()
