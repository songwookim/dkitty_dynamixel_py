import hydra
from omegaconf import DictConfig
from dynamixel_control import DynamixelControl
import time
import os
import numpy as np

@hydra.main(version_base=None, config_path=".", config_name="config")
def main(cfg: DictConfig):
    T = 100
    T = 100
    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()
    torques = [10,8,30]
    # torques = [0,0,0]
    controller.test_torqueinput((np.int64(torques)))

if __name__ == "__main__":
    main()