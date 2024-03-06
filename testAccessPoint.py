import random
import subprocess


def clear_previous_configurations():
    print("Clearing previous configurations...")
    # Move old dnsmasq and hostapd configurations to backup files
    subprocess.call(['sudo', 'mv', '/etc/dnsmasq.conf', '/etc/dnsmasq.conf.backup'], stderr=subprocess.DEVNULL)
    subprocess.call(['sudo', 'mv', '/etc/hostapd/hostapd.conf', '/etc/hostapd/hostapd.conf.backup'],
                    stderr=subprocess.DEVNULL)

    # Clear custom configurations from dhcpcd.conf
    # This example comments out the static IP configuration. Adjust according to your needs.
    with open('/etc/dhcpcd.conf', 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if 'interface wlan0' not in line and 'static ip_address' not in line and 'nohook wpa_supplicant' not in line:
                f.write(line)
        f.truncate()

    # Restart services to apply changes
    subprocess.call(['sudo', 'systemctl', 'daemon-reload'])
    subprocess.call(['sudo', 'systemctl', 'restart', 'dhcpcd'])

def stop_services():
    # Stop the hostapd and dnsmasq services to ensure they don't interfere
    print("Stopping hostapd and dnsmasq services...")
    subprocess.call(['sudo', 'systemctl', 'stop', 'hostapd'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'dnsmasq'])

def create_visible_ap(ssid, password):
    clear_previous_configurations()
    connection_name = ssid

    # Delete existing connection (if exists)
    subprocess.run(['sudo', 'nmcli', 'con', 'del', connection_name], stderr=subprocess.DEVNULL)

    # Create a new Wi-Fi access point connection profile
    subprocess.run([
        'sudo', 'nmcli', 'con', 'add',
        'type', 'wifi',
        'ifname', '*',
        'con-name', connection_name,
        'ssid', ssid,
        'autoconnect', 'yes',
        'save', 'yes'
    ])

    # Set Wi-Fi security
    subprocess.run([
        'sudo', 'nmcli', 'con', 'modify',
        connection_name,
        '802-11-wireless.mode', 'ap',
        '802-11-wireless.band', 'bg',
        'wifi-sec.key-mgmt', 'wpa-psk',
        'wifi-sec.psk', password
    ])

    # Bring up the connection
    subprocess.run(['sudo', 'nmcli', 'con', 'up', connection_name])

    print(f"Visible Access Point '{ssid}' setup complete.")
def start_network_manager():
    # Check if NetworkManager is active
    nm_status = subprocess.run(['sudo', 'systemctl', 'is-active', 'NetworkManager'], stdout=subprocess.PIPE)
    if nm_status.stdout.decode().strip() != "active":
        print("NetworkManager is not active. Starting NetworkManager...")
        # Start NetworkManager service
        subprocess.run(['sudo', 'systemctl', 'start', 'NetworkManager'], check=True)
        print("NetworkManager started.")
    else:
        print("NetworkManager is already running.")

    # Enable NetworkManager to start on boot
    subprocess.run(['sudo', 'systemctl', 'enable', 'NetworkManager'], check=True)
    print("NetworkManager is enabled to start on boot.")

def check_network_manager():
    # Check the status of NetworkManager
    try:
        nm_status_check = subprocess.run(['sudo', 'systemctl', 'status', 'NetworkManager'], stdout=subprocess.PIPE, check=True)
        print(nm_status_check.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Failed to get the status of NetworkManager.")
        print(e)



if __name__ == "__main__":
    random_number = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    ssid = "Soil_Saver_" + random_number
    passphrase = "raspberry"
    stop_services()
    check_network_manager()
    start_network_manager()
    create_visible_ap(ssid, passphrase)
