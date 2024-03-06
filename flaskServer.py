import json
from flask import Flask, request, jsonify
import subprocess
import logging

app = Flask(__name__)

if app.debug:
    app.logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.INFO)


def is_connected():
    try:
        response = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        app.logger.info("Ping was successful")
        return response.returncode == 0

    except Exception as e:
        app.logger.error(f"An error occurred while checking internet connection: {e}")
        return False



def setWifi(SSID, PASSWORD):
    commands = [
        ['sudo', 'systemctl', 'enable', 'NetworkManager'],
        ['sudo', 'systemctl', 'start', 'NetworkManager'],
        ['sudo', 'nmcli', 'radio', 'wifi', 'on'],
        ['sudo', 'nmcli', 'device', 'set', 'wlan0', 'managed', 'yes'],
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
        shutdown_file_path = "shutdown.txt"

        with open(shutdown_file_path, 'w') as file:
            pass  # No need to write anything, just creating or clearin
    else:
        print("Failed to connect to Wi-Fi.")
    return True


def update_topic_path(file_path, new_topic_path):
    try:
        # Load the existing configuration
        with open(file_path, 'r') as file:
            config = json.load(file)

        # Update the 'topicPath' key
        config['topicPath'] = new_topic_path

        # Write the updated configuration back to the file
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)

        print(f"Updated 'topicPath' to '{new_topic_path}' in '{file_path}'.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file '{file_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


@app.route('/update_wifi', methods=['POST'])
def update_wifi():
    data = request.get_json()

    if 'ssid' not in data or 'password' not in data:
        return jsonify({'error': 'Missing ssid or password'}), 400

    ssid = data['ssid']
    password = data['password']
    topicPath = data['topicPath']
    update_topic_path("deviceInformation.json", topicPath)
    print(ssid)
    print(password)

    app.logger.info(f"Received Wi-Fi update request: {data}")

    if setWifi(ssid, password):

        return jsonify({'message': 'Wi-Fi credentials updated successfully'})
    else:
        return jsonify({'error': 'Failed to update Wi-Fi credentials'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8020, debug=True)
