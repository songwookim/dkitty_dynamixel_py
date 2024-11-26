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

    try:
        # controller.disable_torque()
        cur_deg = controller.get_joint_positions()
        cur_vel_deg = controller.get_joint_velocities()
        kp = 0.5 # Nm/deg
        kd = 0.5 # Nm/deg/s
        goal_deg = 175        
        goal_vel_deg = 0
    
        for i in range(T):
            e_deg = goal_deg - cur_deg  # deg
            ed_deg = goal_vel_deg - cur_vel_deg  # deg
            tau = e_deg * kp + ed_deg * kd
            tau = max(-10, min(10, tau))  # Clamp torque
            os.system('clear')
            print(f"Step {i}: Goal={int(goal_deg)}, Current Degree={int(cur_deg)}, Error={int(e_deg)}, Torque={int(tau)}, Velocity={int(cur_vel_deg)} \n")

            
            controller.test_torqueinput(int(tau))

            # Wait for the dynamixel to respond properly
            time.sleep(0.1)  # Reduced delay

            # Read updated positions and velocities
            cur_deg = controller.get_joint_positions()
            cur_vel_deg = controller.get_joint_velocities()
            if cur_deg-goal_deg <= 1:
                print("Goal reached")
                break
            
        # while True:
        #     controller.test_torqueinput(tau) # 2 Nm (must set torque limit to 2 Nm)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.close_port()

if __name__ == "__main__":
    main()
