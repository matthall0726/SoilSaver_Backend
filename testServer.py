import threading
import os
import json
import logging
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class WiFiHTTPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/update_wifi':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.process_update_wifi(post_data)
        else:
            self.send_response(404)
            self.end_headers()

    def process_update_wifi(self, post_data):
        try:
            data = json.loads(post_data.decode('utf-8'))
            print(f"Received data: {data}")
            ssid = data.get('ssid')
            password = data.get('password')
            topicPath = data.get('topicPath')

            if not ssid or not password:
                self.send_error(400, "Missing SSID or password")
                return

            success = setWifi(ssid, password)
            if success:
                update_topic_path("deviceInformation.json", topicPath)
                subprocess.run(['touch', 'shutdown.txt'], check=True)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Wi-Fi credentials updated successfully")
            else:
                self.send_error(500, "Failed to update Wi-Fi credentials")
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            logging.error(f"Error processing Wi-Fi update: {e}")
            self.send_error(500, "Internal server error")


def is_connected():
    try:
        subprocess.check_call(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("Internet connectivity check was successful.")
        return True
    except subprocess.CalledProcessError:
        logging.warning("Internet connectivity check failed.")
        return False


def setWifi(SSID, PASSWORD):
    commands = [
        ['sudo', 'systemctl', 'enable', 'NetworkManager'],
        ['sudo', 'systemctl', 'start', 'NetworkManager'],
        ['sudo', 'nmcli', 'radio', 'wifi', 'on'],
        ['sudo', 'nmcli', 'device', 'set', 'wlan0', 'managed', 'yes'],
        ['sudo', 'nmcli', 'device', 'wifi', 'connect', SSID, 'password', PASSWORD, 'ifname', 'wlan0'],
        ['sudo', 'systemctl', 'disable', 'hostapd'],
        ['sudo', 'systemctl', 'stop', 'hostapd'],
        ['sudo', 'rm', '-f', '/etc/hostapd/hostapd.conf']
    ]
    for command in commands:
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info(f"Executed: {' '.join(command)}")
            if result.stdout:
                logging.info(result.stdout.decode())
            if result.stderr:
                logging.warning(result.stderr.decode())
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to execute command: {' '.join(e.cmd)}, Error: {e.stderr.decode()}")
            return False
    return True


def update_topic_path(file_path, new_topic_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        config['topicPath'] = new_topic_path
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
        logging.info(f"Updated 'topicPath' to '{new_topic_path}' in '{file_path}'.")
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file '{file_path}'.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def run(server_class=HTTPServer, handler_class=WiFiHTTPHandler, port=8020, host='0.0.0.0'):
    global httpd  # Indicate that we are using the global httpd variable
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting httpd server {host}:{port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        logging.info("Stopping httpd server...")

# Your existing function implementations for is_connected, setWifi, and update_topic_path

def check_shutdown_trigger():
    global httpd
    while True:
        if os.path.exists("shutdown.txt"):
            print("Shutdown trigger found. Shutting down server.")
            if httpd:  # Check if httpd is not None
                httpd.shutdown()  # Gracefully shut down the server
                os.remove("shutdown.txt")
                break

if __name__ == "__main__":
    host_ip = '0.0.0.0'
    port = 8020
    server_thread = threading.Thread(target=lambda: run(HTTPServer, WiFiHTTPHandler, port, host_ip))
    server_thread.start()

    time.sleep(2)
    # Check for shutdown trigger in the main thread
    check_shutdown_trigger()

    # Wait for the server thread to finish (i.e., until the server is shut down)
    server_thread.join()
    print("Server has been shut down.")


