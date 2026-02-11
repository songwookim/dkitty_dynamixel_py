"""Force (current) control example for 3-DOF (single leg).

Sets 3 joints to current control mode and applies torques.
"""

import sys
import os

import numpy as np
import hydra
from omegaconf import DictConfig, OmegaConf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from dynamixel_control import DynamixelControl


@hydra.main(version_base=None, config_path="..", config_name="config")
def main(cfg: DictConfig):
    OmegaConf.set_struct(cfg, False)
    cfg["dynamixel"]["control_modes"]["default_mode"] = 0  # current control
    cfg["dynamixel"]["ids"] = [10, 11, 12]

    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()

    try:
        torques = [0, 2, 4]
        controller.set_goal_current(np.array(torques, dtype=np.int64))
    finally:
        controller.close_port()


if __name__ == "__main__":
    main()
