import paho.mqtt.client as mqtt
import json

# MQTT configuration
broker = "192.168.88.153"                    # -h localhost
port = 1883                             # -p 1883
access_token = "2djXfqHWLvqQmrW9B5OX"   # -u <access_token>
topic = "v1/devices/me/telemetry"      # -t <topic>
payload = {"temperature": 42}          # -m "{\"temperature\":25}"

# Initialize MQTT client with updated API
client = mqtt.Client()

# Set access token as username
client.username_pw_set(access_token)

# Optional: Define callbacks if needed
def on_publish(client, userdata, mid):
    print("Message published (mid={})".format(mid))

client.on_publish = on_publish

# Connect to broker
client.connect(broker, port, keepalive=60)

# Publish with QoS 1 (same as -q 1)
result = client.publish(topic, json.dumps(payload), qos=1)

# Wait for publish to complete
result.wait_for_publish()

# Disconnect
client.disconnect()
