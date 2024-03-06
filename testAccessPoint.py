import subprocess

def stop_services():
    # Stop the hostapd and dnsmasq services to ensure they don't interfere
    print("Stopping hostapd and dnsmasq services...")
    subprocess.call(['sudo', 'systemctl', 'stop', 'hostapd'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'dnsmasq'])

def create_visible_ap(ssid, password):
    # Define connection name
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

if __name__ == "__main__":
    ssid = "Your_SSID"
    password = "Your_Password"
    stop_services()  # Ensure hostapd and dnsmasq are stopped
    create_visible_ap(ssid, password)
