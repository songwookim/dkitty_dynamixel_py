"""PD joint-space control using current (torque) mode.

Implements a simple PD controller to drive a single servo
to a goal position using current control mode.
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
    T = 100
    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()

    try:
        # PD gains
        kp = 0.5  # Nm/deg
        kd = 0.5  # Nm/(deg/s)

        goal_deg = 175
        goal_vel_deg = 0

        cur_deg = controller.get_joint_positions()
        cur_vel_deg = controller.get_joint_velocities()

        for i in range(T):
            e_deg = goal_deg - cur_deg
            ed_deg = goal_vel_deg - cur_vel_deg
            tau = e_deg * kp + ed_deg * kd
            tau = max(-10, min(10, tau))  # clamp torque

            os.system("clear")
            print(
                f"Step {i}: Goal={int(goal_deg)}, "
                f"Current={int(cur_deg)}, Error={int(e_deg)}, "
                f"Torque={int(tau)}, Velocity={int(cur_vel_deg)}"
            )

            controller.set_goal_current_one(cfg.dynamixel.ids[0], int(tau))
            time.sleep(0.1)

            cur_deg = controller.get_joint_positions()
            cur_vel_deg = controller.get_joint_velocities()

            if abs(cur_deg - goal_deg) <= 1:
                print("Goal reached")
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.close_port()


if __name__ == "__main__":
    main()
