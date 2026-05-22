# src/wii_remote_pkg/constants.py
# Constants for Wii Remote

class WiiRemoteConstants:
    VENDOR_ID = 0x057E
    PRODUCT_ID = 0x0306

    Hz = 95

    BTN_A = "A"
    BTN_B = "B"
    BTN_UP = "Up"
    BTN_DOWN = "Down"
    BTN_LEFT = "Left"
    BTN_RIGHT = "Right"
    BTN_MINUS = "Minus"
    BTN_PLUS = "Plus"
    BTN_1 = "1"
    BTN_2 = "2"
    BTN_HOME = "Home"

    CMD_RUMBLE_ON = {"command": [0x10, 0x01], "description": "Turn Rumble On"}
    CMD_RUMBLE_OFF = {"command": [0x10, 0x00], "description": "Turn Rumble Off"}

    CMD_LED_1 = {"command": [0x11, 0x10], "description": "Turn first LED On"}
    CMD_LED_2 = {"command": [0x11, 0x20], "description": "Turn second LED On"}
    CMD_LED_3 = {"command": [0x11, 0x40], "description": "Turn third LED On"}
    CMD_LED_4 = {"command": [0x11, 0x80], "description": "Turn fourth LED On"}

    CMD_BTN = {"command": [0x12, 0x00, 0x30], "description": "Noncontinuous data report: Core buttons"}
    CMD_BTN_ACC = {"command": [0x12, 0x00, 0x31],
                   "description": "Noncontinuous data report: Core Buttons, Accelerometer"}
    CMD_BTN_8EXT = {"command": [0x12, 0x00, 0x32],
                    "description": "Noncontinuous data report: Core Buttons, 8 Extension Bytes"}
    CMD_BTN_ACC_12IR = {"command": [0x12, 0x00, 0x33],
                        "description": "Noncontinuous data report: Core Buttons, Accelerometer, 12 IR Bytes"}
    CMD_BTN_19EXT = {"command": [0x12, 0x00, 0x34],
                     "description": "Noncontinuous data report: Core Buttons, 19 Extension Bytes"}
    CMD_BTN_ACC_16EXT = {"command": [0x12, 0x00, 0x35],
                         "description": "Noncontinuous data report: Core Buttons, Accelerometer, 16 Extension Bytes"}
    CMD_BTN_10IR_9EXT = {"command": [0x12, 0x00, 0x36],
                         "description": "Noncontinuous data report: Core Buttons, 10 IR Bytes, 9 Extension Bytes"}
    CMD_BTN_10IR_6EXT = {"command": [0x12, 0x00, 0x37],
                         "description": "Noncontinuous data report: Core Buttons, 10 IR Bytes, 6 Extension Bytes"}
    CMD_21EXT = {"command": [0x12, 0x00, 0x3d], "description": "Noncontinuous data report: 21 Extension Bytes"}

    CMD_CONT_BTN = {"command": [0x12, 0x04, 0x30], "description": "Continuous data report: Core Buttons"}
    CMD_CONT_BTN_ACC = {"command": [0x12, 0x04, 0x31],
                        "description": "Continuous data report: Core Buttons, Accelerometer"}
    CMD_CONT_BTN_8EXT = {"command": [0x12, 0x04, 0x32],
                         "description": "Continuous data report: Core Buttons, 8 Extension Bytes"}
    CMD_CONT_BTN_ACC_12IR = {"command": [0x12, 0x04, 0x33],
                             "description": "Continuous data report: Core Buttons, Accelerometer, 12 IR Bytes"}
    CMD_CONT_BTN_19EXT = {"command": [0x12, 0x04, 0x34],
                          "description": "Continuous data report: Core Buttons, 19 Extension Bytes"}
    CMD_CONT_BTN_ACC_16EXT = {"command": [0x12, 0x04, 0x35],
                              "description": "Continuous data report: Core Buttons, Accelerometer, 16 Extension Bytes"}
    CMD_CONT_BTN_10IR_9EXT = {"command": [0x12, 0x04, 0x36],
                              "description": "Continuous data report: Core Buttons, 10 IR Bytes, 9 Extension Bytes"}
    CMD_CONT_BTN_10IR_6EXT = {"command": [0x12, 0x04, 0x37],
                              "description": "Continuous data report: Core Buttons, 10 IR Bytes, 6 Extension Bytes"}
    CMD_CONT_21EXT = {"command": [0x12, 0x04, 0x3d], "description": "Continuous data report: 21 Extension Bytes"}

    CMD_REQUEST_STATUS = {"command": [0x15, 0x00], "description": "Request Status Report"}

    MAX_RUMBLE_TIME = 0.5
