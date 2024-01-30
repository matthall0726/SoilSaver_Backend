from flask import Flask, request, jsonify
import os

app = Flask(__name__)

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
    app.run(host='0.0.0.0', port=5000, debug=True)


def setWifi(SSID, PASSWORD):
    COUNTRY_CODE = "US"

    # Path to wpa_supplicant.conf file on the Raspberry Pi's boot partition
    wpa_supplicant_path = "/path/to/mounted/boot/partition/wpa_supplicant.conf"

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

    print("Wi-Fi credentials updated successfully. Rebooting...")

    # Reboot the Raspberry Pi
    os.system("sudo reboot")
