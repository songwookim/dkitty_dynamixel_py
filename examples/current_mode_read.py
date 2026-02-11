"""Current mode with position reading loop.

Sets all joints to current control mode with zero torque,
then continuously reads and prints current positions.
"""

import sys
import os
import time

import hydra
from omegaconf import DictConfig

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from dynamixel_control import DynamixelControl


@hydra.main(version_base=None, config_path="..", config_name="config")
def main(cfg: DictConfig):
    T = 10000
    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()

    try:
        # Set zero torque
        zero_torques = [0] * len(cfg.dynamixel.ids)
        controller.set_goal_current(zero_torques)

        # Read positions in a loop
        for i in range(T):
            time.sleep(0.1)
            positions = controller.get_joint_positions()
            print(f"Step {i}: {positions}")
    finally:
        controller.close_port()


if __name__ == "__main__":
    main()
