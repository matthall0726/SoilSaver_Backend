import os

os.system("sudo apt update")
os.system("sudo apt upgrade")

# Install required software
os.system("sudo apt install hostapd dnsmasq")

# Configure static IP
with open("/etc/dhcpcd.conf", "a") as dhcpcd_file:
    dhcpcd_file.write("\ninterface wlan0\n")
    dhcpcd_file.write("    static ip_address=192.168.4.1/24\n")
    dhcpcd_file.write("    nohook wpa_supplicant\n")

# Configure DNSMASQ
with open("/etc/dnsmasq.conf", "a") as dnsmasq_file:
    dnsmasq_file.write("interface=wlan0\n")
    dnsmasq_file.write("dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h\n")

# Configure HostAPD
hostapd_config = f"""
interface=wlan0
driver=nl80211
ssid=POOPYBUTT
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
with open("/etc/hostapd/hostapd.conf", "w") as hostapd_file:
    hostapd_file.write(hostapd_config)

# Update Hostapd Configuration
os.system("sudo sed -i 's/#DAEMON_CONF=\"\"/DAEMON_CONF=\"\/etc\/hostapd\/hostapd.conf\"/' /etc/default/hostapd")

# Start Services
os.system("sudo systemctl unmask hostapd")
os.system("sudo systemctl enable hostapd")
os.system("sudo systemctl enable dnsmasq")

# Restart Raspberry Pi
os.system("sudo reboot")



