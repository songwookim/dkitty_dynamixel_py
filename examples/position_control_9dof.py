"""Position control example for 9-DOF D'Kitty robot.

Sets all 9 joints to position control mode and moves to goal positions.
"""

import sys
import os

import hydra
from omegaconf import DictConfig, OmegaConf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from dynamixel_control import DynamixelControl


@hydra.main(version_base=None, config_path="..", config_name="config")
def main(cfg: DictConfig):
    OmegaConf.set_struct(cfg, False)
    cfg["dynamixel"]["control_modes"]["default_mode"] = 3  # position control
    cfg["dynamixel"]["ids"] = [10, 11, 12, 20, 21, 22, 30, 31, 32]

    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()

    try:
        goal_positions = [1000, 1700, 2500, 1000, 1700, 2500, 1000, 1700, 2500]
        controller.set_joint_positions(goal_positions)

        positions_deg = controller.dynamixel_pos_to_deg(goal_positions)
        print(f"Goal positions (deg): {positions_deg}")
    finally:
        controller.close_port()


if __name__ == "__main__":
    main()
