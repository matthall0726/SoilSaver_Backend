from flask import Flask, request, jsonify
import os

app = Flask(__name__)


def setWifi(SSID, PASSWORD):
    COUNTRY_CODE = "US"

    # Path to wpa_supplicant.conf file on the Raspberry Pi's boot partition
    wpa_supplicant_path = "/etc/wpa_supplicant/wpa_supplicant.conf"

    # Create or update wpa_supplicant.conf
    with open(wpa_supplicant_path, "w") as wpa_file:
        wpa_file.write(f"""country={COUNTRY_CODE}
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{SSID}"
    psk="{PASSWORD}"
}}
""")

    print("Wi-Fi credentials updated successfully.")

    # Remove access point configurations
    os.system("sudo sed -i '/interface=wlan0/,/auth_algs=1/d' /etc/dhcpcd.conf")
    os.system("sudo sed -i '/interface=wlan0/,/dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h/d' /etc/dnsmasq.conf")
    os.system("sudo sed -i '/interface=wlan0/,/ssid=POOPYBUTT/d' /etc/hostapd/hostapd.conf")
    os.system("sudo sed -i 's/DAEMON_CONF=\"\/etc\/hostapd\/hostapd.conf\"/#DAEMON_CONF=\"\"/' /etc/default/hostapd")

    # Restart services
    os.system("sudo service dhcpcd restart")
    os.system("sudo systemctl restart hostapd")
    os.system("sudo systemctl restart dnsmasq")
    print("Access point configurations removed. Services restarted.")

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

    setWifi(ssid, password)

    return jsonify({'message': 'Wi-Fi credentials updated successfully'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8020, debug=True)
