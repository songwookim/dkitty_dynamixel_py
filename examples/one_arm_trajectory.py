import os
import numpy as np

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import * # Uses Dynamixel SDK library

#********* DYNAMIXEL Model definition *********
#***** (Use only one definition at a time) *****
MY_DXL = 'X_SERIES'       # X330 (5.0 V recommended), X430, X540, 2X430


# Control table address
ADDR_TORQUE_ENABLE          = 64
ADDR_GOAL_POSITION          = 116
ADDR_PRESENT_POSITION       = 132
DXL_MINIMUM_POSITION_VALUE  = 0         # Refer to the Minimum Position Limit of product eManual
DXL_MAXIMUM_POSITION_VALUE  = 4095      # Refer to the Maximum Position Limit of product eManual
BAUDRATE                    = 57600
PROTOCOL_VERSION            = 2.0

# Factory default ID of all DYNAMIXEL is 1
# DXL_IDs                      = [10,11,12,20,21,22,]
DXL_IDs                      = [10,11,12,20,21,22,30,31,32,40,41,42]

# Use the actual port assigned to the U2D2.4
DEVICENAME                  = '/dev/ttyUSB0'
TORQUE_ENABLE               = 1     # Value for enabling the torque
TORQUE_DISABLE              = 0     # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 20    # Dynamixel moving status threshold

# ===========================================================================================================
# data
import csv
import os
import numpy as np
import time
def get_data() -> list:
    datas = list()

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "monkey/data.csv"
    abs_file_path = os.path.join(script_dir, rel_path)
    f = open(abs_file_path,'r')
    rea = csv.reader(f)
    for row in rea:
        row = [float(i)*np.pi for i in row]
        row[0:7:2] = np.add(row[0:7:2], np.pi/2)
        row[1:8:2] = np.add(row[0:7:2], row[1:8:2])
    
        datas.append(row)
    f.close
    return datas

def rad_to_dynamixel(datas) :
    datas = np.array(datas)
    datas_dynamixel = datas * (180/np.pi) * 11.37
    return datas_dynamixel

def main() :
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    # Open port
    if portHandler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        print("Press any key to terminate...")
        getch()
        quit()

    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        quit()

    # Enable Dynamixel Torque
    for id in DXL_IDs:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)    
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")            

    datas = get_data() # rad
    goals = rad_to_dynamixel(datas)
    
    while 1 :
        for dxl_goal_positions in goals :
            dxl_goal_positions = np.insert(dxl_goal_positions,[0,2,4,6],1024)
            dxl_goal_positions[6] = 1250
            for idx, dxl_id in enumerate(DXL_IDs):
                print("Press any key to continue! (or press ESC to quit!)")
                dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, int(dxl_goal_positions[idx]))
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                    

            # time.sleep(0.01)
#        break

    portHandler.closePort()
main()

