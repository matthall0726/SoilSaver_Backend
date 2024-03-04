import subprocess

def is_wpa_supplicant_blank(file_path):
    """Check if the wpa_supplicant.conf file is blank or does not exist."""
    try:
        # Use 'sudo cat' to read the file with elevated privileges
        result = subprocess.run(['sudo', 'cat', file_path], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Check if command executed successfully
        if result.returncode == 0:
            contents = result.stdout.strip()
            return not contents  # Returns True if blank, False otherwise
        else:
            print(f"Error accessing file: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error checking file: {e}")
        return False

def run_script(script_name):
    """Execute a Python script with sudo if necessary."""
    subprocess.run(['sudo', 'python', script_name], check=True)

# Path to the wpa_supplicant.conf you want to check
wpa_supplicant_path = '/etc/wpa_supplicant/wpa_supplicant.conf'

# Determine the workflow based on the file's condition
if is_wpa_supplicant_blank(wpa_supplicant_path):
    # If the wpa_supplicant.conf file is blank or missing, run accessPoint.py, then flaskServer.py
    print("wpa_supplicant.conf is blank or missing. Running accessPoint.py and flaskServer.py...")
    run_script('accessPoint.py')
    run_script('flaskServer.py')
else:
    # If the wpa_supplicant.conf file is not blank, run mqtt.py
    print("wpa_supplicant.conf has content. Running mqtt.py...")
    run_script('mqtt.py')

# Finally, run mqttClient.py which should run regardless
print("Running mqttClient.py...")
run_script('mqttClient.py')
