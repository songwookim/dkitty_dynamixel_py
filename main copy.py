import hydra
from omegaconf import DictConfig
from dynamixel_control import DynamixelControl
import time
import os

@hydra.main(version_base=None, config_path=".", config_name="config")
def main(cfg: DictConfig):
    T = 100
    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()

    # try:
    #     # controller.disable_torque()
    #     cur_deg = controller.get_joint_positions()
    #     cur_vel_deg = controller.get_joint_velocities()
    
        # for i in range(T):
        
        #     # Read updated positions and velocities
        #     cur_deg = controller.get_joint_positions()
        #     cur_vel_deg = controller.get_joint_velocities()
        #     print(cur_deg)
            
        # while True:
        #     controller.test_torqueinput(tau) # 2 Nm (must set torque limit to 2 Nm)
    # except Exception as e:
    #     print(f"Error: {e}")
    # finally:
    #     controller.close_port()

if __name__ == "__main__":
    main()
