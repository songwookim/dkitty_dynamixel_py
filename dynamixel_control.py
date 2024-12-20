import sys
import tty
import termios
from dynamixel_sdk import *  # Uses Dynamixel SDK library

class DynamixelControl:
    def __init__(self, config):
        self.cfg = config
        self.portHandler = PortHandler(self.cfg.device_name)
        self.packetHandler = PacketHandler(self.cfg.protocol_version)
        self.old_settings = termios.tcgetattr(sys.stdin.fileno())

    def getch(self):
        fd = sys.stdin.fileno()
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, self.old_settings)
        return ch

    def connect(self):
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            raise Exception("Failed to open the port")

        if self.portHandler.setBaudRate(self.cfg.baudrate):
            print("Succeeded to change the baudrate")
        else:
            raise Exception("Failed to change the baudrate")
        # if self.get_operating_mode() != self.cfg.control_modes.default_mode:
        self.disable_torque()
        self.set_operating_mode(self.cfg.control_modes.default_mode)

        self.enable_torque() # for dynamaixel operation
        


    def set_operating_mode(self, mode):
        for id in self.cfg.ids:
            # mode = self.cfg.control_modes.default_mode
            addr_operating_mode = self.cfg.control_table.addr_operating_mode
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                self.portHandler, id, addr_operating_mode, mode)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to set operating mode: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Dynamixel ID {id} set to mode {mode}")

    def get_operating_mode(self) -> int:
        addr_operating_mode = self.cfg.control_table.addr_operating_mode
        for id in self.cfg.ids:
            dxl_current_state, dxl_comm_result, dxl_error = self.packetHandler.read1ByteTxRx( # state -> mode depenedent
                self.portHandler, id, addr_operating_mode)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to get operating mode: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Operating mode for Dynamixel ID {id} is {dxl_current_state}")
        return dxl_current_state
    
    def enable_torque(self):
        addr_torque_enable = self.cfg.control_table.addr_torque_enable
        for id in self.cfg.ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                self.portHandler, id, addr_torque_enable, self.cfg.torque_enable)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to enable torque: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Torque enabled for Dynamixel ID {id}")
    def dynamixel_pos_to_deg(self, pos):
        return pos * 0.0878
    def get_joint_velocities(self) -> int:
        ADDR_PRESENT_VELOCITY = self.cfg.control_table.ADDR_PRESENT_VELOCITY
        for id in self.cfg.ids:
            dxl_present_velocity, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
                self.portHandler, id, ADDR_PRESENT_VELOCITY)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to get velocity: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            # else:
            #     print(f"Velocity for Dynamixel ID {id} is {dxl_present_velocity}")
            if dxl_present_velocity > 0x7fffffff:
                dxl_present_velocity = dxl_present_velocity - 4294967296
        return dxl_present_velocity
    
    def get_joint_positions(self) -> int:
        ADDR_PRESENT_POSITION = self.cfg.control_table.ADDR_PRESENT_POSITION
        for id in self.cfg.ids:
            dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
                self.portHandler, id, ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to get position: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            # else:
            #     print(f"Position for Dynamixel ID {id} is {dxl_present_position}")
        # rad = self.dynamixel_pos_to_deg(dxl_present_position)
        return rad
        
    
    def disable_torque(self):
        addr_torque_enable = self.cfg.control_table.addr_torque_enable
        for id in self.cfg.ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                self.portHandler, id, addr_torque_enable, self.cfg.torque_disable)
            if dxl_comm_result != COMM_SUCCESS:
                print(f"Failed to disable torque: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                print(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Torque disabled for Dynamixel ID {id}")
                
    def test_torqueinput(self, input_torque):
        ADDR_GOAL_CURRENT = self.cfg.control_table.ADDR_GOAL_CURRENT
        for id in self.cfg.ids:
            dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
                self.portHandler, id, ADDR_GOAL_CURRENT, input_torque)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to write torque: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            # else:
            #     print(f"Torque written for Dynamixel ID {id}")
    def close_port(self):
        self.disable_torque()
        self.portHandler.closePort()
        print("Port closed")
