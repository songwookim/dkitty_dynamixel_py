import os, sys, ctypes

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    def getch():
        return sys.stdin.read(1)

os.sys.path.append('../dynamixel_functions_py')             # Path setting

from dynamixel_sdk import *                     # Uses DYNAMIXEL SDK library

# Control table address
ADDR_PRO_TORQUE_ENABLE      = 562                           # Control table address is different in Dynamixel model
ADDR_PRO_LED_RED            = 563
ADDR_PRO_GOAL_POSITION      = 596
ADDR_PRO_PRESENT_POSITION   = 611

# Data Byte Length
LEN_PRO_LED_RED             = 1
LEN_PRO_GOAL_POSITION       = 4
LEN_PRO_PRESENT_POSITION    = 4

# Protocol version
PROTOCOL_VERSION            = 2                             # See which protocol version is used in the Dynamixel

# Default setting
DXL1_ID                     = 1                             # Dynamixel ID: 1
DXL2_ID                     = 2                             # Dynamixel ID: 2
BAUDRATE                    = 57600#115200
DEVICENAME                  = "/dev/ttyUSB0"                # Check which port is being used on your controller
                                                            # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0"

TORQUE_ENABLE               = 1                             # Value for enabling the torque
TORQUE_DISABLE              = 0                             # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE  = -150000                       # Dynamixel will rotate between this value
DXL_MAXIMUM_POSITION_VALUE  = 150000                        # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
DXL_MOVING_STATUS_THRESHOLD = 20                            # Dynamixel moving status threshold

ESC_ASCII_VALUE             = 0x1b

COMM_SUCCESS                = 0                             # Communication Success result value
COMM_TX_FAIL                = -1001                         # Communication Tx Failed

# Initialize PortHandler Structs
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler Structs
packetHandler = PacketHandler(PROTOCOL_VERSION)

groupBulkRead = GroupBulkRead(portHandler, packetHandler)
groupBulkWrite = GroupBulkWrite(portHandler, packetHandler)

index = 0
dxl_comm_result = COMM_TX_FAIL                              # Communication result
dxl_addparam_result = 0                                     # AddParam result
dxl_getdata_result = 0                                      # GetParam result
dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]         # Goal position

dxl_error = 0                                               # Dynamixel error
dxl_led_value = [0, 255]                                    # Dynamixel LED value for write
dxl1_present_position = 0                                   # Present position
dxl2_led_value_read = 0                                     # Dynamixel moving status


# Open port
if portHandler.openPort():
    print("Succeeded to open the port!")
else:
    print("Failed to open the port!")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate!")
else:
    print("Failed to change the baudrate!")
    print("Press any key to terminate...")
    getch()
    quit()


# Enable Dynamixel#1 Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Dynamixel has been successfully connected")

# Enable Dynamixel#2 Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL2_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Dynamixel has been successfully connected")


# Add parameter storage for Dynamixel#1 present position value
dxl_addparam_result = (groupBulkRead.addParam(DXL1_ID, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION))
if dxl_addparam_result != 1:
    print("[ID:%03d] groupBulkRead addparam failed" % (DXL1_ID))
    quit()

# Add parameter storage for Dynamixel#2 present moving value
dxl_addparam_result = (groupBulkRead.addParam(DXL2_ID, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION))
if dxl_addparam_result != 1:
    print("[ID:%03d] groupBulkRead addparam failed" % (DXL2_ID))
    quit()
groupBulkRead.txPacket()

while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(ESC_ASCII_VALUE):
        break

    # Add parameter storage for Dynamixel#1 goal position
    dxl_addparam_result = groupBulkWrite.addParam(DXL1_ID, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION, "0")
    if dxl_addparam_result != 1:
        print("[ID:%03d] groupBulkWrite addparam failed", DXL1_ID)
        quit()

    # Add parameter storage for Dynamixel#2 LED value
    dxl_addparam_result = groupBulkWrite.addParam(DXL2_ID, ADDR_PRO_LED_RED, LEN_PRO_LED_RED, "0")
    if dxl_addparam_result != 1:
        print("[ID:%03d] groupBulkWrite addparam failed", DXL2_ID)
        quit()

    # Bulkwrite goal position and LED value
    dxl_comm_result = packetHandler.bulkWriteTxOnly(portHandler, groupBulkWrite.param, len(groupBulkWrite.param))
    if dxl_comm_result != COMM_SUCCESS:
        print("fail!")

    # Clear bulkwrite parameter storage
    groupBulkWrite.clearParam()

    while 1:
        # Add parameter storage for Dynamixel#1 goal position
        dxl_addparam_result = groupBulkRead.addParam(DXL1_ID, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION)
        if dxl_addparam_result != 1:
            print("[ID:%03d] groupBulkWrite addparam failed", DXL1_ID)
            quit()

        # Add parameter storage for Dynamixel#2 LED value
        dxl_addparam_result = groupBulkRead.addParam(DXL2_ID, ADDR_PRO_LED_RED, LEN_PRO_LED_RED)
        if dxl_addparam_result != 1:
            print("[ID:%03d] groupBulkWrite addparam failed", DXL2_ID)
            quit()
        
        # Bulkread present position and moving status
        dxl_comm_result = packetHandler.bulkReadTx(portHandler, groupBulkRead.param, len(groupBulkWrite.param))
        if dxl_comm_result != COMM_SUCCESS:
            print("fail!")

        # Check if groupbulkread data of Dynamixel#1 is available
        dxl_getdata_result = groupBulkRead.isAvailable(DXL1_ID, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
        if dxl_getdata_result != 1:
            print("[ID:%03d] groupBulkRead getdata failed" % (DXL1_ID))
            quit()

        # Check if groupbulkread data of Dynamixel#2 is available
        dxl_getdata_result = groupBulkRead.isAvailable(DXL2_ID, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
        if dxl_getdata_result != 1:
            print("[ID:%03d] groupBulkRead getdata failed" % (DXL2_ID))
            quit()

        # Get Dynamixel#1 present position value
        dxl1_present_position = groupBulkRead.getData(DXL1_ID, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)

        # Get Dynamixel#2 moving status value
        dxl2_present_position = groupBulkRead.getData(DXL1_ID, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)

        print("[ID:%03d] Present Position : %d \t [ID:%03d] LED Value: %d" % (DXL1_ID, dxl1_present_position, DXL2_ID, dxl2_led_value_read))

        if not (abs(dxl_goal_position[index] - dxl1_present_position) > DXL_MOVING_STATUS_THRESHOLD):
            break

    # Change goal position
    if index == 0:
        index = 1
    else:
        index = 0


# # Disable Dynamixel#1 Torque
# dynamixel.write1ByteTxRx(portHandler, PROTOCOL_VERSION, DXL1_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
# if dynamixel.getLastTxRxResult(portHandler, PROTOCOL_VERSION) != COMM_SUCCESS:
#     dynamixel.printTxRxResult(PROTOCOL_VERSION, dynamixel.getLastTxRxResult(portHandler, PROTOCOL_VERSION))
# elif dynamixel.getLastRxPacketError(portHandler, PROTOCOL_VERSION) != 0:
#     dynamixel.printRxPacketError(PROTOCOL_VERSION, dynamixel.getLastRxPacketError(portHandler, PROTOCOL_VERSION))

# # Disable Dynamixel#2 Torque
# dynamixel.write1ByteTxRx(portHandler, PROTOCOL_VERSION, DXL2_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
# if dynamixel.getLastTxRxResult(portHandler, PROTOCOL_VERSION) != COMM_SUCCESS:
#     dynamixel.printTxRxResult(PROTOCOL_VERSION, dynamixel.getLastTxRxResult(portHandler, PROTOCOL_VERSION))
# elif dynamixel.getLastRxPacketError(portHandler, PROTOCOL_VERSION) != 0:
#     dynamixel.printRxPacketError(PROTOCOL_VERSION, dynamixel.getLastRxPacketError(portHandler, PROTOCOL_VERSION))

# # Close port
# dynamixel.closePort(portHandler)