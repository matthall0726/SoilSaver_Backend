import subprocess
import random

def run_command(command, use_sudo=False):
    """
    Executes a system command, optionally with sudo.
    """
    if use_sudo:
        command.insert(0, 'sudo')
    subprocess.call(command, check=True)

def append_to_file(file_path, content, use_sudo=False):
    """
    Appends given content to the file at file_path, optionally using sudo.
    """
    command = f"echo '{content}' | tee -a {file_path}"
    if use_sudo:
        command = "sudo " + command
    subprocess.call(command, shell=True, check=True)

def write_to_file(file_path, content, use_sudo=False):
    """
    Writes given content to the file at file_path, optionally using sudo.
    """
    command = f"echo '{content}' | tee {file_path}"
    if use_sudo:
        command = "sudo " + command
    subprocess.call(command, shell=True, check=True)

def install_packages():
    """
    Install necessary packages using apt-get.
    """
    run_command(['apt-get', 'install', 'hostapd', 'dnsmasq', '-y'], use_sudo=True)

def configure_ap(ssid, passphrase):
    """
    Configure and start the access point with the given SSID and passphrase.
    """
    # Stop services
    run_command(['systemctl', 'stop', 'hostapd'], use_sudo=True)
    run_command(['systemctl', 'stop', 'dnsmasq'], use_sudo=True)

    # Set up wlan0 with a static IP
    dhcpcd_content = 'interface wlan0\nstatic ip_address=192.168.1.6/24\nnohook wpa_supplicant\n'
    append_to_file('/etc/dhcpcd.conf', dhcpcd_content, use_sudo=True)

    # Restart dhcpcd
    run_command(['service', 'dhcpcd', 'restart'], use_sudo=True)

    # Configure dnsmasq
    dnsmasq_conf = """interface=wlan0
dhcp-range=192.168.1.10,192.168.1.20,255.255.255.0,24h
"""
    write_to_file('/etc/dnsmasq.conf', dnsmasq_conf, use_sudo=True)

    # Configure hostapd
    hostapd_conf = f"""interface=wlan0
driver=nl80211
ssid={ssid}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={passphrase}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
    write_to_file('/etc/hostapd/hostapd.conf', hostapd_conf, use_sudo=True)

    # Point hostapd to the configuration file
    append_to_file('/etc/default/hostapd', 'DAEMON_CONF="/etc/hostapd/hostapd.conf"\n', use_sudo=True)

    # Enable and start hostapd and dnsmasq
    run_command(['systemctl', 'unmask', 'hostapd'], use_sudo=True)
    run_command(['systemctl', 'enable', 'hostapd'], use_sudo=True)
    run_command(['systemctl', 'start', 'hostapd'], use_sudo=True)
    run_command(['systemctl', 'restart', 'dnsmasq'], use_sudo=True)

    print("Access Point setup complete. SSID:", ssid)

if __name__ == "__main__":
    random_number = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    ssid = "SoilSaver_" + random_number
    passphrase = "raspberry"  # Reminder: Use a strong passphrase in production
    install_packages()
    configure_ap(ssid, passphrase)
