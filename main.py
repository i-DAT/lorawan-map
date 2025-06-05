import paho.mqtt.client as mqtt
import json
from pprint import pprint


with open("secrets.json", "r") as f:
    secrets = json.load(f)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        raise RuntimeError(f"Failed to connect to MQTT broker: {reason_code}")
    for topic in secrets["topics"].values():
        client.subscribe(topic)


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    print(msg.topic)
    pprint(payload["uplink_message"]["decoded_payload"])
    print()


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(secrets["username"], secrets["password"])
client.tls_set()

client.connect(secrets["url"], secrets["port"])
client.loop_forever()
