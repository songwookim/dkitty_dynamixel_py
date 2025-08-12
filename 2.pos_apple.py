import hydra
from omegaconf import DictConfig
from dynamixel_control import DynamixelControl
import time
import os

@hydra.main(version_base=None, config_path=".", config_name="config")
def main(cfg: DictConfig):
    
    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()
    cur_deg = controller.get_joint_positions()
    # initial_val = [1000, 1700, 2500, 1000, 1700, 2500, 1000, 1700, 2500]
    initial_val = [1700, 1700, 1700]
    controller.set_joint_positions(initial_val)
    cur_deg = controller.dynamixel_pos_to_deg(initial_val)
    
    print(cur_deg)


if __name__ == "__main__":
    main()