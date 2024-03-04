import json
from flask import Flask, request, jsonify
import subprocess
import logging

app = Flask(__name__)

if app.debug:
    app.logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.INFO)

app = Flask(__name__)

def is_connected():
    try:
        response = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        app.logger.info("Ping was successful")
        return response.returncode == 0

    except Exception as e:
        app.logger.error(f"An error occurred while checking internet connection: {e}")
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
        ['sudo', 'cp', '-f', '/home/wokahontas/Desktop/SoilSaver_Backend/dhcpcd.conf', '/etc/dhcpcd.conf'],
        ['sudo', 'cp', '-f', '/home/wokahontas/Desktop/SoilSaver_Backend/dnsmasq.conf', '/etc/dnsmasq.conf'],
        ['sudo', 'cp', '-f', '/home/wokahontas/Desktop/SoilSaver_Backend/hostapd', '/etc/default/hostapd'],
        ['sudo', 'systemctl', 'disable', 'hostapd'],
        ['sudo', 'systemctl', 'stop', 'hostapd'],
        ['sudo', 'rm', '-f', '/etc/hostapd/hostapd.conf']
    ]

    for command in commands:
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            app.logger.info(f"Success: {result.stdout}")
            app.logger.info("Wi-Fi credentials updated using NetworkManager. Previous configurations restored.")

        except subprocess.CalledProcessError as e:
            app.logger.error(f"Error: {e.stderr}")
            return False

    if is_connected():
        print("Successfully connected to Wi-Fi.")
        shutdown_server()
    else:
        print("Failed to connect to Wi-Fi.")
    return True

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
    topicPath = data['topicPath']
    print(ssid)
    print(password)

    app.logger.info(f"Received Wi-Fi update request: {data}")

    if setWifi(ssid, password):

        return jsonify({'message': 'Wi-Fi credentials updated successfully'})
    else:
        return jsonify({'error': 'Failed to update Wi-Fi credentials'}), 500


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.post('/update_topic')
def update_device_topic():
    data = request.get_json()
    topic_path = data.get('topicPath')
    if not topic_path:
        return "topicPath is required", 400

    json_file_path = "deviceInformation.json"

    try:
        with open(json_file_path, "r") as json_file:
            device_data = json.load(json_file)
    except (IOError, json.JSONDecodeError) as e:
        return f"Failed to read or parse the JSON file: {str(e)}", 500

    device_data['topicPath'] = topic_path

    try:
        with open(json_file_path, "w") as json_file:
            json.dump(device_data, json_file, indent=4)
    except IOError as e:
        return f"Failed to write to the JSON file: {str(e)}", 500

    return "Updated"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8020, debug=True)

