from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

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
        subprocess.run(['sudo', 'bash', '-c', f'echo "{wpa_supplicant_conf}" > {wpa_supplicant_path}'], check=True)

        # Remove access point configurations and restart services using subprocess with sudo
        commands = [
            "sudo sed -i '/interface=wlan0/,/auth_algs=1/d' /etc/dhcpcd.conf",
            "sudo sed -i '/interface=wlan0/,/dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h/d' /etc/dnsmasq.conf",
            "sudo sed -i '/interface=wlan0/,/ssid=POOPYBUTT/d' /etc/hostapd/hostapd.conf",
            "sudo sed -i 's/DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"/#DAEMON_CONF=\"\"/' /etc/default/hostapd",
            "sudo service dhcpcd restart",
            "sudo systemctl restart hostapd",
            "sudo systemctl restart dnsmasq"
        ]

        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)

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

    if setWifi(ssid, password):
        return jsonify({'message': 'Wi-Fi credentials updated successfully'})
    else:
        return jsonify({'error': 'Failed to update Wi-Fi credentials'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8020, debug=True)
