import time
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

def is_connected():
    try:
        response = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return response.returncode == 0
        print("Ping was successful")
    except Exception as e:
        print(f"An error occurred while checking internet connection: {e}")
        return False

# Example usage
if is_connected():
    print("Device is connected to the internet.")
else:
    print("Device is not connected to the internet.")

def setWifi(SSID, PASSWORD):
    commands = [
        ['sudo', 'systemctl', 'enable', 'NetworkManager'],
        ['sudo', 'systemctl', 'start', 'NetworkManager'],
        ['sudo', 'nmcli', 'radio', 'wifi', 'on'],
        ['sudo', 'nmcli', 'device', 'set', 'wlan0', 'managed', 'yes'],
        ['sudo', 'nmcli', 'connection', 'delete', 'id', SSID],  # Replace 'YOUR_SSID' with your SSID variable
        ['sudo', 'nmcli', 'device', 'wifi', 'connect', SSID, 'password', PASSWORD, 'ifname', 'wlan0'],
        # Replace 'YOUR_SSID' and 'YOUR_PASSWORD' with your variables
        ['sudo', 'cp', '-f', '/home/username/Desktop/SoilSaver_Backend/dhcpcd.conf', '/etc/dhcpcd.conf'],
        ['sudo', 'cp', '-f', '/home/username/Desktop/SoilSaver_Backend/dnsmasq.conf', '/etc/dnsmasq.conf'],
        ['sudo', 'cp', '-f', '/home/username/Desktop/SoilSaver_Backend/hostapd', '/etc/default/hostapd'],
        ['sudo', 'systemctl', 'disable', 'hostapd'],
        ['sudo', 'systemctl', 'stop', 'hostapd'],
        ['sudo', 'rm', '-f', '/etc/hostapd/hostapd.conf']
    ]

    for command in commands:
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Success: {result.stdout}")
            print("Wi-Fi credentials updated using NetworkManager. Previous configurations restored.")
            time.sleep(10)
            is_connected()
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}")
            return False



    # time.sleep(20)
    # if is_connected():
    #     print("Successfully connected to Wi-Fi.")
    # else:
    #     print("Failed to connect to Wi-Fi.")
    # return True

@app.route('/')
def hello_world():
    return 'Hello, Raspberry Pi!'

@app.route('/update_wifi', methods=['POST'])
def update_wifi():
    data = request.get_json()

    if 'ssid' not in data or 'password' not in data:
        return jsonify({'error': 'Missing ssid or password'}), 400

    ssid = data['ssid']
    password = data['password']
    print(ssid)
    print(password)

    if setWifi(ssid, password):

        return jsonify({'message': 'Wi-Fi credentials updated successfully'})
    else:
        return jsonify({'error': 'Failed to update Wi-Fi credentials'}), 500

def runApp():
    app.run(host='0.0.0.0', port=8020, debug=True)
