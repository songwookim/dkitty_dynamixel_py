"""Dynamixel communication speed test.

Measures time to send random position commands in rapid succession.
"""

import sys
import os
import time

import numpy as np
import hydra
from omegaconf import DictConfig

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from dynamixel_control import DynamixelControl


@hydra.main(version_base=None, config_path="..", config_name="config")
def main(cfg: DictConfig):
    N_ITERATIONS = 100

    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()

    try:
        start_time = time.process_time()
        for _ in range(N_ITERATIONS):
            positions = np.random.randint(0, 4096, size=len(cfg.dynamixel.ids)).tolist()
            controller.set_joint_positions(positions)
        elapsed = time.process_time() - start_time

        print(f"{N_ITERATIONS} iterations in {elapsed:.4f}s")
        print(f"Average: {elapsed / N_ITERATIONS * 1000:.2f}ms per command")
    finally:
        controller.close_port()


if __name__ == "__main__":
    main()
