import hydra
from omegaconf import DictConfig
from dynamixel_control import DynamixelControl
import time
import os
import numpy as np
@hydra.main(version_base=None, config_path=".", config_name="config")
def main(cfg: DictConfig):
    T = 100
    
    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()
    cur_deg = controller.get_joint_positions()
    
    positions = [1000, 1000]
    timeer = 1
    print(f"{time.process_time()}")
    
    while True:
        timeer +=1

        b = np.random.randint(0,4096)
        a = np.random.randint(0,4096)
        controller.set_joint_positions([a,b])
        if timeer >= 100:
            break
        # print(timeer)
        
    print(f"{time.process_time()}")
        
    # cur_deg = controller.dynamixel_pos_to_deg(initial_val)
    
    # print(cur_deg)


if __name__ == "__main__":
    main()
