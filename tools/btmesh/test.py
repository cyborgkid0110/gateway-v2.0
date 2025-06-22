import paho.mqtt.client as mqtt
import json

# MQTT Configuration
BROKER = "192.168.88.192"
# BROKER = "192.168.2.81"
PORT = 1883
KEEPALIVE = 60

access_token = "2djXfqHWLvqQmrW9B5OX"

# MQTT client setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        return
        # print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Received on {msg.topic}: {msg.payload.decode()}")

def connect_mqtt():
    # client.username_pw_set(access_token)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, KEEPALIVE)
    client.loop_start()

def scan_device():
    topic = 'farm/node/scan'
    message = {
        'operator': 'scan_device',
        'status': 1,
        'info': {
            'protocol': 'ble_mesh',
            'room_id': 407,
        }
    }
    result = client.publish(topic, json.dumps(message))
    status = result.rc
    if status == 0:
        print(f"Message sent to {topic}")
    else:
        print(f"Failed to send message to {topic}")

def add_node():
    topic = 'farm/node/add'
    uuid = input("Enter UUID: ").strip()
    mac = input("Enter MAC: ").strip()
    message = {
        "operator": "add_node",
        "status": 1,
        "info": {
            "room_id": 407,
            "protocol": "ble_mesh",
            "remote_prov": {
                "enable": 0,
                "unicast": 0
            },
            "dev_info": {
                "uuid": uuid,
                "device_name": "IPAC_LAB_SMART_FARM",
                "mac": mac,
                "address_type": 0,
                "oob_info": 0,
                "adv_type": 3,
                "bearer_type": "PB-ADV",
            }
        }
    }
    result = client.publish(topic, json.dumps(message))
    status = result.rc
    if status == 0:
        print(f"Message sent to {topic}")
    else:
        print(f"Failed to send message to {topic}")

def ac_control():
    topic = 'farm/control'
    message = {
        "operator": "actuator_control",
        "status": 1,
        "info": {
            "room_id": 407,
            "node_id": 1,
            "protocol": "ble_mesh",
            "function": 'AirCon',
            "control_state": {
                'setpoint': 17,
                'mode': 1,
                'start_time': 1,
                'end_time': 1,
                'status': 1,
            }
        }
    }
    result = client.publish(topic, json.dumps(message))
    status = result.rc
    if status == 0:
        print(f"Message sent to {topic}")
    else:
        print(f"Failed to send message to {topic}")

def subscribe_topic():
    topic = input("Enter topic to subscribe: ").strip()
    client.subscribe(topic)
    print(f"Subscribed to {topic}")

def exit_program():
    print("Exiting program...")
    client.loop_stop()
    client.disconnect()

def unknown_command():
    print("Unknown command.")

# Command handler
def handle_command(cmd):
    commands = {
        "scan_device": scan_device,
        "subscribe": subscribe_topic,
        "exit": exit_program,
        "add_node": add_node,
        'ac_control':  ac_control
    }
    action = commands.get(cmd, unknown_command)
    action()

# CLI loop
def cli():
    print("BtMesh Test started.")

    while True:
        cmd = input("> ").strip().lower()
        if cmd == "exit":
            handle_command(cmd)
            break
        handle_command(cmd)

# Main
if __name__ == "__main__":
    connect_mqtt()
    cli()
