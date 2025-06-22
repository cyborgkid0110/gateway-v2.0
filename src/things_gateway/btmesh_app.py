import serial
import time
import select
import struct
import asyncio
import uuid
import threading
import csv

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from src.shared import mesh_model, mesh_codes

INITIAL_STATE = 0
IDLE_STATE = 1
PROVISIONING_STATE = 2
RESTART_STATE = 3

# USB port
USB_PORT = '/dev/ttyUSB0'
USB_BAUDRATE= 19200

# opcode
OPCODE_GET_LOCAL_KEYS           = 0x01
OPCODE_UPDATE_LOCAL_KEYS        = 0x02
OPCODE_SCAN_UNPROV_DEV          = 0x03
OPCODE_PROVISIONER_DISABLE      = 0x04
OPCODE_ADD_UNPROV_DEV           = 0x05
OPCODE_DELETE_DEVICE            = 0x06
OPCODE_GET_COMPOSITION_DATA     = 0x07
OPCODE_ADD_APP_KEY              = 0x08
OPCODE_BIND_MODEL_APP           = 0x09 
OPCODE_SET_MODEL_PUB            = 0x0A
OPCODE_SET_MODEL_SUB            = 0x0B
OPCODE_RPR_SCAN_GET             = 0x0C
OPCODE_RPR_SCAN_START           = 0x0D
OPCODE_RPR_SCAN_STOP            = 0x0E
OPCODE_RPR_LINK_GET             = 0x0F
OPCODE_RPR_LINK_OPEN            = 0x10
OPCODE_RPR_LINK_CLOSE           = 0x11
OPCODE_REMOTE_PROVISIONING      = 0x12
OPCODE_RELAY_GET                = 0x13
OPCODE_RELAY_SET                = 0x14
OPCODE_PROXY_GET                = 0x15
OPCODE_PROXY_SET                = 0x16
OPCODE_FRIEND_GET               = 0x17
OPCODE_FRIEND_SET               = 0x18
OPCODE_HEARTBEAT_PUB_GET        = 0x19
OPCODE_HEARTBEAT_PUB_SET        = 0x1A

OPCODE_SCAN_RESULT              = 0x40
OPCODE_SEND_NEW_NODE_INFO       = 0x41
OPCODE_RPR_SCAN_RESULT          = 0x42
OPCODE_RPR_LINK_REPORT          = 0x43
OPCODE_HEARTBEAT_MSG            = 0x44

OPCODE_SENSOR_DATA_GET          = 0x50
OPCODE_SENSOR_DATA_STATUS       = 0x51
OPCODE_AC_CONTROL_STATE_GET     = 0x52
OPCODE_AC_CONTROL_STATE_SET     = 0x53
OPCODE_DEVICE_INFO_GET          = 0x80
OPCODE_DEVICE_INFO_STATUS       = 0x81

OPCODE_TEST_SIMPLE_MSG = 0xC4

# response byte
RESPONSE_BYTE_STATUS_OK = 0x01
RESPONSE_BYTE_STATUS_FAILED = 0x02

ser = None                      # serial COM
provision_pending = 0

remote_unprov_dev_dict = {}
# {
#     'unicast': uuid_dev,...
# }

bus = None
gw_service = None               # Gateway Service D-Bus Object
gw_service_interface = None     # Gateway Service D-Bus Interface

# Ultilities
def split_bytearray(data, n):
    return [data[i:i+n] for i in range(0, len(data), n)]

def uuid_str_to_bytes(uuid_node):
    uuid_str = uuid_node[:8] + '-' + uuid_node[8:12] + '-' + uuid_node[12:16] + '-' + uuid_node[16:20] + '-' + uuid_node[20:]
    print(uuid_str)
    uuid_bytes = uuid.UUID(uuid_str)
    return uuid_bytes.bytes

def mac_str_to_bytes(mac):
    mac_bytes = bytes(int(part, 16) for part in mac.split(':'))
    return mac_bytes

# transmit functions
def send_message_to_esp32(msg, pack_format):
    packet = struct.pack(pack_format, *msg)
    print(f'Packet: {packet}')
    ser.ser.write(packet)
    ser.ser.flush()

def get_local_keys_cmd():
    msg = [OPCODE_GET_LOCAL_KEYS]
    send_message_to_esp32(msg, '<B')

def update_local_keys_cmd(net_key, app_key):
    # net_key, app_key must be in bytes
    checksum = ~(OPCODE_UPDATE_LOCAL_KEYS + sum(net_key) + sum(app_key)) & 0xFF
    msg = [OPCODE_UPDATE_LOCAL_KEYS, net_key, app_key, checksum]
    send_message_to_esp32(msg, '<B16s16sB')

def scan_device_cmd():
    msg = [OPCODE_SCAN_UNPROV_DEV]
    send_message_to_esp32(msg ,'<B')

def stop_scan_cmd():
    msg = [OPCODE_PROVISIONER_DISABLE]
    send_message_to_esp32(msg, '<B')

def add_device_cmd(uuid, addr, addr_type, oob_info, bearer):
    checksum = ~(OPCODE_ADD_UNPROV_DEV + sum(uuid) + sum(addr) + addr_type + sum(struct.pack('<H', oob_info)) + bearer) & 0xFF

    msg = [OPCODE_ADD_UNPROV_DEV, uuid, addr, addr_type, oob_info, bearer, checksum]
    send_message_to_esp32(msg, '<B16s6sBHBB')

def delete_node_cmd(unicast):
    checksum = ~(OPCODE_DELETE_DEVICE 
                + sum(struct.pack('<H', unicast))) & 0xFF
    msg = [OPCODE_DELETE_DEVICE, unicast, checksum]
    send_message_to_esp32(msg, '<BHB')

def get_composition_data_cmd(unicast):
    checksum = ~(OPCODE_GET_COMPOSITION_DATA 
                + sum(struct.pack('<H', unicast))) & 0xFF
    msg = [OPCODE_GET_COMPOSITION_DATA, unicast, checksum]
    send_message_to_esp32(msg, '<BHB')
    print("Send cmd")

def add_appkey_cmd(unicast):
    checksum = ~(OPCODE_ADD_APP_KEY + sum(struct.pack('<H', unicast))) & 0xFF
    msg = [OPCODE_ADD_APP_KEY, unicast, checksum]
    send_message_to_esp32(msg, '<BHB')

def model_app_bind_cmd(unicast, model_id, company_id):
    checksum = ~(OPCODE_BIND_MODEL_APP 
                + sum(struct.pack('<H', unicast))
                + sum(struct.pack('<H', model_id))
                + sum(struct.pack('<H', company_id))) & 0xFF
    msg = [OPCODE_BIND_MODEL_APP, unicast, model_id, company_id, checksum]
    send_message_to_esp32(msg, '<BHHHB')

def model_pub_set_cmd(unicast, group_addr, model_id, company_id):
    checksum = ~(OPCODE_SET_MODEL_PUB 
                + sum(struct.pack('<H', unicast))
                + sum(struct.pack('<H', group_addr))
                + sum(struct.pack('<H', model_id))
                + sum(struct.pack('<H', company_id))) & 0xFF
    msg = [OPCODE_SET_MODEL_PUB, unicast, group_addr, model_id, company_id, checksum]
    send_message_to_esp32(msg, '<BHHHHB')

def model_sub_set_cmd(unicast, group_addr, model_id, company_id):
    checksum = ~(OPCODE_SET_MODEL_SUB 
                + sum(struct.pack('<H', unicast))
                + sum(struct.pack('<H', group_addr))
                + sum(struct.pack('<H', model_id))
                + sum(struct.pack('<H', company_id))) & 0xFF
    msg = [OPCODE_SET_MODEL_SUB, unicast, group_addr, model_id, company_id, checksum]
    send_message_to_esp32(msg, '<BHHHHB')

def rpr_scan_get_cmd(remote_addr):
    checksum = ~(OPCODE_RPR_SCAN_GET + sum(struct.pack('<H', remote_addr))) & 0xFF
    msg = [OPCODE_RPR_SCAN_GET, remote_addr, checksum]
    send_message_to_esp32(msg, '<BHB')

def rpr_scan_start_cmd(remote_addr):
    checksum = ~(OPCODE_RPR_SCAN_START + sum(struct.pack('<H', remote_addr))) & 0xFF
    msg = [OPCODE_RPR_SCAN_START, remote_addr, checksum]
    send_message_to_esp32(msg, '<BHB')

def rpr_scan_stop_cmd(remote_addr):
    checksum = ~(OPCODE_RPR_SCAN_STOP + sum(struct.pack('<H', remote_addr))) & 0xFF
    msg = [OPCODE_RPR_SCAN_STOP, remote_addr, checksum]
    send_message_to_esp32(msg, '<BHB')

def rpr_link_get_cmd(remote_addr, uuid_dev):
    checksum = ~(OPCODE_RPR_LINK_GET + sum(struct.pack('<H', remote_addr))) & 0xFF
    msg = [OPCODE_RPR_LINK_GET, remote_addr, checksum]
    send_message_to_esp32(msg, '<BHB')

def rpr_link_open_cmd(remote_addr):
    uuid = remote_unprov_dev_dict[remote_addr]
    checksum = ~(OPCODE_RPR_LINK_OPEN + sum(struct.pack('<H', remote_addr)) + sum(uuid)) & 0xFF
    msg = [OPCODE_RPR_LINK_OPEN, remote_addr, uuid, checksum]
    send_message_to_esp32(msg, '<BH16sB')

def rpr_link_close_cmd(remote_addr):
    reason = mesh_codes.REMOTE_PROVISIONING_LINK_CLOSE_REASON_SUCCESS
    checksum = ~(OPCODE_RPR_LINK_CLOSE + reason + sum(struct.pack('<H', remote_addr))) & 0xFF
    msg = [OPCODE_RPR_LINK_CLOSE, remote_addr, reason, checksum]
    send_message_to_esp32(msg, '<BHBB')

def remote_provisioning_cmd(remote_addr):
    checksum = ~(OPCODE_REMOTE_PROVISIONING + sum(struct.pack('<H', remote_addr))) & 0xFF
    msg = [OPCODE_REMOTE_PROVISIONING, remote_addr, checksum]
    send_message_to_esp32(msg, '<BHB')

def node_role_get_cmd(unicast, opcode):
    checksum = ~(opcode + sum(struct.pack('<H', unicast))) & 0xFF
    msg = [opcode, unicast, checksum]
    send_message_to_esp32(msg, '<BHB')

def relay_set_cmd(unicast, relay_state, relay_retransmit):
    checksum = ~(OPCODE_RELAY_SET + sum(struct.pack('<H', unicast))
                + relay_state + relay_retransmit) & 0xFF
    msg = [OPCODE_RELAY_SET, unicast, relay_state, relay_retransmit, checksum]
    send_message_to_esp32(msg, '<BHBBB')

def proxy_set_cmd(unicast, proxy_state):
    checksum = ~(OPCODE_RELAY_SET + sum(struct.pack('<H', unicast)) + proxy_state) & 0xFF
    msg = [OPCODE_RELAY_SET, unicast, proxy_state, checksum]
    send_message_to_esp32(msg, '<BHBB')

def friend_set_cmd(unicast, friend_state):
    checksum = ~(OPCODE_RELAY_SET + sum(struct.pack('<H', unicast)) + friend_state) & 0xFF
    msg = [OPCODE_RELAY_SET, unicast, friend_state, checksum]
    send_message_to_esp32(msg, '<BHBB')

def heartbeat_pub_get_cmd(unicast):
    checksum = ~(OPCODE_HEARTBEAT_PUB_GET + sum(struct.pack('<H', unicast))) & 0xFF
    msg = [OPCODE_HEARTBEAT_PUB_GET, unicast, checksum]
    send_message_to_esp32(msg, '<BHB')

def heartbeat_pub_set_cmd(unicast, dst, period, ttl):
    checksum = ~(OPCODE_HEARTBEAT_PUB_SET 
                + sum(struct.pack('<H', unicast))
                + sum(struct.pack('<H', dst))
                + period + ttl) & 0xFF
    msg = [OPCODE_HEARTBEAT_PUB_SET, unicast, dst, period, ttl, checksum]
    send_message_to_esp32(msg, '<BHHBBB')

def sensor_model_get_cmd():
    msg = [OPCODE_SENSOR_DATA_GET]
    send_message_to_esp32(msg ,'<B')

def ac_control_state_get_cmd():
    pass

def ac_control_state_set_cmd(unicast, device_id, device_state):
    checksum = ~(OPCODE_AC_CONTROL_STATE_SET + device_id
                + sum(struct.pack('<I', device_state))
                + sum(struct.pack('<H', unicast))) & 0xFF
    msg = [OPCODE_AC_CONTROL_STATE_SET, unicast, device_id, device_state, checksum]
    send_message_to_esp32(msg, '<BHBIB')

def test_simple_msg():
    msg = [OPCODE_TEST_SIMPLE_MSG]
    send_message_to_esp32(msg ,'<B')
    print('Send test message')

# recv function

class UART():
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.setup_uart()
    
    def setup_uart(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
            time.sleep(1)
            print("Serial connection established")
        except serial.SerialException as e:
            return None
    
    def restart_uart(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Restart connection.")
        time.sleep(1)
        self.setup_uart()

    def close_uart():
        self.ser.close()

class MeshGateway():
    def __init__(self, serial):
        self.opcodes = []
        self.ser = serial

    def read_opcode(self, op_byte):
        opcode = int.from_bytes(op_byte, byteorder='little') & 0xFF
        if (opcode == OPCODE_GET_LOCAL_KEYS):
            self.recv_get_local_keys()
        elif (opcode == OPCODE_UPDATE_LOCAL_KEYS):
            self.recv_update_local_keys()
        elif (opcode == OPCODE_SCAN_UNPROV_DEV):
            self.recv_scan_unprov_dev()
        elif (opcode == OPCODE_PROVISIONER_DISABLE):
            self.recv_stop_scan()
        elif (opcode == OPCODE_ADD_UNPROV_DEV):
            self.recv_add_unprov_dev()
        elif (opcode == OPCODE_DELETE_DEVICE):
            self.recv_delete_device()
        elif (opcode == OPCODE_GET_COMPOSITION_DATA):
            self.recv_get_composition_data()
        elif (opcode == OPCODE_ADD_APP_KEY):
            self.recv_add_app_key_status()
        elif (opcode == OPCODE_BIND_MODEL_APP):
            self.recv_bind_model_status()
        elif (opcode == OPCODE_SET_MODEL_PUB):
            self.recv_model_pub_status()
        elif (opcode == OPCODE_SET_MODEL_SUB):
            self.recv_model_sub_status()
        elif (opcode == OPCODE_RPR_SCAN_GET):
            self.recv_rpr_scan_get()
        elif (opcode == OPCODE_RPR_SCAN_START):
            self.recv_rpr_scan_start()
        elif (opcode == OPCODE_RPR_SCAN_STOP):
            self.recv_rpr_scan_stop()
        elif (opcode == OPCODE_RPR_LINK_GET):
            self.recv_rpr_link_get()
        elif (opcode == OPCODE_RPR_LINK_OPEN):
            self.recv_rpr_link_open()
        elif (opcode == OPCODE_RPR_LINK_CLOSE):
            self.recv_rpr_link_close()
        # elif (opcode == OPCODE_REMOTE_PROVISIONING):
        #     self.recv_remote_prov_ack()
        elif (opcode == OPCODE_RELAY_GET):
            self.recv_relay_set()
        elif (opcode == OPCODE_RELAY_SET):
            self.recv_relay_set()
        elif (opcode == OPCODE_PROXY_GET):
            self.recv_proxy_get()
        elif (opcode == OPCODE_PROXY_SET):
            self.recv_proxy_set()
        elif (opcode == OPCODE_FRIEND_GET):
            self.recv_friend_get()
        elif (opcode == OPCODE_FRIEND_SET):
            self.recv_friend_set()
        elif (opcode == OPCODE_HEARTBEAT_PUB_GET):
            self.recv_heartbeat_pub_get()
        elif (opcode == OPCODE_HEARTBEAT_PUB_SET):
            self.recv_heartbeat_pub_set()
        elif (opcode == OPCODE_HEARTBEAT_MSG):
            self.recv_heartbeat_msg()
        

        # command from esp32
        elif (opcode == OPCODE_SCAN_RESULT):
            self.recv_scan_result()
        elif (opcode == OPCODE_SEND_NEW_NODE_INFO):
            self.recv_new_node_info()

        # custom model commands
        elif (opcode == OPCODE_DEVICE_INFO_STATUS):
            self.recv_device_info_status()
        elif (opcode == OPCODE_SENSOR_DATA_STATUS):
            self.recv_sensor_data_status()
        elif (opcode == OPCODE_AC_CONTROL_STATE_SET):
            self.recv_ac_control_state_set()
    
    def recv_get_local_keys(self):
        msg = self.ser.ser.read(34)
        status, net_key, app_key, checksum = struct.unpack('<B16s16sB', msg)
        if ((OPCODE_GET_LOCAL_KEYS + sum(msg)) & 0xFF) != 0xFF:
            print('Wrong checksum')
        elif (status != RESPONSE_BYTE_STATUS_OK):
            print('Get keys failed')
        else:
            print('----------------BLE Mesh Keys----------------')
            print(f'Netkey: {net_key.hex()}')
            print(f'Appkey: {app_key.hex()}')

    def recv_update_local_keys(self):
        msg = self.ser.ser.read(2)
        status, checksum = struct.unpack('<BB', msg)
        
        if ((OPCODE_UPDATE_LOCAL_KEYS + sum(msg)) & 0xFF) != 0xFF:
            print('Wrong checksum')
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Update keys failed')
        else:
            print('Updated keys successfully')

    def recv_scan_unprov_dev(self):
        msg = self.ser.ser.read(2)
        status, checksum = struct.unpack('<BB', msg)
        check = (OPCODE_SCAN_UNPROV_DEV + sum(msg)) & 0xFF
        if check != 0xFF:
            print('Wrong checksum')
            status = RESPONSE_BYTE_STATUS_FAILED
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Cannot start scan')
        else:
            print('Start scan')

        dbus_msg = True if status == RESPONSE_BYTE_STATUS_OK else False
        if gw_service is None or gw_service_interface is None:
            dbus_call_proxy_object()
        if gw_service is not None and gw_service_interface is not None:
            gw_service_interface.BtmeshScanDeviceAck(dbus_msg)

    def recv_add_unprov_dev(self):
        msg = self.ser.ser.read(28)
        uuid, addr, addr_type, oob_info, bearer_type, status, checksum = struct.unpack('<16s6sBHBBB', msg)
        if ((OPCODE_ADD_UNPROV_DEV + sum(msg)) & 0xFF) != 0xFF:
            print('Wrong checksum')
            # status = RESPONSE_BYTE_STATUS_FAILED
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Cannot start provisioning')
        else:
            print('Start provisioning')

        uuid_str = uuid.hex()
        addr_str = ":".join(f"{b:02X}" for b in addr)

        dbus_msg = {
            'remote': False,
            'remote_addr': 0x0000,
            'uuid': uuid_str,
            'device_name': 'IPAC_LAB_SMART_FARM',
            'mac': addr_str,
            'address_type': addr_type,
            'oob_info': 0,
            'adv_type': 1,           # currently not synchronized
            'status': (1 if status == RESPONSE_BYTE_STATUS_OK else 0),
            'bearer_type': ('PB-ADV' if bearer_type == mesh_codes.PB_ADV else 'PB-GATT'),
        }

        if gw_service is None or gw_service_interface is None:
            dbus_call_proxy_object()
        if gw_service is not None and gw_service_interface is not None:
            gw_service_interface.BtmeshAddNodeAck(dbus_msg)

    def recv_stop_scan(self):
        msg = self.ser.ser.read(2)
        status, checksum = struct.unpack('<BB', msg)
        check = (OPCODE_PROVISIONER_DISABLE + sum(msg)) & 0xFF
        if check != 0xFF:
            print('Wrong checksum')
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Cannot stop scan')
        else:
            print('Scan stopped. Provisioner is disabled')

    def recv_delete_device(self):
        msg = self.ser.ser.read(4)
        unicast, status, checksum = struct.unpack('<HBB', msg)
        check = (OPCODE_DELETE_DEVICE + sum(msg)) & 0xFF
        if check != 0xFF:
            print('Wrong checksum')
            status = RESPONSE_BYTE_STATUS_FAILED
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Cannot delete node')
        else:
            print('Node deleted. Removing node in database')

        # assume there's only one delete target per time
        dbus_msg = {
            'unicast': unicast,
            'status': (0 if status == RESPONSE_BYTE_STATUS_FAILED else 1),
        }
        if gw_service is None or gw_service_interface is None:
            dbus_call_proxy_object()
        if gw_service is not None and gw_service_interface is not None:
            gw_service_interface.BtmeshDeleteNodeAck(dbus_msg)

    def recv_get_composition_data(self):
        msg = self.ser.ser.read(4)
        unicast, comp_data_len = struct.unpack('<HH', msg)
        print(f'Unicast: {unicast}')
        print(f'Composition data len: {comp_data_len}')
        
        comp_data_raw = ser.ser.read(comp_data_len + 1)
        print()
        if ((sum(msg) + sum(comp_data_raw) + OPCODE_GET_COMPOSITION_DATA) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
        
        size = comp_data_len - 10

        comp_data = {}
        comp_data['feature'] = {}
        comp_data['elements'] = []
        cid, pid, vid, crpl, feature, elements, checksum = struct.unpack(f'<HHHHH{size}sB', comp_data_raw)
        comp_data['cid'] = cid
        comp_data['pid'] = pid
        comp_data['vid'] = vid
        comp_data['crpl'] = crpl
        comp_data['feature']['relay'] = feature & (0x01)
        comp_data['feature']['proxy'] = feature & (0x02)
        comp_data['feature']['friend'] = feature & (0x04)
        comp_data['feature']['low_power'] = feature & (0x08)

        while size > 0:
            size -= 4
            loc, numS, numV, models = struct.unpack(f'<HBB{size}s', elements)
            size -= (2*numS + 4*numV)
            modelS, modelV, rest_msg = struct.unpack(f'<{2*numS}s{4*numV}s{size}s', models)
            
            sig_models = []
            vendor_models = []
            # print(split_bytearray(modelS, 2))
            for sig_model in split_bytearray(modelS, 2):
                sig_model_hex = struct.unpack("<H", sig_model)
                sig_models.append(sig_model_hex[0])
            for vendor_model in split_bytearray(modelV, 4):
                vendor_model_hex = struct.unpack("<HH", vendor_model)
                vendor_models.append(list(vendor_model_hex))
            
            element = {}
            element['location'] = loc
            element['numS'] = numS
            element['numV'] = numV
            element['sig_models'] = mesh_model.read_sig_models(sig_models)
            element['vendor_models'] = mesh_model.read_vendor_models(vendor_models)
            comp_data['elements'].append(element)

            elements = rest_msg

        print('-------------Composition Data Status-------------')
        print(f'Primary unicast: {unicast}')
        print(comp_data)
        # add_appkey_cmd(unicast)

        for sig_model in comp_data['elements'][0]['sig_models']:
            if (sig_model[0] == mesh_model.CONFIGURATION_CLIENT_MODEL) or (sig_model[0] == mesh_model.CONFIGURATION_SERVER_MODEL):
                continue

            if (sig_model[0] == mesh_model.REMOTE_PROVISIONING_SERVER_MODEL):
                # enable Remote Provisioner Field
                pass
            
            model_app_bind_cmd(unicast, sig_model[0], 0xFFFF)
            time.sleep(0.05)

        print(comp_data['elements'][0]['vendor_models'])        
        for model in comp_data['elements'][0]['vendor_models']:
            print(model)
            model_app_bind_cmd(unicast, model[0][1], model[0][0])

    def recv_add_app_key_status(self):
        msg = self.ser.ser.read(4)
        unicast, status, checksum = struct.unpack('<HBB', msg)

        if ((sum(msg) + OPCODE_ADD_APP_KEY) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        print('-----------------Add Appkey Status---------------')
        print(f'Unicast address: {hex(unicast)}')
        print(f'Status code: {hex(status)}')
        get_composition_data_cmd(unicast)

    def recv_bind_model_status(self):
        msg = self.ser.ser.read(8)
        ele_addr, model_id, company_id, status, checksum = struct.unpack('<HHHBB', msg)
        if ((sum(msg) + OPCODE_BIND_MODEL_APP) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        print('-----------------Model App Status----------------')
        print(f'Unicast address: {hex(ele_addr)}')
        print(f'Vendor Model ID: {hex(company_id)} {hex(model_id)}')
        print(f'Status code: {hex(status)}')
        if model_id % 2 == 0:   # Server
            model_sub_set_cmd(ele_addr, 0xC000, model_id + 1, company_id)
        else:                   # Client
            model_sub_set_cmd(ele_addr, 0xC000, model_id - 1, company_id)

    def recv_model_pub_status(self):
        msg = self.ser.ser.read(10)
        ele_addr, group_addr, model_id, company_id, status, checksum = struct.unpack('<HHHHBB', msg)
        if ((sum(msg) + OPCODE_SET_MODEL_PUB) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
        
        print('-----------------Model Pub Status----------------')
        print(f'Element address: {hex(ele_addr)}')
        print(f'Group address: {hex(group_addr)}')
        print(f'Vendor Model ID: {hex(company_id)} {hex(model_id)}')
        print(f'Status code: {hex(status)}')

        print('------------Node Configuration Status------------')
        print(f'Node {ele_addr} configured successfully')

    def recv_model_sub_status(self):
        msg = self.ser.ser.read(10)
        ele_addr, group_addr, model_id, company_id, status, checksum = struct.unpack('<HHHHBB', msg)
        if ((sum(msg) + OPCODE_SET_MODEL_SUB) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
        
        print('-----------------Model Sub Status----------------')
        print(f'Element address: {hex(ele_addr)}')
        print(f'Group address: {hex(group_addr)}')
        print(f'Vendor Model ID: {hex(company_id)} {hex(model_id)}')
        print(f'Status code: {hex(status)}')
        if model_id % 2 == 0:   # Server
            model_pub_set_cmd(ele_addr, 0xC000, model_id + 1, company_id)
        else:                   # Client
            model_pub_set_cmd(ele_addr, 0xC000, model_id - 1, company_id)

    def recv_rpr_scan_get(self):
        msg = self.ser.ser.read(7)
        unicast, status, rpr_scanning, scan_items_limit, timeout, checksum = struct.unpack("<HBBBBB", msg)
        if ((sum(msg) + OPCODE_RPR_SCAN_GET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
    
    def recv_rpr_scan_start(self):
        msg = self.ser.ser.read(7)
        unicast, status, rpr_scanning, scan_items_limit, timeout, checksum = struct.unpack("<HBBBBB", msg)
        if ((sum(msg) + OPCODE_RPR_SCAN_START) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
        
        # assume only feedback scan status with error only
        if status != mesh_codes.REMOTE_PROVISIONER_STATUS_SUCCESS:
            scan_status = False
            if gw_service is None or gw_service_interface is None:
                dbus_call_proxy_object()
            if gw_service is not None and gw_service_interface is not None:
                gw_service_interface.BtmeshRemoteScanDeviceAck(scan_status, unicast)
        
        print('---------------Remote Scan Status----------------')
        print(f'Node {unicast} start remote scan with status {status}')

    def recv_rpr_scan_stop(self):
        msg = self.ser.ser.read(7)
        unicast, status, rpr_scanning, scan_items_limit, timeout, checksum = struct.unpack("<HBBBBB", msg)
        if ((sum(msg) + OPCODE_RPR_SCAN_STOP) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

    def recv_rpr_link_get(self):
        msg = self.ser.ser.read(5)
        remote_addr, status, rpr_state, checksum = struct.unpack("<HBBB", msg)
        if ((sum(msg) + OPCODE_RPR_LINK_GET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
        
        if status == mesh_codes.REMOTE_PROVISIONER_STATUS_SUCCESS and rpr_state == mesh_codes.REMOTE_PROVISIONING_LINK_STATE_IDLE:
            rpr_link_open_cmd(remote_addr)
        else:
            dbus_msg = {
                'remote': True,
                'remote_addr': remote_addr,
                'uuid': remote_unprov_dev_dict[remote_addr]['uuid'],
                'device_name': remote_unprov_dev_dict[remote_addr]['device_name'],
                'mac': remote_unprov_dev_dict[remote_addr]['mac'],
                'address_type': remote_unprov_dev_dict[remote_addr]['address_type'],
                'oob_info': remote_unprov_dev_dict[remote_addr]['oob_info'],
                'adv_type': remote_unprov_dev_dict[remote_addr]['adv_type'],
                'status': 0,
                'bearer_type': remote_unprov_dev_dict[remote_addr]['bearer_type'],
            }

            if gw_service is None or gw_service_interface is None:
                dbus_call_proxy_object()
            if gw_service is not None and gw_service_interface is not None:
                gw_service_interface.BtmeshAddNodeAck(dbus_msg)
        
        print('-------------Remote Link Get Status--------------')
        print(f'Remote address: {remote_addr}')
        print(f'Status: {status}')
        print(f'Remote Provisioning Link state value: {rpr_state}')

    def recv_rpr_link_open(self):
        msg = self.ser.ser.read(5)
        remote_addr, status, rpr_state, checksum = struct.unpack("<HBBB", msg)
        if ((sum(msg) + OPCODE_RPR_LINK_OPEN) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        if status != mesh_codes.REMOTE_PROVISIONER_STATUS_SUCCESS or rpr_state != mesh_codes.REMOTE_PROVISIONING_LINK_STATE_LINK_OPENING:
            dbus_msg = {
                'remote': True,
                'remote_addr': remote_addr,
                'uuid': remote_unprov_dev_dict[remote_addr]['uuid'],
                'device_name': remote_unprov_dev_dict[remote_addr]['device_name'],
                'mac': remote_unprov_dev_dict[remote_addr]['mac'],
                'address_type': remote_unprov_dev_dict[remote_addr]['address_type'],
                'oob_info': remote_unprov_dev_dict[remote_addr]['oob_info'],
                'adv_type': remote_unprov_dev_dict[remote_addr]['adv_type'],
                'status': 0,
                'bearer_type': remote_unprov_dev_dict[remote_addr]['bearer_type'],
            }

            if gw_service is None or gw_service_interface is None:
                dbus_call_proxy_object()
            if gw_service is not None and gw_service_interface is not None:
                gw_service_interface.BtmeshAddNodeAck(dbus_msg)
        
        print('-------------Remote Link Open Status-------------')
        print(f'Remote address: {remote_addr}')
        print(f'Status: {status}')
        print(f'Remote Provisioning Link state value: {rpr_state}')

    def recv_rpr_link_close(self):
        msg = self.ser.ser.read(5)
        remote_addr, status, rpr_state, checksum = struct.unpack("<HBBB", msg)
        if ((sum(msg) + OPCODE_RPR_LINK_CLOSE) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        if status != mesh_codes.REMOTE_PROVISIONER_STATUS_SUCCESS or rpr_state != mesh_codes.REMOTE_PROVISIONING_LINK_STATE_LINK_CLOSING:
            dbus_msg = {
                'remote': True,
                'remote_addr': remote_addr,
                'uuid': remote_unprov_dev_dict[remote_addr]['uuid'],
                'device_name': remote_unprov_dev_dict[remote_addr]['device_name'],
                'mac': remote_unprov_dev_dict[remote_addr]['mac'],
                'address_type': remote_unprov_dev_dict[remote_addr]['address_type'],
                'oob_info': remote_unprov_dev_dict[remote_addr]['oob_info'],
                'adv_type': remote_unprov_dev_dict[remote_addr]['adv_type'],
                'status': 0,
                'bearer_type': remote_unprov_dev_dict[remote_addr]['bearer_type'],
            }

            if gw_service is None or gw_service_interface is None:
                dbus_call_proxy_object()
            if gw_service is not None and gw_service_interface is not None:
                gw_service_interface.BtmeshAddNodeAck(dbus_msg)
        
        print('-------------Remote Link Open Status-------------')
        print(f'Remote address: {remote_addr}')
        print(f'Status: {status}')
        print(f'Remote Provisioning Link state value: {rpr_state}')

    def recv_rpr_link_report(self):
        msg = self.ser.ser.read(7)
        unicast, status, rpr_state, reason_en, reason, checksum = struct.unpack("<HBBBBB", msg)
        if ((sum(msg) + OPCODE_RPR_LINK_REPORT) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        if status == mesh_codes.REMOTE_PROVISIONER_STATUS_SUCCESS and rpr_state == mesh_codes.REMOTE_PROVISIONING_LINK_STATE_LINK_ACTIVE:
            remote_provisioning_cmd(unicast)

    def recv_remote_prov_ack():
        msg = self.ser.ser.read(3)
        status, remote_addr, checksum = struct.unpack("<BHB", msg)
        if ((sum(msg) + OPCODE_REMOTE_PROVISIONING) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        if status == RESPONSE_BYTE_STATUS_FAILED:
            print(f"Start remote provisioning at node {remote_addr} failed")
        else:
            print(f"Start remote provisioning at node {remote_addr}")

        dbus_msg = {
            'remote': True,
            'remote_addr': remote_addr,
            'uuid': remote_unprov_dev_dict[remote_addr]['uuid'],
            'device_name': remote_unprov_dev_dict[remote_addr]['device_name'],
            'mac': remote_unprov_dev_dict[remote_addr]['mac'],
            'address_type': remote_unprov_dev_dict[remote_addr]['address_type'],
            'oob_info': remote_unprov_dev_dict[remote_addr]['oob_info'],
            'adv_type': remote_unprov_dev_dict[remote_addr]['adv_type'],
            'status': 1,
            'bearer_type': remote_unprov_dev_dict[remote_addr]['bearer_type'],
        }

        if gw_service is None or gw_service_interface is None:
            dbus_call_proxy_object()
        if gw_service is not None and gw_service_interface is not None:
            gw_service_interface.BtmeshAddNodeAck(dbus_msg)

    def recv_relay_get(self):
        msg = self.ser.ser.read(5)
        unicast, relay_state, relay_retransmit, checksum = struct.unpack("<HBBB", msg)
        if ((sum(msg) + OPCODE_RELAY_GET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

    def recv_relay_set(self):
        msg = self.ser.ser.read(5)
        unicast, relay_state, relay_retransmit, checksum = struct.unpack("<HBBB", msg)
        if ((sum(msg) + OPCODE_RELAY_SET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        print('----------------Relay set result---------------')
        print(f'Unicast: {unicast}')
        print(f'Relay state: {relay_state}')
        print(f'Relay retransmit: {relay_retransmit}')

    def recv_friend_get(self):
        msg = self.ser.ser.read(4)
        unicast, friend_state, checksum = struct.unpack("<HBB", msg)
        if ((sum(msg) + OPCODE_FRIEND_GET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
    
    def recv_friend_set(self):
        msg = self.ser.ser.read(4)
        unicast, friend_state, checksum = struct.unpack("<HBB", msg)
        if ((sum(msg) + OPCODE_FRIEND_SET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

    def recv_proxy_get(self):
        msg = self.ser.ser.read(4)
        unicast, proxy_state, checksum = struct.unpack("<HBB", msg)
        if ((sum(msg) + OPCODE_PROXY_GET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

    def recv_proxy_set(self):
        msg = self.ser.ser.read(4)
        unicast, proxy_state, checksum = struct.unpack("<HBB", msg)
        if ((sum(msg) + OPCODE_PROXY_SET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

    def recv_heartbeat_pub_get(self):
        msg = self.ser.ser.read(7)
        unicast, dst, period, ttl, checksum = struct.unpack("<HHBBB", msg)
        if ((sum(msg) + OPCODE_HEARTBEAT_PUB_GET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

    def recv_heartbeat_pub_set(self):
        msg = self.ser.ser.read(7)
        unicast, dst, period, ttl, checksum = struct.unpack("<HHBBB", msg)
        if ((sum(msg) + OPCODE_HEARTBEAT_PUB_SET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

    def recv_heartbeat_msg(self):
        msg = self.ser.ser.read(4)
        feature, hops, checksum = struct.unpack("<HBB", msg)
        if ((sum(msg) + OPCODE_HEARTBEAT_MSG) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

    def recv_scan_result(self):
        msg = self.ser.ser.read(49)
        device_name, uuid, addr, addr_type, oob_info, adv_type, bearer, rssi, checksum = struct.unpack('<20s16s6sBHBBbB', msg)
        if (bearer == 2):           # (optional) we don't accept 'PB-GATT' 
            return

        if ((sum(msg) + OPCODE_SCAN_RESULT) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
            
        uuid_str = uuid.hex()
        device_name_str = device_name.decode('utf-8')
        addr_str = ":".join(f"{b:02X}" for b in addr)
        address_type = 'Public address' if (addr_type == 0x00) else 'Random address'
        bearer_type = 'PB-ADV' if (bearer == mesh_codes.PB_ADV) else 'PB-GATT'
        print('-------------------Scan result-----------------')
        print(f'Device name: {device_name_str}')
        print(f'UUID: {uuid_str}')
        print(f'Mac address: {addr_str}')
        print(f'Address type: {addr_type} {address_type}')
        print(f'OOB info: {oob_info}')
        print(f'ADV type: {adv_type}')
        print(f'Bearer type: {bearer} {bearer_type}')
        print(f'RSSI: {rssi}')

        dbus_msg = {
            'remote': False,
            'remote_addr': 0x0000,
            'uuid': uuid_str,
            'mac': addr_str, 
            'device_name': device_name_str.rstrip('\x00'),      # this name should be assigned from device
            'address_type': addr_type,
            'oob_info': oob_info,
            'adv_type': adv_type,
            'bearer_type': bearer_type,
            'rssi': rssi,
        }
        if gw_service is None or gw_service_interface is None:
            dbus_call_proxy_object()
        if gw_service is not None and gw_service_interface is not None:
            gw_service_interface.BtmeshScanResult(dbus_msg)

    def recv_new_node_info(self):
        msg = self.ser.ser.read(25)
        remote, uuid, unicast, rpr_srv_addr, net_idx, elem_num, checksum = struct.unpack('<B16sHHHBB', msg)
        if (sum(msg) + OPCODE_SEND_NEW_NODE_INFO & 0xFF) != 0xFF:
            print('Wrong checksum here')
        else:
            uuid_str = uuid.hex()
            print('-------------------New node info-----------------')
            print(f'UUID: {uuid_str}')
            print(f'Primary unicast: {hex(unicast)}')
            print(f'NetKey id: {hex(net_idx)}')
            print(f'Element: {hex(elem_num)}')

            add_appkey_cmd(unicast)                         # configuration node start here
            dbus_msg = {
                'function': 'sensor',                      # get function from device
                'uuid': uuid_str,
                'device_name': 'IPAC_LAB_SMART_FARM',     # this name should be assigned from device
                'unicast': unicast,
            }
            if gw_service is None or gw_service_interface is None:
                dbus_call_proxy_object()
            if gw_service is not None and gw_service_interface is not None:
                gw_service_interface.BtmeshNewNodeInfo(dbus_msg)

    def recv_rpr_scan_report(self):
        msg = self.ser.ser.read(30)
        unicast, rssi, uuid, oob_info, uri_hash, checksum = struct.unpack('<Hb16sHIB', msg)
        if (sum(msg) + OPCODE_RPR_SCAN_RESULT & 0xFF) != 0xFF:
            print('Wrong checksum here')
            return

        uuid_str = uuid.hex()
        print('-------------------Scan result-----------------')
        print(f'Device name: {device_name_str}')
        print(f'UUID: {uuid_str}')
        print(f'Mac address: {addr_str}')
        print(f'Address type: {addr_type} {address_type}')
        print(f'OOB info: {oob_info}')
        print(f'RSSI: {rssi}')

        dbus_msg = {
            'remote': False,
            'remote_addr': 0x0000,
            'uuid': uuid_str,
            'mac': addr_str, 
            'device_name': "IPAC_LAB_SMART_FARM",      # this name should be assigned from device
            'address_type': addr_type,
            'oob_info': oob_info,
            'adv_type': adv_type,
            'bearer_type': bearer_type,
            'rssi': rssi,
        }
        if gw_service is None or gw_service_interface is None:
            dbus_call_proxy_object()
        if gw_service is not None and gw_service_interface is not None:
            gw_service_interface.BtmeshScanResult(dbus_msg)

    def recv_sensor_data_status(self):        # publish message
        print("Received")
        msg = self.ser.ser.read(23)
        id, unicast, temp, humid, light, co2, motion, dust, battery, checksum = struct.unpack('<HHffHHBfBB', msg)
        if (sum(msg) + OPCODE_SENSOR_DATA_STATUS & 0xFF) != 0xFF:
            print('Wrong checksum')
        else:
            dbus_msg = {
                'protocol': 'ble_mesh',
                'unicast': unicast,
                'battery': battery,
                # 'data': {
                #     'pid': id,
                #     'temp': temp, 
                #     'hum': humid,      # this name should be assigned from device
                #     'light': light,
                #     'co2': co2,
                #     'motion': motion,
                #     'dust': dust,
                # }
                'pid': id,
                'temp': temp, 
                'hum': humid,
                'light': light,
                'co2': co2,
                'motion': motion,
                'dust': dust,
            }
            print(dbus_msg)
            
            # csv_filename = 'btmesh_sensor.csv'
            # csv_headers = ['unicast', 'pid', 'temp', 'hum', 'light', 'co2', 'motion', 'dust']
            # with open(csv_filename, 'a', newline='') as csvfile:
            #     writer = csv.writer(csvfile)
            #     row = [unicast, id, temp, humid, light, co2, motion, dust]
            #     writer.writerow(row)
            if gw_service is None or gw_service_interface is None:
               dbus_call_proxy_object()
            if gw_service is not None and gw_service_interface is not None:
               gw_service_interface.SaveSensorDataToThingsboard(dbus_msg)
            #    return

    def recv_device_info_status(self):
        msg = self.ser.ser.read(25)
        unicast, device_name, function, tx_power, checksum = struct.unpack('<H20sBbB', msg)
        if (sum(msg) + OPCODE_DEVICE_INFO_STATUS & 0xFF) != 0xFF:
            print('Wrong checksum')
        else:
            dbus_msg = {
                'protocol': 'ble_mesh',
                'dev_info': {
                    'unicast': unicast,
                    'device_name': str(device_name, "utf-8"), 
                    'function': function,      
                    'tx_power': tx_power,
                }
            }
            # if gw_service is None or gw_service_interface is None:
            #     dbus_call_proxy_object()
            # if gw_service is not None and gw_service_interface is not None:
            #     gw_service_interface.SaveSensorData(dbus_msg)

    def recv_ac_control_state_get(self):
        pass

    def recv_ac_control_state_set(self):
        msg = self.ser.ser.read(9)
        unicast, device_id, device_state, status, checksum = struct.unpack('<HBIBB', msg)
        print(f'Received: {msg}')
        if ((sum(msg) + OPCODE_AC_CONTROL_STATE_SET) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        print('------------Universal IR Controller------------')
        print(f'Device ID: {device_id}')
        print(f'Device state: {device_state}')
        print(f'Controller status: {status}')

    def recv_test_simple_msg(self):
        msg = self.ser.ser.read(2)
        status, checksum = struct.unpack('<BB', msg)
        print(f'Received: {msg}')
        if ((status + OPCODE_TEST_SIMPLE_MSG + checksum) & 0xFF) != 0xFF:
            print('Wrong checksum')
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Status byte is RESPONSE_BYTE_STATUS_FAILED')
        else: 
            print('Status byte is RESPONSE_BYTE_STATUS_OK')

class BluetoothMeshService(dbus.service.Object):
    def __init__(self, bus_name, object_path='/org/ipac/btmesh'):
        bus_name = dbus.service.BusName('org.ipac.btmesh', bus=bus)
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.method('org.ipac.btmesh', in_signature='', out_signature='')
    def BtmeshScanDevice(self):
        scan_device_cmd()

    @dbus.service.method('org.ipac.btmesh', in_signature='aq', out_signature='')
    def BtmeshRemoteScanStartAll(self, unicast_list):
        for unicast in unicast_list:
            rpr_scan_start_cmd(unicast)

    @dbus.service.method('org.ipac.btmesh', in_signature='a{sv}', out_signature='')
    def BtmeshAddDevice(self, unprov_dev):
        if provision_pending == True:
            dbus_msg = {
                'remote': False,
                'remote_addr': 0x0000,
                'uuid': unprov_dev['uuid'],
                'device_name': unprov_dev['device_name'],
                'mac': unprov_dev['mac'],
                'address_type': unprov_dev['address_type'],
                'oob_info': unprov_dev['oob_info'],
                'adv_type': unprov_dev['adv_type'],           # currently not synchronized
                'status': 0,
                'bearer_type': unprov_dev['bearer_type'],
            }
            if gw_service is None or gw_service_interface is None:
                dbus_call_proxy_object()
            if gw_service is not None and gw_service_interface is not None:
                gw_service_interface.BtmeshAddNodeAck(dbus_msg)
        else:
            uuid = uuid_str_to_bytes(str(unprov_dev['uuid']))
            mac = mac_str_to_bytes(str(unprov_dev['mac']))
            bearer = mesh_codes.PB_ADV if (unprov_dev['bearer_type'] == 'PB-ADV') else mesh_codes.PB_GATT
            add_device_cmd(uuid, mac, int(unprov_dev['address_type']), int(unprov_dev['oob_info']), bearer)

    @dbus.service.method('org.ipac.btmesh', in_signature='qa{sv}', out_signature='')
    def BtmeshRemoteAddDevice(self, remote_addr, unprov_dev):
        unicasts = list(remote_unprov_dev_dict.keys())
        if remote_addr in unicasts:
            dbus_msg = {
                'remote': True,
                'remote_addr': remote_addr,
                'uuid': unprov_dev['uuid'],
                'device_name': unprov_dev['device_name'],
                'mac': unprov_dev['mac'],
                'address_type': unprov_dev['address_type'],
                'oob_info': unprov_dev['oob_info'],
                'adv_type': unprov_dev['adv_type'],
                'status': 0,
                'bearer_type': unprov_dev['bearer_type'],
            }

            if gw_service is None or gw_service_interface is None:
                dbus_call_proxy_object()
            if gw_service is not None and gw_service_interface is not None:
                gw_service_interface.BtmeshAddNodeAck(dbus_msg)
        else:
            remote_unprov_dev_dict[remote_addr] = {
                'uuid': unprov_dev['uuid'],
                'device_name': unprov_dev['device_name'],
                'mac': unprov_dev['mac'],
                'address_type': unprov_dev['address_type'],
                'oob_info': unprov_dev['oob_info'],
                'adv_type': unprov_dev['adv_type'],
                'bearer_type': unprov_dev['bearer_type'],
            }
            uuid_dev = uuid_str_to_bytes(str(unprov_dev['uuid']))
            rpr_link_get_cmd(remote_addr, uuid_dev)

    @dbus.service.method('org.ipac.btmesh', in_signature='a{sv}', out_signature='')
    def BtmeshDeleteNode(self, dev_info):
        delete_node_cmd(dev_info['unicast'])

    @dbus.service.method('org.ipac.btmesh', in_signature='a{sv}', out_signature='')
    def BtmeshRelaySet(self, config):
        relay_retransmit = 0x00
        relay_set_cmd(config['unicast'], config['relay_state'], relay_retransmit)

    @dbus.service.method('org.ipac.btmesh', in_signature='a{sa{sv}}', out_signature='')
    def BtmeshUniversalIRController(self, actuator_target):
        # actuator_target = {
        #     'actuator_info': {
        #         'unicast',
        #         'function',
        #     },
        #     'control_state': {
        #         'setpoint':
        #         'mode',
        #         'start_time',
        #         'end_time',
        #         'status',
        #     }
        # }
        device_id = 3                           # currently fixed for test
        if actuator_target['actuator_info']['function'] == 'Air':
            if (isinstance(actuator_target['control_state']['setpoint'], int) == False or 
                actuator_target['control_state']['setpoint'] > mesh_codes.AIRCON_MAX_TEMP or
                actuator_target['control_state']['setpoint'] < mesh_codes.AIRCON_MIN_TEMP):
                print('Invalid setpoint')
                return

            device_state = (actuator_target['control_state']['setpoint']
                            - mesh_codes.AIRCON_MIN_TEMP
                            + mesh_codes.IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_17)
            
            print('Send actuator control')
            ac_control_state_set_cmd(actuator_target['actuator_info']['unicast'],
                                     device_id, device_state)
            # with more properties, convert to state and send control for each property

def dbus_call_proxy_object():
    global gw_service
    global gw_service_interface
    
    try:
        gw_service = bus.get_object('org.ipac.gateway', '/org/ipac/gateway')
        gw_service_interface = dbus.Interface(gw_service, 'org.ipac.gateway')
    except dbus.exceptions.DBusException:
        print('Cannot connect to GatewayService')

def dbus_handler():
    DBusGMainLoop(set_as_default=True)
    global bus

    bus = dbus.SystemBus()
    bus_name = dbus.service.BusName('org.ipac.btmesh', bus=bus)
    btmesh_service = BluetoothMeshService(bus_name)
    print("BluetoothMeshService is running.")
    # Start the main loop to process incoming D-Bus messages
    GLib.MainLoop().run()

def btmesh_app():
    global ser
    state = INITIAL_STATE
    retry_read = 0
    ser = UART(USB_PORT, USB_BAUDRATE)
    mesh_gw = MeshGateway(ser)

    while True:
        if ser is None:
            print("Failed to establish serial connection. Retrying...")
            time.sleep(3)
            ser.setup_uart()
            continue

        if (state == INITIAL_STATE):
            # temporary
            # get_local_keys_cmd()
            state = IDLE_STATE
        elif (state == IDLE_STATE):
            # time.sleep(1)
            # Check for incoming data
            rlist, _, _ = select.select([ser.ser], [], [], 0.1)  # Non-blocking check
            if rlist:
                try:
                    opcode = ser.ser.read()
                    if (opcode.hex() != '40'):
                        print(f'Opcode: {opcode.hex()} {opcode}')
                    if (opcode is None) or (opcode == 0x00):
                        retry_read += 1
                    else:
                        mesh_gw.read_opcode(opcode)
                except serial.SerialException:
                    retry_read += 1
            # else:
            #     print('No response')

            if (retry_read > 5):
                state = RESTART_STATE

        elif (state == RESTART_STATE):
            retry_read = 0
            ser.restart_uart()

        time.sleep(0.1)

    # Close the serial connection on exit
    ser.close_uart()

def main():
    app_thread = threading.Thread(target=btmesh_app)
    dbus_handler_thread = threading.Thread(target=dbus_handler)

    app_thread.start()
    dbus_handler_thread.start()

if __name__ == '__main__':
    main()
