import time
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import ssl
from flask_cors import CORS
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

topic = "motors/control"
topic2 = "triggers/control"


def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result: " + str(rc))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    while not client.is_connected():
        print("Attempting to reconnect...")
        try:
            client.reconnect()
        except ConnectionRefusedError:
            print("Failed to reconnect, retrying in 5 seconds...")
            time.sleep(5)


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.tls_set(
    ca_certs='./AmazonRootCA1.pem',
    certfile='./cec69141d6f3a0869a78f2331a3b6acebf6bc9ddb27a738dc3945c2ea4a99618-certificate.pem.crt',
    keyfile='./cec69141d6f3a0869a78f2331a3b6acebf6bc9ddb27a738dc3945c2ea4a99618-private.pem.key',
    tls_version=ssl.PROTOCOL_SSLv23)
client.tls_insecure_set(False)

client.connect("a169mg5ru5h2z1-ats.iot.us-east-2.amazonaws.com", 8883, 65000)
client.loop_start()


def send_message(key):
    if client.is_connected():
        if key == 'v' or key == 'b':
            client.publish(topic2, payload=key, qos=0, retain=False)
        else:
            client.publish(topic, payload=key, qos=0, retain=False)
        return 'Connected and message sent'
    elif not client.is_connected():
        raise Exception("Client not connected")


load_dotenv()


@app.route('/api/mqtt/<string:key>', methods=['POST'])
def send_key(key):
    auth_header = request.headers.get('Authorization')

    expected_auth_header = os.getenv('AUTH_HEADER')

    if auth_header is None or auth_header != expected_auth_header:
        return jsonify({'Message': 'Unauthorized'}), 401

    allowed_keys = ['w', 'a', 's', 'd', 'e', 'i', 'k', 'o', 'p', '1', '2', 'x', 'u', 'j', 'v', 'b']
    if key not in allowed_keys:
        return jsonify({'Message': 'Key not allowed'}), 400
    try:
        message = send_message(key)
    except Exception as e:
        return jsonify({'Message': 'Error sending message: {}'.format(e)}), 500
    return jsonify({'Message': message}), 200


if __name__ == "__main__":
    app.run()
