import json
import time
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, firestore


def load_device_config(file_path='deviceInformation.json'):
    try:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print("Configuration file not found.")
        return None


def update_device_config(file_path, config):
    try:
        with open(file_path, 'w') as json_file:
            json.dump(config, json_file, indent=4)
            print("Configuration file updated.")
    except Exception as e:
        print(f"Failed to update configuration file: {e}")


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    # Subscribe to a topic
    client.subscribe(device_data['topicPath'])

    if not device_data.get('setup', False):

        device_data['setup'] = True
        update_device_config('deviceInformation.json', device_data)

        setup_complete_msg = json.dumps({"status": "Wifi has been set up."})
        client.publish(device_data['topicPath'], setup_complete_msg, qos=1)
    else:
        print("Device setup has already been completed.")

    mqtt_mqtt_msg = json.dumps({"status": "MQTT has been set up."})
    client.publish(device_data['topicPath'], mqtt_mqtt_msg, qos=1)

    if check_firestore_connectivity():
        mqtt_firebase_message = json.dumps({"status": "FireBase has been set up."})
        client.publish(device_data['topicPath'], mqtt_firebase_message, qos=1)


def check_firestore_connectivity():
    try:
        docs = db.collection(u'users').limit(1).get()

        print("Connected to Firestore, collection accessed.")

        if len(docs) > 0:
            print("The collection contains documents.")
        else:
            print("The collection is empty.")

        return True
    except Exception as e:
        print(f"Failed to connect to Firestore: {e}")
        return False


def on_message(client, userdata, msg):
    try:

        incomingData = json.loads(msg.payload.decode())

        print(f"Received message on topic {msg.topic}: {incomingData}")

        if 'wateringTime' in incomingData:
            wateringTime = incomingData['wateringTime']
            print(f"Temperature: {wateringTime}")
        else:
            print("The message does not contain the 'temperature' field.")

        if 'humidity' in incomingData:
            humidity = incomingData['humidity']
            print(f"Humidity: {humidity}")

    except json.JSONDecodeError:
        print("Failed to decode JSON from message.")
    except UnicodeDecodeError:
        print("Failed to decode message payload.")


def main():
    cred_path = "soilsave-firebase-adminsdk-nxl0k-b3187dbd27.json"
    cred = credentials.Certificate(cred_path)
    global db
    db = firestore.client()
    firebase_admin.initialize_app(cred)
    global device_data
    device_data = load_device_config()
    if device_data is None:
        print("Failed to load device configuration. Exiting...")
        return

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Test")
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set()
    client.username_pw_set(device_data['username'], device_data['password'])
    client.connect_async(device_data['broker_address'], device_data['port'])
    client.loop_forever()


if __name__ == "__main__":
    main()
