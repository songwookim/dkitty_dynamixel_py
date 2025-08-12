import hydra
from omegaconf import DictConfig, OmegaConf
from dynamixel_control import DynamixelControl
import time
import os
import numpy as np

@hydra.main(version_base=None, config_path=".", config_name="config")
def main(cfg: DictConfig):
    OmegaConf.set_struct(cfg, False)
    cfg["dynamixel"]["default_mode"] = 0
    cfg["dynamixel"]["ids"] = [10,11,12,20,21,22,30,31,32] 

    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()
    torques = [0,2,4,0,2,4,0,2,4]
    # torques = [0,0,0,0,0,0,0,0,0]
    controller.test_torqueinput((np.int64(torques)))

if __name__ == "__main__":
    main()