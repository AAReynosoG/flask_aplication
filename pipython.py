from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import ssl

app = Flask(__name__)

topic = "motors/control"


def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT con resultado: " + str(rc))


client = mqtt.Client()
client.on_connect = on_connect

client.tls_set(
    ca_certs='./AmazonRootCA1.pem',
    certfile='./cec69141d6f3a0869a78f2331a3b6acebf6bc9ddb27a738dc3945c2ea4a99618-certificate.pem.crt',
    keyfile='./cec69141d6f3a0869a78f2331a3b6acebf6bc9ddb27a738dc3945c2ea4a99618-private.pem.key',
    tls_version=ssl.PROTOCOL_SSLv23)
client.tls_insecure_set(True)

client.connect("a169mg5ru5h2z1-ats.iot.us-east-2.amazonaws.com", 8883, 60)


def send_message(key):
    client.publish(topic, payload=key, qos=0, retain=False)
    print("Mensaje enviado")


@app.route('/api/mqtt/<string:key>', methods=['POST'])
def send_key(key):
    allowed_keys = ['w', 'a', 's', 'd', 'e', 'q']
    if key not in allowed_keys:
        return jsonify({'Message': 'Key not allowed'}), 400
    try:
        send_message(key)
    except Exception as e:
        return jsonify({'Message': 'Error sending message: {}'.format(e)}), 500
    return jsonify({'Message': 'Message sent'}), 200


if __name__ == "__main__":
    client.loop_start()
    app.run(port=5000, debug=True)
