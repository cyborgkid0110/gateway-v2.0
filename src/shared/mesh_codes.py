# Provisioner Bearer Type Codes
PB_ADV    = 0x01
PB_GATT   = 0x02
PB_BEARER = 0x04

# Relay State
RELAY_DISABLE       = 0x00
RELAY_ENABLE        = 0x01
RELAY_NOT_SUPPORTED = 0x02

# Remote Provisioning Server Status Codes
REMOTE_PROVISIONER_STATUS_SUCCESS                                   = 0x00
REMOTE_PROVISIONER_STATUS_SCANNING_CANNOT_START                     = 0x01
REMOTE_PROVISIONER_STATUS_INVALID_STATE                             = 0x02
REMOTE_PROVISIONER_STATUS_LIMITED_RESOURCES                         = 0x03
REMOTE_PROVISIONER_STATUS_LINK_CANNOT_OPEN                          = 0x04
REMOTE_PROVISIONER_STATUS_LINK_OPEN_FAILED                          = 0x05
REMOTE_PROVISIONER_STATUS_LINK_CLOSED_BY_DEVICE                     = 0x06
REMOTE_PROVISIONER_STATUS_LINK_CLOSED_BY_SERVER                     = 0x07
REMOTE_PROVISIONER_STATUS_LINK_CLOSED_BY_CLIENT                     = 0x08
REMOTE_PROVISIONER_STATUS_LINK_CLOSED_AS_CANNOT_RECEIVE_PDU         = 0x09
REMOTE_PROVISIONER_STATUS_LINK_CLOSED_AS_CANNOT_SEND_PDU            = 0x0A
REMOTE_PROVISIONER_STATUS_LINK_CLOSED_AS_CANNOT_DELIVER_PDU_REPORT  = 0x0B

# Remote Provisioning Link Close Reason Field Values
REMOTE_PROVISIONING_LINK_CLOSE_REASON_SUCCESS           = 0x00
REMOTE_PROVISIONING_LINK_CLOSE_REASON_PROHIBITED        = 0x01
REMOTE_PROVISIONING_LINK_CLOSE_REASON_FAIL              = 0x02

# Remote Provisioning Link State Values
REMOTE_PROVISIONING_LINK_STATE_IDLE                     = 0x00
REMOTE_PROVISIONING_LINK_STATE_LINK_OPENING             = 0x01
REMOTE_PROVISIONING_LINK_STATE_LINK_ACTIVE              = 0x02
REMOTE_PROVISIONING_LINK_STATE_OUTBOUND_PACKET_TRANSFER = 0x03
REMOTE_PROVISIONING_LINK_STATE_LINK_CLOSING             = 0x04

# Air Conditioner Setpoint Threshold
AIRCON_MIN_TEMP = 17
AIRCON_MAX_TEMP = 30

# Actuator State of Universal IR Controller
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_ON                   = 0x00
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_OFF                  = 0x01
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_17              = 0x02
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_18              = 0x03
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_19              = 0x04
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_20              = 0x05
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_21              = 0x06
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_22              = 0x07
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_23              = 0x08
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_24              = 0x09
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_25              = 0x0A
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_26              = 0x0B
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_27              = 0x0C
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_28              = 0x0D
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_29              = 0x0E
IPAC_UNIVERSAL_IR_CONTROLLER_STATE_TEMP_30              = 0x0F

# Universal IR Controller status
IPAC_UNIVERSAL_IR_CONTROLLER_NO_DATA                    = 0x00
IPAC_UNIVERSAL_IR_CONTROLLER_OK                         = 0x01
IPAC_UNIVERSAL_IR_CONTROLLER_USER_INTERACT_OK           = 0x02
IPAC_UNIVERSAL_IR_CONTROLLER_USER_INTERACT_OFF          = 0x03