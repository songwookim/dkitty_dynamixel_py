"""Dynamixel servo motor control module for D'Kitty robot.

Provides a high-level interface for controlling Dynamixel X/MX series servos
via the Dynamixel SDK. Supports position control and current (torque) control modes.

Reference:
    - https://emanual.robotis.com/docs/en/dxl/x/xh430-w350/
    - https://emanual.robotis.com/docs/kr/dxl/protocol2/
"""

import sys
import tty
import termios

import numpy as np
from dynamixel_sdk import *


class DynamixelControl:
    """High-level controller for multiple Dynamixel servos.

    Args:
        config: OmegaConf DictConfig containing dynamixel settings from config.yaml.
    """

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
        """Open port, set baudrate, configure operating mode, and enable torque."""
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            raise Exception("Failed to open the port")

        if self.portHandler.setBaudRate(self.cfg.baudrate):
            print("Succeeded to change the baudrate")
        else:
            raise Exception("Failed to change the baudrate")

        self.disable_torque()
        for dxl_id in self.cfg.ids:
            cur_mode = self.get_operating_mode(dxl_id)
            if cur_mode != self.cfg.control_modes.default_mode:
                self.set_operating_mode_one(dxl_id, self.cfg.control_modes.default_mode)

        self.enable_torque()
    def set_delaytime(self, delaytime):
        """Set return delay time for all servos.

        Args:
            delaytime: Delay time value (0~254), unit: 2 microseconds.
        """
        for dxl_id in self.cfg.ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                self.portHandler, dxl_id, self.cfg.control_table.addr_delaytime, delaytime)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to set delaytime: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Delaytime set for Dynamixel ID {dxl_id}")

    def set_baudrate(self, baudrate):
        """Set baudrate for all servos.

        Args:
            baudrate: Baudrate index (0~7). See Dynamixel e-manual for mapping.
        """
        for dxl_id in self.cfg.ids:
            dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
                self.portHandler, dxl_id, self.cfg.control_table.addr_baudrate, baudrate)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to set baudrate: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Baudrate set for Dynamixel ID {dxl_id}")

    def set_operating_mode_all(self, mode):
        """Set operating mode for all servos.

        Args:
            mode: Operating mode value (see config.yaml control_modes).
        """
        for dxl_id in self.cfg.ids:
            self.set_operating_mode_one(dxl_id, mode)

    def set_operating_mode_one(self, dxl_id, mode):
        """Set operating mode for a single servo.

        Args:
            dxl_id: Target Dynamixel ID.
            mode: Operating mode value.
        """
        addr = self.cfg.control_table.addr_operating_mode
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, dxl_id, addr, mode)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"Failed to set operating mode: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
        else:
            print(f"Dynamixel ID {dxl_id} set to mode {mode}")

    def get_operating_mode_all(self) -> dict:
        """Get operating mode for all servos.

        Returns:
            Dict mapping servo ID to its current operating mode.
        """
        modes = {}
        addr = self.cfg.control_table.addr_operating_mode
        for dxl_id in self.cfg.ids:
            dxl_current_state, dxl_comm_result, dxl_error = self.packetHandler.read1ByteTxRx(
                self.portHandler, dxl_id, addr)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to get operating mode: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Operating mode for Dynamixel ID {dxl_id} is {dxl_current_state}")
            modes[dxl_id] = dxl_current_state
        return modes
    
    def get_operating_mode(self, dxl_id) -> int:
        """Get operating mode for a single servo.

        Args:
            dxl_id: Target Dynamixel ID.

        Returns:
            Current operating mode value.
        """
        addr = self.cfg.control_table.addr_operating_mode
        dxl_current_state, dxl_comm_result, dxl_error = self.packetHandler.read1ByteTxRx(
            self.portHandler, dxl_id, addr)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"Failed to get operating mode: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
        else:
            print(f"Operating mode for Dynamixel ID {dxl_id} is {dxl_current_state}")
        return dxl_current_state

    def enable_torque(self):
        """Enable torque for all servos."""
        addr = self.cfg.control_table.addr_torque_enable
        for dxl_id in self.cfg.ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                self.portHandler, dxl_id, addr, self.cfg.torque_enable)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to enable torque: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Torque enabled for Dynamixel ID {dxl_id}")

    # ── Unit Conversion ─────────────────────────────────────────────

    def dynamixel_pos_to_deg(self, pos):
        """Convert raw Dynamixel position to degrees (360° / 4096 ≈ 0.088°/step)."""
        return np.array(pos) * 0.0879120879

    def dynamixel_pos_to_rad(self, pos) -> np.ndarray:
        """Convert raw Dynamixel position to radians (2π / 4096 ≈ 0.00153 rad/step)."""
        return np.array(pos) * 0.001533981

    # ── Read Methods ─────────────────────────────────────────────────

    def get_joint_velocities(self) -> np.ndarray:
        """Read present velocity of all servos.

        Returns:
            Numpy array of velocity values (unit: 0.229 rev/min per step).
        """
        addr = self.cfg.control_table.ADDR_PRESENT_VELOCITY
        velocities = []
        for dxl_id in self.cfg.ids:
            raw_vel, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
                self.portHandler, dxl_id, addr)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to get velocity: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            # Convert unsigned 32-bit to signed
            if raw_vel > 0x7FFFFFFF:
                raw_vel -= 4294967296
            velocities.append(raw_vel)
        return np.array(velocities)

    def get_joint_positions(self, unit=None) -> np.ndarray:
        """Read present position of all servos.

        Args:
            unit: Output unit - 'rad', 'deg', or None for raw value (0~4095).

        Returns:
            Numpy array of position values in the specified unit.
        """
        addr = self.cfg.control_table.ADDR_PRESENT_POSITION
        positions = []
        for dxl_id in self.cfg.ids:
            raw_pos, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
                self.portHandler, dxl_id, addr)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to get position: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            positions.append(raw_pos)

        if unit == "rad":
            return self.dynamixel_pos_to_rad(positions)
        elif unit == "deg":
            return self.dynamixel_pos_to_deg(positions)
        return np.array(positions, dtype=float)

    # ── Write Methods ────────────────────────────────────────────────

    def set_joint_positions(self, goal_pos):
        """Set goal position for all servos.

        Args:
            goal_pos: List of goal positions (raw value 0~4095) for each servo.
        """
        addr = self.cfg.control_table.ADDR_GOAL_POSITION
        for idx, dxl_id in enumerate(self.cfg.ids):
            dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
                self.portHandler, dxl_id, addr, goal_pos[idx])
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to set position: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
    
    def disable_torque(self):
        """Disable torque for all servos."""
        addr = self.cfg.control_table.addr_torque_enable
        for dxl_id in self.cfg.ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                self.portHandler, dxl_id, addr, self.cfg.torque_disable)
            if dxl_comm_result != COMM_SUCCESS:
                print(f"Failed to disable torque: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                print(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            else:
                print(f"Torque disabled for Dynamixel ID {dxl_id}")

    def set_goal_current(self, currents, log=False):
        """Set goal current (torque) for all servos. Requires current control mode.

        Args:
            currents: List of goal current values for each servo. Unit: ~3.36mA per step.
            log: If True, print status for each servo.

        Raises:
            ValueError: If any current value exceeds the configured max_current.
        """
        addr = self.cfg.control_table.ADDR_GOAL_CURRENT
        max_current = self.cfg.current.max_current
        currents = np.array(currents, dtype=np.int64)

        if np.any(np.abs(currents) > max_current):
            raise ValueError(f"Current value exceeds max_current ({max_current})")

        for idx, dxl_id in enumerate(self.cfg.ids):
            dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
                self.portHandler, dxl_id, addr, int(currents[idx]))
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to write current: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            elif log:
                print(f"Current set for Dynamixel ID {dxl_id}: {currents[idx]}")

    def set_goal_current_one(self, dxl_id, current, log=False):
        """Set goal current (torque) for a single servo.

        Args:
            dxl_id: Target Dynamixel ID.
            current: Goal current value.
            log: If True, print status.
        """
        addr = self.cfg.control_table.ADDR_GOAL_CURRENT
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, dxl_id, addr, int(current))
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"Failed to write current: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
        elif log:
            print(f"Current set for Dynamixel ID {dxl_id}: {current}")

    def set_goal_currents(self, ids, currents, log=False):
        """Set goal current (torque) for a subset of servos.

        Args:
            ids: List of target Dynamixel IDs.
            currents: Array of goal current values corresponding to each ID.
            log: If True, print status for each servo.
        """
        addr = self.cfg.control_table.ADDR_GOAL_CURRENT
        currents = np.array(currents, dtype=np.int64)
        max_current = self.cfg.current.max_current

        if np.any(np.abs(currents) > max_current):
            raise ValueError(f"Current value exceeds max_current ({max_current})")

        for idx, dxl_id in enumerate(ids):
            dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
                self.portHandler, dxl_id, addr, int(currents[idx]))
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception(f"Failed to write current: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            elif dxl_error != 0:
                raise Exception(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            elif log:
                print(f"Current set for Dynamixel ID {dxl_id}: {currents[idx]}")

    # ── Lifecycle ──────────────────────────────────────────────────────

    def close_port(self):
        """Disable torque and close the serial port."""
        self.disable_torque()
        self.portHandler.closePort()
        print("Port closed")