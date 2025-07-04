# Bluetooth Mesh SIG Model Identifiers
# Based on the provided table from the Bluetooth SIG Assigned Numbers document
# Values are 16-bit identifiers as defined by the Bluetooth SIG

# Company ID
COMPANY_ID = 0x02E5

# Foundation Models
CONFIGURATION_SERVER_MODEL = 0x0000
CONFIGURATION_CLIENT_MODEL = 0x0001
HEALTH_SERVER_MODEL = 0x0002
HEALTH_CLIENT_MODEL = 0x0003
REMOTE_PROVISIONING_SERVER_MODEL = 0x0004
REMOTE_PROVISIONING_CLIENT_MODEL = 0x0005
DIRECTED_FORWARDING_CONFIGURATION_SERVER_MODEL = 0x0006
DIRECTED_FORWARDING_CONFIGURATION_CLIENT_MODEL = 0x0007
BRIDGE_CONFIGURATION_SERVER_MODEL = 0x0008
BRIDGE_CONFIGURATION_CLIENT_MODEL = 0x0009
MESH_PRIVATE_BEACON_SERVER_MODEL = 0x000A
MESH_PRIVATE_BEACON_CLIENT_MODEL = 0x000B
ON_DEMAND_PRIVATE_PROXY_SERVER_MODEL = 0x000C
ON_DEMAND_PRIVATE_PROXY_CLIENT_MODEL = 0x000D
SAR_CONFIGURATION_SERVER_MODEL = 0x000E
SAR_CONFIGURATION_CLIENT_MODEL = 0x000F
OPCODES_AGGREGATOR_SERVER_MODEL = 0x0010
OPCODES_AGGREGATOR_CLIENT_MODEL = 0x0011
LARGE_COMPOSITION_DATA_SERVER_MODEL = 0x0012
LARGE_COMPOSITION_DATA_CLIENT_MODEL = 0x0013
SOLICITATION_PDU_RPL_CONFIGURATION_SERVER_MODEL = 0x0014
SOLICITATION_PDU_RPL_CONFIGURATION_CLIENT_MODEL = 0x0015

# Generic Models
GENERIC_ONOFF_SERVER_MODEL = 0x1000
GENERIC_ONOFF_CLIENT_MODEL = 0x1001
GENERIC_LEVEL_SERVER_MODEL = 0x1002
GENERIC_LEVEL_CLIENT_MODEL = 0x1003
GENERIC_DEFAULT_TRANSITION_TIME_SERVER_MODEL = 0x1004
GENERIC_DEFAULT_TRANSITION_TIME_CLIENT_MODEL = 0x1005
GENERIC_POWER_ONOFF_SERVER_MODEL = 0x1006
GENERIC_POWER_ONOFF_SETUP_SERVER_MODEL = 0x1007
GENERIC_POWER_ONOFF_CLIENT_MODEL = 0x1008
GENERIC_POWER_LEVEL_SERVER_MODEL = 0x1009
GENERIC_POWER_LEVEL_SETUP_SERVER_MODEL = 0x100A
GENERIC_POWER_LEVEL_CLIENT_MODEL = 0x100B
GENERIC_BATTERY_SERVER_MODEL = 0x100C
GENERIC_BATTERY_CLIENT_MODEL = 0x100D
GENERIC_LOCATION_SERVER_MODEL = 0x100E
GENERIC_LOCATION_SETUP_SERVER_MODEL = 0x100F
GENERIC_LOCATION_CLIENT_MODEL = 0x1010
GENERIC_ADMIN_PROPERTY_SERVER_MODEL = 0x1011
GENERIC_MANUFACTURER_PROPERTY_SERVER_MODEL = 0x1012
GENERIC_USER_PROPERTY_SERVER_MODEL = 0x1013
GENERIC_CLIENT_PROPERTY_SERVER_MODEL = 0x1014
GENERIC_PROPERTY_CLIENT_MODEL = 0x1015

# Sensor Models
SENSOR_SERVER_MODEL = 0x1100
SENSOR_SETUP_SERVER_MODEL = 0x1101
SENSOR_CLIENT_MODEL = 0x1102

# Time and Scenes Models
TIME_SERVER_MODEL = 0x1200
TIME_SETUP_SERVER_MODEL = 0x1201
TIME_CLIENT_MODEL = 0x1202
SCENE_SERVER_MODEL = 0x1203
SCENE_SETUP_SERVER_MODEL = 0x1204
SCENE_CLIENT_MODEL = 0x1205
SCHEDULER_SERVER_MODEL = 0x1206
SCHEDULER_SETUP_SERVER_MODEL = 0x1207
SCHEDULER_CLIENT_MODEL = 0x1208

# Lighting Models
LIGHT_LIGHTNESS_SERVER_MODEL = 0x1300
LIGHT_LIGHTNESS_SETUP_SERVER_MODEL = 0x1301
LIGHT_LIGHTNESS_CLIENT_MODEL = 0x1302
LIGHT_CTL_SERVER_MODEL = 0x1303
LIGHT_CTL_SETUP_SERVER_MODEL = 0x1304
LIGHT_CTL_CLIENT_MODEL = 0x1305
LIGHT_CTL_TEMPERATURE_SERVER_MODEL = 0x1306
LIGHT_HSL_SERVER_MODEL = 0x1307
LIGHT_HSL_SETUP_SERVER_MODEL = 0x1308
LIGHT_HSL_CLIENT_MODEL = 0x1309
LIGHT_HSL_HUE_SERVER_MODEL = 0x130A
LIGHT_HSL_SATURATION_SERVER_MODEL = 0x130B
LIGHT_XYL_SERVER_MODEL = 0x130C
LIGHT_XYL_SETUP_SERVER_MODEL = 0x130D
LIGHT_XYL_CLIENT_MODEL = 0x130E
LIGHT_LC_SERVER_MODEL = 0x130F
LIGHT_LC_SETUP_SERVER_MODEL = 0x1310
LIGHT_LC_CLIENT_MODEL = 0x1311
IEC_62386_104_MODEL = 0x1312

# Firmware and BLOB Transfer Models
BLOB_TRANSFER_SERVER_MODEL = 0x1400
BLOB_TRANSFER_CLIENT_MODEL = 0x1401
FIRMWARE_UPDATE_SERVER_MODEL = 0x1402
FIRMWARE_UPDATE_CLIENT_MODEL = 0x1403
FIRMWARE_DISTRIBUTION_SERVER_MODEL = 0x1404
FIRMWARE_DISTRIBUTION_CLIENT_MODEL = 0x1405

# List of all SIG Models with their IDs and names
ALL_SIG_MODELS = [
    (CONFIGURATION_SERVER_MODEL, "Configuration Server"),
    (CONFIGURATION_CLIENT_MODEL, "Configuration Client"),
    (HEALTH_SERVER_MODEL, "Health Server"),
    (HEALTH_CLIENT_MODEL, "Health Client"),
    (REMOTE_PROVISIONING_SERVER_MODEL, "Remote Provisioning Server"),
    (REMOTE_PROVISIONING_CLIENT_MODEL, "Remote Provisioning Client"),
    (DIRECTED_FORWARDING_CONFIGURATION_SERVER_MODEL, "Directed Forwarding Configuration Server"),
    (DIRECTED_FORWARDING_CONFIGURATION_CLIENT_MODEL, "Directed Forwarding Configuration Client"),
    (BRIDGE_CONFIGURATION_SERVER_MODEL, "Bridge Configuration Server"),
    (BRIDGE_CONFIGURATION_CLIENT_MODEL, "Bridge Configuration Client"),
    (MESH_PRIVATE_BEACON_SERVER_MODEL, "Mesh Private Beacon Server"),
    (MESH_PRIVATE_BEACON_CLIENT_MODEL, "Mesh Private Beacon Client"),
    (ON_DEMAND_PRIVATE_PROXY_SERVER_MODEL, "On-Demand Private Proxy Server"),
    (ON_DEMAND_PRIVATE_PROXY_CLIENT_MODEL, "On-Demand Private Proxy Client"),
    (SAR_CONFIGURATION_SERVER_MODEL, "SAR Configuration Server"),
    (SAR_CONFIGURATION_CLIENT_MODEL, "SAR Configuration Client"),
    (OPCODES_AGGREGATOR_SERVER_MODEL, "Opcodes Aggregator Server"),
    (OPCODES_AGGREGATOR_CLIENT_MODEL, "Opcodes Aggregator Client"),
    (LARGE_COMPOSITION_DATA_SERVER_MODEL, "Large Composition Data Server"),
    (LARGE_COMPOSITION_DATA_CLIENT_MODEL, "Large Composition Data Client"),
    (SOLICITATION_PDU_RPL_CONFIGURATION_SERVER_MODEL, "Solicitation PDU RPL Configuration Server"),
    (SOLICITATION_PDU_RPL_CONFIGURATION_CLIENT_MODEL, "Solicitation PDU RPL Configuration Client"),
    (GENERIC_ONOFF_SERVER_MODEL, "Generic OnOff Server"),
    (GENERIC_ONOFF_CLIENT_MODEL, "Generic OnOff Client"),
    (GENERIC_LEVEL_SERVER_MODEL, "Generic Level Server"),
    (GENERIC_LEVEL_CLIENT_MODEL, "Generic Level Client"),
    (GENERIC_DEFAULT_TRANSITION_TIME_SERVER_MODEL, "Generic Default Transition Time Server"),
    (GENERIC_DEFAULT_TRANSITION_TIME_CLIENT_MODEL, "Generic Default Transition Time Client"),
    (GENERIC_POWER_ONOFF_SERVER_MODEL, "Generic Power OnOff Server"),
    (GENERIC_POWER_ONOFF_SETUP_SERVER_MODEL, "Generic Power OnOff Setup Server"),
    (GENERIC_POWER_ONOFF_CLIENT_MODEL, "Generic Power OnOff Client"),
    (GENERIC_POWER_LEVEL_SERVER_MODEL, "Generic Power Level Server"),
    (GENERIC_POWER_LEVEL_SETUP_SERVER_MODEL, "Generic Power Level Setup Server"),
    (GENERIC_POWER_LEVEL_CLIENT_MODEL, "Generic Power Level Client"),
    (GENERIC_BATTERY_SERVER_MODEL, "Generic Battery Server"),
    (GENERIC_BATTERY_CLIENT_MODEL, "Generic Battery Client"),
    (GENERIC_LOCATION_SERVER_MODEL, "Generic Location Server"),
    (GENERIC_LOCATION_SETUP_SERVER_MODEL, "Generic Location Setup Server"),
    (GENERIC_LOCATION_CLIENT_MODEL, "Generic Location Client"),
    (GENERIC_ADMIN_PROPERTY_SERVER_MODEL, "Generic Admin Property Server"),
    (GENERIC_MANUFACTURER_PROPERTY_SERVER_MODEL, "Generic Manufacturer Property Server"),
    (GENERIC_USER_PROPERTY_SERVER_MODEL, "Generic User Property Server"),
    (GENERIC_CLIENT_PROPERTY_SERVER_MODEL, "Generic Client Property Server"),
    (GENERIC_PROPERTY_CLIENT_MODEL, "Generic Property Client"),
    (SENSOR_SERVER_MODEL, "Sensor Server"),
    (SENSOR_SETUP_SERVER_MODEL, "Sensor Setup Server"),
    (SENSOR_CLIENT_MODEL, "Sensor Client"),
    (TIME_SERVER_MODEL, "Time Server"),
    (TIME_SETUP_SERVER_MODEL, "Time Setup Server"),
    (TIME_CLIENT_MODEL, "Time Client"),
    (SCENE_SERVER_MODEL, "Scene Server"),
    (SCENE_SETUP_SERVER_MODEL, "Scene Setup Server"),
    (SCENE_CLIENT_MODEL, "Scene Client"),
    (SCHEDULER_SERVER_MODEL, "Scheduler Server"),
    (SCHEDULER_SETUP_SERVER_MODEL, "Scheduler Setup Server"),
    (SCHEDULER_CLIENT_MODEL, "Scheduler Client"),
    (LIGHT_LIGHTNESS_SERVER_MODEL, "Light Lightness Server"),
    (LIGHT_LIGHTNESS_SETUP_SERVER_MODEL, "Light Lightness Setup Server"),
    (LIGHT_LIGHTNESS_CLIENT_MODEL, "Light Lightness Client"),
    (LIGHT_CTL_SERVER_MODEL, "Light CTL Server"),
    (LIGHT_CTL_SETUP_SERVER_MODEL, "Light CTL Setup Server"),
    (LIGHT_CTL_CLIENT_MODEL, "Light CTL Client"),
    (LIGHT_CTL_TEMPERATURE_SERVER_MODEL, "Light CTL Temperature Server"),
    (LIGHT_HSL_SERVER_MODEL, "Light HSL Server"),
    (LIGHT_HSL_SETUP_SERVER_MODEL, "Light HSL Setup Server"),
    (LIGHT_HSL_CLIENT_MODEL, "Light HSL Client"),
    (LIGHT_HSL_HUE_SERVER_MODEL, "Light HSL Hue Server"),
    (LIGHT_HSL_SATURATION_SERVER_MODEL, "Light HSL Saturation Server"),
    (LIGHT_XYL_SERVER_MODEL, "Light xyL Server"),
    (LIGHT_XYL_SETUP_SERVER_MODEL, "Light xyL Setup Server"),
    (LIGHT_XYL_CLIENT_MODEL, "Light xyL Client"),
    (LIGHT_LC_SERVER_MODEL, "Light LC Server"),
    (LIGHT_LC_SETUP_SERVER_MODEL, "Light LC Setup Server"),
    (LIGHT_LC_CLIENT_MODEL, "Light LC Client"),
    (IEC_62386_104_MODEL, "IEC 62386-104 Model"),
    (BLOB_TRANSFER_SERVER_MODEL, "BLOB Transfer Server"),
    (BLOB_TRANSFER_CLIENT_MODEL, "BLOB Transfer Client"),
    (FIRMWARE_UPDATE_SERVER_MODEL, "Firmware Update Server"),
    (FIRMWARE_UPDATE_CLIENT_MODEL, "Firmware Update Client"),
    (FIRMWARE_DISTRIBUTION_SERVER_MODEL, "Firmware Distribution Server"),
    (FIRMWARE_DISTRIBUTION_CLIENT_MODEL, "Firmware Distribution Client"),
]

CUSTOM_DEVICE_INFO_SERVER_MODEL = [COMPANY_ID, 0x1400]
CUSTOM_DEVICE_INFO_CLIENT_MODEL = [COMPANY_ID, 0x1401]
CUSTOM_SENSOR_SERVER_MODEL = [COMPANY_ID, 0x1414]
CUSTOM_SENSOR_CLIENT_MODEL = [COMPANY_ID, 0x1415]
CUSTOM_AC_SERVER_MODEL = [COMPANY_ID, 0x1416]
CUSTOM_AC_CLIENT_MODEL = [COMPANY_ID, 0x1417]

ALL_CUSTOM_MODELS = [
    (CUSTOM_DEVICE_INFO_CLIENT_MODEL, "Custom Device Info Client Model"),
    (CUSTOM_DEVICE_INFO_SERVER_MODEL, "Custom Device Info Server Model"),
    (CUSTOM_SENSOR_CLIENT_MODEL, "Custom Sensor Client Model"),
    (CUSTOM_SENSOR_SERVER_MODEL, "Custom Sensor Server Model"),
    (CUSTOM_AC_SERVER_MODEL, "Custom Air Conditioner Server Model"),
    (CUSTOM_AC_CLIENT_MODEL, "Custom Air Conditioner Client Model"),
]

def read_sig_models(model_list):
    sig_model_list = []
    for sig_model in ALL_SIG_MODELS:
        for model in model_list: 
            if model == sig_model[0]:
                sig_model_list.append(sig_model)
                break

    return sig_model_list

def read_vendor_models(model_list):
    vendor_model_list = []
    for vendor_model in ALL_CUSTOM_MODELS:
        for model in model_list: 
            if model == vendor_model[0]:
                vendor_model_list.append(vendor_model)
                break

    return vendor_model_list
