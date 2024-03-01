import os
import subprocess

def install_packages():
    subprocess.call(['sudo', 'apt-get', 'install', 'hostapd', 'dnsmasq', '-y'])

def configure_ap(ssid, passphrase):
    # Stop services
    subprocess.call(['sudo', 'systemctl', 'stop', 'hostapd'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'dnsmasq'])

    # Set up wlan0 with a static IP
    with open('/etc/dhcpcd.conf', 'a') as f:
        f.write('interface wlan0\nstatic ip_address=192.168.1.6/24\nnohook wpa_supplicant\n')

    # Restart dhcpcd
    subprocess.call(['sudo', 'service', 'dhcpcd', 'restart'])

    # Configure dnsmasq
    dnsmasq_conf = """interface=wlan0
dhcp-range=192.168.1.10,192.168.1.20,255.255.255.0,24h
"""
    with open('/etc/dnsmasq.conf', 'w') as f:
        f.write(dnsmasq_conf)

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
    with open('/etc/hostapd/hostapd.conf', 'w') as f:
        f.write(hostapd_conf)

    # Point hostapd to the configuration file
    with open('/etc/default/hostapd', 'a') as f:
        f.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"\n')

    # Enable and start hostapd and dnsmasq
    subprocess.call(['sudo', 'systemctl', 'unmask', 'hostapd'])
    subprocess.call(['sudo', 'systemctl', 'enable', 'hostapd'])
    subprocess.call(['sudo', 'systemctl', 'start', 'hostapd'])
    subprocess.call(['sudo', 'systemctl', 'restart', 'dnsmasq'])

    print("Access Point setup complete. SSID: ", ssid)

if __name__ == "__main__":
    ssid = "PiZeroAP"
    passphrase = "raspberry"  # Use a strong passphrase in production
    configure_ap(ssid, passphrase)