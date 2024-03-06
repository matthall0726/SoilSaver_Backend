import os
import random
import subprocess

def configure_ap_nmcli(ssid, passphrase):
    # Generating a random SSID suffix
    random_number = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    ssid_full = f"{ssid}_{random_number}"

    # Delete existing connection with the same SSID (if exists)
    subprocess.call(['sudo', 'nmcli', 'connection', 'delete', ssid_full], stderr=subprocess.DEVNULL)

    # Create a new Wi-Fi access point
    subprocess.call([
        'sudo', 'nmcli', 'device', 'wifi', 'hotspot',
        'ifname', 'wlan0',
        'con-name', ssid_full,
        'ssid', ssid_full,
        'band', 'bg',  # Use 'a' for 5 GHz
        'channel', '7',
        'password', passphrase
    ])

    print(f"Access Point '{ssid_full}' setup complete.")

if __name__ == "__main__":
    ssid = "Soil_Saver"
    passphrase = "1234567"  # Use a strong passphrase in production
    configure_ap_nmcli(ssid, passphrase)