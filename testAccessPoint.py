import os
import random
import subprocess

def reset_network_manager():
    print("Resetting Network Manager...")
    # Reload NetworkManager to clear caches
    subprocess.call(['sudo', 'systemctl', 'restart', 'NetworkManager'])
    # Optionally, delete all saved connections to ensure a clean state
    subprocess.call(['sudo', 'nmcli', 'connection', 'delete', '--all'])

def configure_ap_nmcli(ssid, passphrase):
    # Generating a random SSID suffix
    random_number = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    ssid_full = f"{ssid}_{random_number}"

    print(f"Configuring Access Point: {ssid_full}")

    # Delete existing connection with the same SSID (if exists)
    # This step is now redundant because of the reset, but left here if a selective delete is preferred
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
    passphrase = "raspberry"  # Use a strong passphrase in production
    reset_network_manager()  # Reset Network Manager to clear caches and existing connections
    configure_ap_nmcli(ssid, passphrase)
