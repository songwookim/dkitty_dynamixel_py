"""Position control example for 3-DOF (single leg).

Sets 3 joints to position control mode and moves to goal positions.
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
    cfg["dynamixel"]["ids"] = [10, 11, 12]

    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()

    try:
        goal_positions = [1700, 1700, 1700]
        controller.set_joint_positions(goal_positions)

        positions_deg = controller.dynamixel_pos_to_deg(goal_positions)
        print(f"Goal positions (deg): {positions_deg}")
    finally:
        controller.close_port()


if __name__ == "__main__":
    main()
