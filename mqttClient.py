import json
import time
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe

# Initialize Firebase Admin
cred = credentials.Certificate("soilsave-firebase-adminsdk-nxl0k-b3187dbd27.json")
firebase_admin.initialize_app(cred)


with open("deviceInformation.json", "r") as json_file:
    device_data = json.load(json_file)


broker_address = "nc41d4ec.ala.us-east-1.emqxsl.com"
port = 8883
username = "wokahontas"
password = "1234"
client_id = "PythonClient"

# Connect callback
def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")
    client.subscribe(device_data['topicPath'])

# Message callback
def on_message(client, userdata, message):
    payload_str = message.payload.decode("utf-8")
    data = json.loads(payload_str)
    wateringTime = data.get("wateringTime")
    if wateringTime is not None:
        water_plant(wateringTime)

# Simulate watering plant
def water_plant(wateringTime):
    print(f"Watering for {wateringTime} seconds.")
    time.sleep(wateringTime)
    # Here, add your GPIO code to control the hardware

# Publish to a topic
def create_topic(payload, topic_path):
    publish.single(topic_path, payload, port=port,
                   hostname=broker_address,
                   client_id=client_id,
                   auth={'username': username, 'password': password},
                   qos=1)

# Subscribe to a topic
def subscribe_to_topic(topic_path):
    subscribe.simple(topic_path, port=port, qos=1,
                     hostname=broker_address,
                     client_id=client_id,
                     auth={'username': username, 'password': password})

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set()
    client.username_pw_set(username, password)
    client.connect_async(broker_address, port)
    client.loop_forever()

if __name__ == "__main__":
    main()