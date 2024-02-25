import time
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)



def is_connected():
    try:
        # Ping command varies depending on the operating system
        # -c: number of pings to send (1 for a simple check)
        response = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Check if ping command was successful
        return response.returncode == 0
    except Exception as e:
        print(f"An error occurred while checking internet connection: {e}")
        return False

# Example usage
if is_connected():
    print("Device is connected to the internet.")
else:
    print("Device is not connected to the internet.")

def setWifi(SSID, PASSWORD):
    COUNTRY_CODE = "US"
    wpa_supplicant_conf = f"""country={COUNTRY_CODE}
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{SSID}"
    psk="{PASSWORD}"
}}
"""
    wpa_supplicant_path = "/etc/wpa_supplicant/wpa_supplicant.conf"

    # Update wpa_supplicant.conf using echo and subprocess with sudo
    try:
        backup_dhcpcd_conf_path = "/home/wokahontas/Desktop/SoilSaver_Backend/dhcpcd.conf"
        # The target path for dhcpcd.conf
        target_dhcpcd_conf_path = "/etc/dhcpcd.conf"

        backup_dnsmasq_conf_path = "/home/wokahontas/Desktop/SoilSaver_Backend/dnsmasq.conf"

        target_dnsmasq_conf_path = "/etc/dnsmasq.conf"

        backup_hostapd_conf_path = "/home/wokahontas/Desktop/SoilSaver_Backend/hostapd"

        target_hostapd_conf_path = "/etc/default/hostapd"

        subprocess.run(['sudo', 'bash', '-c', f'echo "{wpa_supplicant_conf}" > {wpa_supplicant_path}'], check=True)

        # Remove access point configurations and restart services using subprocess with sudo
        commands = [
            f"sudo cp {backup_dhcpcd_conf_path} {target_dhcpcd_conf_path}",
            f"sudo cp {backup_dnsmasq_conf_path} {target_dnsmasq_conf_path}",
            f"sudo cp {backup_hostapd_conf_path} {target_hostapd_conf_path}",
            "sudo service dhcpcd restart",
            "sudo systemctl stop hostapd",
            "sudo systemctl disable hostapd",
            "sudo rm /etc/hostapd/hostapd.conf",
            "sudo systemctl restart dnsmasq"
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)
        time.sleep(20)
        is_connected()
        print("Wi-Fi credentials updated and access point configurations removed. Services restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return False
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
    print(ssid)
    print(password)

    if setWifi(ssid, password):
        return jsonify({'message': 'Wi-Fi credentials updated successfully'})
    else:
        return jsonify({'error': 'Failed to update Wi-Fi credentials'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8020, debug=True)
