
# from lib.dao import SqliteDAO
import json
import time
import sys
import os
# from lib.mqtt import Client, Topic
import paho.mqtt.client as mqtt
from lib.logs import Log

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

BROKER_SERVER = '192.168.8.103'     # test broker
PORT = 1883
KEEPALIVE = 60

room_id = 1         # this must be taken from database

client = None       # MQTT client

bus = None
btmesh_service = None
btmesh_interface = None

def dbus_call_proxy_object():
    global btmesh_service
    global btmesh_interface
    
    try:
        btmesh_service = bus.get_object('org.ipac.btmesh', '/org/ipac/btmesh')
        btmesh_interface = dbus.Interface(btmesh_service, 'org.ipac.btmesh')
    except dbus.exceptions.DBusException:
        print('Cannot connect to BtmeshService')
        return False
    
    return True

def mqtt_recv_scan_device(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return

    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'scan_device':
            if (msg['info']['protocol'] == 'ble_mesh'):
                btmesh_interface.BtmeshScanDevice()
            elif (msg['info']['protocol'] == 'wifi'):
                pass

def mqtt_recv_add_device(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return

    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'add_node':
            if (msg['info']['protocol'] == 'ble_mesh'):
                btmesh_interface.BtmeshAddDevice(msg['info']['dev_info'])
            elif (msg['info']['protocol'] == 'wifi'):
                pass

def mqtt_recv_new_node_info(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return

    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'new_node_info_ack':
            # add node info database
            if (msg['info']['protocol'] == 'ble_mesh'):
                pass
            elif (msg['info']['protocol'] == 'wifi'):
                pass

def mqtt_recv_delete_node(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return
    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'delete_node':
            if (msg['info']['protocol'] == 'ble_mesh'):
                btmesh_interface.BtmeshDeleteNode(msg['info']['dev_info'])
            elif (msg['info']['protocol'] == 'wifi'):
                pass

class GatewayClient(mqtt.Client):
    def __init__(self, topic):
        super().__init__()
        self.__logger = Log(__name__)
        self.__topic = topic

    def on_connect(self, client, userdata, flags, rc):
        """Called when the broker responds to our connection request"""
        # The connection result
        if rc == 0:
            self.__logger.info("Connected to broker")
            for topic in self.__topic:
                self.subscribe(topic)
    
    def on_connect_fail(self, client, userdata):
        """Called when the client failed to connect to the broker"""
        self.__logger.info("Unconnected to broker")

    def on_disconnect(self, client, userdata, rc):
        if rc == 0:
            self.__logger.info("Gateway disconnected to broker")

    def on_message(self, client, userdata, msg):
        """Called when a message has been received on a topic that the client subscribes to"""
        # self.__msg = msg.payload.decode("utf-8")
        self.__msg = json.loads(msg.payload.decode())
        if (msg.topic == SCAN_DEVICE_TOPIC):
            mqtt_recv_scan_device(self.__msg)
        if (msg.topic == ADD_NODE_TOPIC):
            mqtt_recv_add_device(self.__msg)
        if (msg.topic == NEW_NODE_TOPIC):
            mqtt_recv_new_node_info(self.__msg)
        if (msg.topic == DELETE_NODE_TOPIC):
            mqtt_recv_delete_node(self.__msg)
        if (msg.topic == KEEPALIVE_ACK_TOPIC):
            pass

    def on_publish(self, client, userdata, mid):
        '''Called when publish() function has been used'''
        self.__logger.info("Published successfully")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Publish a message on a topic"""
        self.__logger.info(f"Subscribed to {self.__topic} successfully")

class GatewayService(dbus.service.Object):
    def __init__(self, bus_name, object_path='/org/ipac/gateway'):
        bus_name = dbus.service.BusName('org.ipac.gateway', bus=bus)
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.method('org.ipac.gateway', in_signature='b', out_signature='')
    def BtmeshScanDeviceAck(self, scan_status):
        msg = {
            'operator': 'scan_device_ack',
            'status': (1 if (scan_status == True) else 0),
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(SCAN_DEVICE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send new node info to server')

    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def BtmeshScanResult(self, scan_result):
        msg = {
            'operator': 'scan_result',
            'status': 1,
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'dev_info': {
                    'uuid': scan_result['uuid'],
                    'device_name': scan_result['device_name'],   # this name should be assigned from device
                    'mac': scan_result['mac'],
                    'address_type': scan_result['address_type'],
                    'oob_info': scan_result['oob_info'],
                    'adv_type': scan_result['adv_type'],
                    'bearer_type': scan_result['bearer_type'],
                    'rssi': scan_result['rssi']
                }
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(SCAN_DEVICE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send new node info to server')

    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def BtmeshNewNodeInfo(self, new_node_info):
        msg = {
            'operator': 'new_node_info',
            'status': 1,
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'dev_info': {
                    'function': new_node_info['function'],
                    'uuid': new_node_info['uuid'],
                    'device_name': new_node_info['device_name'],   # this name should be assigned from device
                    'unicast': new_node_info['unicast'],
                }
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(NEW_NODE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send scan device result to server')

    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def BtmeshAddNodeAck(self, add_node_ack):
        msg = {
            'operator': 'add_node_ack',
            'status': add_node_ack['status'],
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'dev_info': {
                    'uuid': add_node_ack['uuid'],
                    'device_name': add_node_ack['device_name'],   # this name should be assigned from device
                    'mac': add_node_ack['mac'],
                    'address_type': add_node_ack['address_type'],
                    'oob_info': add_node_ack['oob_info'],
                    'adv_type': add_node_ack['adv_type'],
                    'bearer_type': add_node_ack['bearer_type'],
                }
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(ADD_NODE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send scan device result to server')
    
    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def BtmeshDeleteNodeAck(self, delete_node_ack):
        node_id = 1                                 # for test only
        uuid = 'cb5da3ba5e4445f6aa45898e961fad0f'   # must take from database
        # after taking data from database, delete node if status = 1
        msg = {
            'operator': 'delete_node_ack',
            'status': delete_node_ack['status'],
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'dev_info': {
                    'node_id': node_id,
                    'unicast': delete_node_ack['unicast'],
                    'uuid': uuid,
                }
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(DELETE_NODE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send delete node result to server')

def main():
    global bus
    global btmesh
    global client

    bus = dbus.SessionBus()
    topic = [
        SCAN_DEVICE_TOPIC,
        ADD_NODE_TOPIC,
        NEW_NODE_TOPIC,
        DELETE_NODE_TOPIC,
        KEEPALIVE_ACK_TOPIC,
    ]

    client = GatewayClient(topic)
    client.on_message = on_message
    client.connect(BROKER_SERVER, PORT, KEEPALIVE)
    client.loop_forever()