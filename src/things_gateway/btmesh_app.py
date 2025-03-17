import serial
import time
import select
import struct
import asyncio
import uuid
import threading

INITIAL_STATE = 0
IDLE_STATE = 1
PROVISIONING_STATE = 2
RESTART_STATE = 3

# USB port
USB_PORT = '/dev/ttyUSB0'
USB_BAUDRATE= 9600

# opcode
OPCODE_GET_LOCAL_KEYS           = 0x01
OPCODE_UPDATE_LOCAL_KEYS        = 0x02
OPCODE_SCAN_UNPROV_DEV          = 0x03
OPCODE_PROVISIONER_DISABLE      = 0x04
OPCODE_ADD_UNPROV_DEV           = 0x05
OPCODE_SEND_ASSIGNED_DEV_INFO   = 0x06
OPCODE_DELETE_DEVICE            = 0x07
OPCODE_GET_COMPOSITION_DATA     = 0x08
OPCODE_ADD_APP_KEY              = 0x09
OPCODE_BIND_MODEL_APP           = 0x0A
OPCODE_SET_MODEL_PUB            = 0x0B
OPCODE_SET_MODEL_SUB            = 0x0C

OPCODE_SCAN_RESULT = 0x40
OPCODE_SEND_NEW_NODE_INFO = 0x41

OPCODE_TEST_SIMPLE_MSG = 0xC4

# response byte
RESPONSE_BYTE_STATUS_OK = 0x01
RESPONSE_BYTE_STATUS_FAILED = 0x02

ser = None
uuid_target = None
addr_target = None
addr_type_target = None
oob_info_target = None
bearer_target = None

net_idx_target = None
primary_unicast_target = None 

detected_device = 0
scan_status = 0
provision_pending = 0
provision_status = 0

# Ultilities
def split_bytearray(data, n):
    return [data[i:i+n] for i in range(0, len(data), n)]

def uuid_str_to_bytes(uuid):
    uuid_str = uuid[:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:]
    uuid_bytes = uuid.UUID(uuid_str).bytes
    return uuid_bytes

def mac_str_to_bytes(mac):
    mac_bytes = bytes(int(part, 16) for part in mac.split(':'))
    return mac_bytes

# Initialize UART
def setup_uart():
    try:
        ser = serial.Serial(USB_PORT, USB_BAUDRATE)
        time.sleep(1)
        print("Serial connection established")
        return ser

    except serial.SerialException as e:
        return None

def restart_uart(ser):
    if ser and ser.is_open:
        ser.close()
        print("Restart connection.")
    time.sleep(1)
    return setup_uart()

# transmit functions
def send_message_to_esp32(msg, pack_format):
    packet = struct.pack(pack_format, *msg)
    print(f'Packet: {packet}')
    ser.write(packet)
    ser.flush()

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

# def send_assigned_node_info_cmd():
#     msg = [OPCODE_SEND_ASSIGNED_DEV_INFO]
#     send_message_to_esp32(msg, '<B')

def delete_node_cmd(unicast):
    checksum = ~(OPCODE_GET_COMPOSITION_DATA 
                + sum(struct.pack('<H', unicast))) & 0xFF
    msg = [OPCODE_DELETE_DEVICE, unicast, checksum]
    send_message_to_esp32(msg, '<BHB')

def get_composition_data_cmd(unicast):
    checksum = ~(OPCODE_GET_COMPOSITION_DATA 
                + sum(struct.pack('<H', unicast))) & 0xFF
    msg = [OPCODE_GET_COMPOSITION_DATA, unicast, checksum]
    send_message_to_esp32(msg, '<BHB')

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
        # elif (opcode == OPCODE_SEND_ASSIGNED_DEV_INFO):
        #     self.recv_send_assigned_dev_info()
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
        # command from esp32
        elif (opcode == OPCODE_SCAN_RESULT):
            self.recv_scan_result()
        elif (opcode == OPCODE_SEND_NEW_NODE_INFO):
            self.recv_new_node_info()
    
    def recv_get_local_keys(self):
        msg = self.ser.read(34)
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
        msg = self.ser.read(2)
        status, checksum = struct.unpack('<BB', msg)
        
        if ((OPCODE_UPDATE_LOCAL_KEYS + sum(msg)) & 0xFF) != 0xFF:
            print('Wrong checksum')
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Update keys failed')
        else:
            print('Updated keys successfully')

    def recv_scan_unprov_dev(self):
        global scan_status
        
        msg = self.ser.read(2)
        status, checksum = struct.unpack('<BB', msg)
        check = (OPCODE_SCAN_UNPROV_DEV + sum(msg)) & 0xFF
        if check != 0xFF:
            print('Wrong checksum')
            scan_status = 0
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Cannot start scan')
            scan_status = 0
        else:
            print('Start scan')

    def recv_add_unprov_dev(self):
        msg = self.ser.read(2)
        status, checksum = struct.unpack('<BB', msg)
        if ((OPCODE_ADD_UNPROV_DEV + sum(msg)) & 0xFF) != 0xFF:
            print('Wrong checksum')
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Cannot start provisioning')
        else:
            print('Start provisioning')

    def recv_stop_scan(self):
        global scan_status
        msg = self.ser.read(2)
        status, checksum = struct.unpack('<BB', msg)
        check = (OPCODE_PROVISIONER_DISABLE + sum(msg)) & 0xFF
        if check != 0xFF:
            print('Wrong checksum')
            scan_status = 1
        elif (status == RESPONSE_BYTE_STATUS_FAILED):
            print('Cannot stop scan')
            scan_status = 1
        else:
            print('Scan stopped. Provisioner is disabled')

    def recv_send_assigned_dev_info(self):
        pass
    def recv_delete_device(self):
        pass

    def recv_get_composition_data(self):
        msg = self.ser.read(4)
        unicast, comp_data_len = struct.unpack('<HH', msg)
        print(f'Unicast: {unicast}')
        print(f'Composition data len: {comp_data_len}')
        
        comp_data_raw = ser.read(comp_data_len + 1)
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
            for sig_model in split_bytearray(modelS, 2):
                sig_models.append(list(sig_model))
            for vendor_model in split_bytearray(modelV, 4):
                vendor_models.append(list(vendor_model))
            
            element = {}
            element['location'] = loc
            element['numS'] = numS
            element['numV'] = numV
            element['sig_models'] = sig_models
            element['vendor_models'] = vendor_models
            comp_data['elements'].append(element)

            elements = rest_msg

        print('-------------Composition Data Status-------------')
        print(f'Primary unicast: {unicast}')
        print(comp_data)
        add_appkey_cmd(primary_unicast_target)

    def recv_add_app_key_status(self):
        msg = self.ser.read(4)
        unicast, status, checksum = struct.unpack('<HBB', msg)

        if ((sum(msg) + OPCODE_ADD_APP_KEY) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        print('-----------------Add Appkey Status---------------')
        print(f'Unicast address: {hex(unicast)}')
        print(f'Status code: {hex(status)}')
        model_app_bind_cmd(primary_unicast_target, 0x1000, 0xFFFF)

    def recv_bind_model_status(self):
        msg = self.ser.read(8)
        ele_addr, model_id, company_id, status, checksum = struct.unpack('<HHHBB', msg)
        if ((sum(msg) + OPCODE_BIND_MODEL_APP) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return

        print('-----------------Model App Status----------------')
        print(f'Unicast address: {hex(ele_addr)}')
        print(f'Vendor Model ID: {hex(company_id)} {hex(model_id)}')
        print(f'Status code: {hex(status)}')
        model_pub_set_cmd(primary_unicast_target, 0xC000, 0x1000, 0xFFFF)

    def recv_model_pub_status(self):
        msg = self.ser.read(10)
        ele_addr, group_addr, model_id, company_id, status, checksum = struct.unpack('<HHHHBB', msg)
        if ((sum(msg) + OPCODE_SET_MODEL_PUB) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
        
        print('-----------------Model Pub Status----------------')
        print(f'Element address: {hex(ele_addr)}')
        print(f'Group address: {hex(group_addr)}')
        print(f'Vendor Model ID: {hex(company_id)} {hex(model_id)}')
        print(f'Status code: {hex(status)}')
        model_sub_set_cmd(primary_unicast_target, 0xC000, 0x1000, 0xFFFF)

    def recv_model_sub_status(self):
        msg = self.ser.read(10)
        ele_addr, group_addr, model_id, company_id, status, checksum = struct.unpack('<HHHHBB', msg)
        if ((sum(msg) + OPCODE_SET_MODEL_SUB) & 0xFF) != 0xFF:
            print('Wrong checksum')
            return
        
        print('-----------------Model Sub Status----------------')
        print(f'Element address: {hex(ele_addr)}')
        print(f'Group address: {hex(group_addr)}')
        print(f'Vendor Model ID: {hex(company_id)} {hex(model_id)}')
        print(f'Status code: {hex(status)}')

    def recv_scan_result(self):
        global uuid_target
        global addr_target
        global addr_type_target
        global oob_info_target
        global bearer_target
        global detected_device
        
        msg = self.ser.read(29)
        uuid, addr, addr_type, oob_info, adv_type, bearer, rssi, checksum = struct.unpack('<16s6sBHBBbB', msg)
        if (detected_device == 1) or (bearer == 2):
            return

        if ((sum(msg) + OPCODE_SCAN_RESULT) & 0xFF) != 0xFF:
            print('Wrong checksum')
        else:
            detected_device = 1
            uuid_target = uuid
            addr_target = addr
            addr_type_target = adv_type
            oob_info_target = oob_info
            bearer_target = bearer

            uuid_str = uuid.hex()
            addr_str = ":".join(f"{b:02X}" for b in addr)
            address_type = 'Public address' if (addr_type == 0x01) else 'Unicast address'
            bearer_type = 'PB-ADV' if (bearer == 0x01) else 'PB-GATT'
            print('-------------------Scan result-----------------')
            print(f'UUID: {uuid_str}')
            print(f'Mac address: {addr_str}')
            print(f'Address type: {addr_type} {address_type}')
            print(f'OOB info: {oob_info}')
            print(f'ADV type: {adv_type}')
            print(f'Bearer type: {bearer} {bearer_type}')
            print(f'RSSI: {rssi}')

    def recv_new_node_info(self):
        global net_idx_target
        global primary_unicast_target
        global provision_status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  

        msg = self.ser.read(24)
        node_idx, uuid, unicast, net_idx, elem_num, checksum = struct.unpack('<H16sHHBB', msg)
        if (sum(msg) + OPCODE_SEND_NEW_NODE_INFO & 0xFF) != 0xFF:
            print('Wrong checksum')
        else:
            net_idx_target = net_idx
            primary_unicast_target = unicast
            provision_status = 1

            uuid_str = uuid.hex()
            print('-------------------New node info-----------------')
            print(f'UUID: {uuid_str}')
            print(f'Node id: {hex(node_idx)}')
            print(f'Primary unicast: {hex(unicast)}')
            print(f'NetKey id: {hex(net_idx)}')
            print(f'Element: {hex(elem_num)}')

    def recv_test_simple_msg(self):
        msg = self.ser.read(2)
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
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.method('org.ipac.btmesh', in_signature='', out_signature='')
    def BtmeshScanDevice(self):
        scan_device_cmd()

    @dbus.service.method('org.ipac.btmesh', in_signature='a{sv}', out_signature='')
    def BtmeshAddDevice(self, unprov_dev):
        uuid = uuid_str_to_bytes(unprov_dev['uuid'])
        mac = uuid_str_to_bytes(unprov_dev['mac'])
        add_device_cmd(uuid, mac, unprov_dev['addr_type'], unprov_dev['oob_info'], unprov_dev['bearer'])

    @dbus.service.method('org.ipac.btmesh', in_signature='', out_signature='')
    def BtmeshDeleteNode(self, dev_info):
        delete_node_cmd(dev_info['unicast'])
    
    # @dbus.service.method('org.ipac.btmesh', in_signature='', out_signature='')
    # def BtmeshSendAssignedNodeInfo(self, dev_info):
    #     send_assigned_node_info_cmd()

def dbus_handler():
    DBusGMainLoop(set_as_default=True)
    bus_name = dbus.service.BusName('org.ipac.Service', bus=dbus.SessionBus())
    btmesh_service = BluetoothMeshService(bus_name)
    print("BluetoothMeshService is running.")
    # Start the main loop to process incoming D-Bus messages
    GLib.MainLoop().run()

def btmesh_app():
    global scan_status
    global provision_pending
    global ser
    global provision_status
    state = INITIAL_STATE
    retry_read = 0
    ser = UART(USB_PORT, USB_BAUDRATE)
    mesh_gw = MeshGateway(ser)

    while True:
        if ser is None:
            print("Failed to establish serial connection. Retrying...")
            time.sleep(2)
            ser.setup_uart()
            continue

        if (state == INITIAL_STATE):
            # temporary
            # get_local_keys_cmd()
            state = IDLE_STATE
        elif (state == IDLE_STATE):
            if detected_device == 0 and scan_status == 0:
                scan_device_cmd()
                print('Sent scan cmd')
                scan_status = 1
            elif detected_device == 1 and provision_pending == 0:
                add_device_cmd(uuid_target, addr_target, addr_type_target, oob_info_target, bearer_target)
                # elif detected_device == 1: provision_pending = 1
                provision_pending = 1
                scan_status = 0
            
            if provision_status == 1:
                get_composition_data_cmd(primary_unicast_target)
                provision_status = 2

            # time.sleep(1)
            # Ch# elif detected_device == 1:eck for incoming data
            rlist, _, _ = select.select([ser], [], [], 0.1)  # Non-blocking check
            if rlist:
                try:
                    opcode = ser.read()
                    if (opcode.hex() != '40'):
                        print(f'Opcode: {opcode.hex()} {opcode}')
                    if (opcode is None) or (opcode == 0x00):
                        retry_read += 1
                except serial.SerialException:
                    retry_read += 1

                read_opcode(opcode)

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