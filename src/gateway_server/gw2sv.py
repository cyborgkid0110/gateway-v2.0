
# from lib.dao import SqliteDAO
import json
import time
import sys
import os
from lib.mqtt import Client, Topic

# serverTopics = {"data_request": "farm/monitor/sensor",        OK
#                   "energy_data" : "farm/monitor/sensor",      OK
#                   "actuator_data": "farm/monitor/actuator",   OK
#                   "send_setpoint": "farm/control",
#                   "send_setpoint_ack": "farm/control", 
#                   "server_delete": "farm/sync_node",
#                   "server_delete_ack": "farm/sync_node_ack",
#                   "server_add": "farm/sync_node",
#                   "server_add_ack": "farm/sync_node_ack",
#                   "keep_alive_ack": "farm/monitor/alive"}

# SERVER_DELETE_TOPIC = "farm/sync_node"          # deprecated
# SERVER_DELETE_ACK_TOPIC = "farm/sync_node_ack"  # deprecated
# "server_add": "farm/sync_node",                 # deprecated
# "server_add_ack": "farm/sync_node_ack",

SENSOR_DATA_TOPIC = "farm/monitor/sensor"
ACTUATOR_DATA_TOPIC = "farm/monitor/actuator"
SEND_SETPOINT_TOPIC = "farm/control"
SEND_SETPOINT_ACK_TOPIC = "farm/control" 
SCAN_DEVICE_TOPIC = "farm/node/scan"
ADD_NODE_TOPIC = "farm/node/add"
NEW_NODE_TOPIC = "farm/node/new"
DELETE_NODE_TOPIC = "farm/node/delete"
KEEPALIVE_ACK_TOPIC = "farm/monitor/alive"

BROKER_SERVER = 'test.mosquitto.org'
PORT = 1883
KEEPALIVE = 60

btmesh = None
room_id = 1         # this must be taken from database

# def printHello(message):
#     print(message)

def checkDBusStatus():
    if btmesh is None:
        print("Cannot connect to btmesh_app by DBus")
        return False
    
    return True

class GatewayService(dbus.service.Object):
    def __init__(self, bus_name, object_path='/org/ipac/btmesh'):
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.method('org.ipac.btmesh', in_signature='', out_signature='')
    def Gateway(self):
        scan_device_cmd()

def mqtt_recv_scan_device(msg):
    if checkDBusStatus() == False:
        return
    if (msg['info']['room_id'] == room_id):
        if (msg['info']['protocol'] == 'ble_mesh'):
            btmesh.BtmeshScanDevice()
        elif (msg['info']['protocol'] == 'wifi'):
            pass

def mqtt_recv_add_device(msg):
    if checkDBusStatus() == False:
        return
    if (msg['info']['room_id'] == room_id):
        if (msg['info']['protocol'] == 'ble_mesh'):
            btmesh.BtmeshAddDevice(msg['info']['dev_info'])
        elif (msg['info']['protocol'] == 'wifi'):
            pass

def mqtt_recv_new_node_info(msg):
    if checkDBusStatus() == False:
        return
    if (msg['info']['room_id'] == room_id):
        if (msg['info']['protocol'] == 'ble_mesh'):
            # btmesh.BtmeshSendAssignedNodeInfo()
            pass
        elif (msg['info']['protocol'] == 'wifi'):
            pass

def mqtt_recv_delete_node(msg):
    if checkDBusStatus() == False:
        return
    if (msg['info']['room_id'] == room_id):
        if (msg['info']['protocol'] == 'ble_mesh'):
            btmesh.BtmeshDeleteNode(msg['info']['dev_info'])
            pass
        elif (msg['info']['protocol'] == 'wifi'):
            pass

def main():
    global btmesh
    bus = dbus.SessionBus()
    btmesh = bus.get_object('ipac.example.Service', '/ipac/example/Service')

    topic = {
        'publish': [],
        'subscribe': [],
    }
    # test_topic = Topic('test/011003', printHello)
    # topic['subscribe'].append(test_topic)

    client = Client(topic)
    client.connect(BROKER_SERVER, PORT, KEEPALIVE)
    client.loop_forever()