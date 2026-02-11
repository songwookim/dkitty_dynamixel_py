# D'Kitty Dynamixel Controller (Python)

Dynamixel XM/XH430 시리즈 서보모터를 이용한 **D'Kitty 4족 로봇** 제어 패키지.  
Hydra 기반 설정 관리와 Dynamixel SDK를 사용하여 위치 제어 및 전류(토크) 제어를 지원합니다.

## 프로젝트 구조

```
dkitty_dynamixel_py/
├── dynamixel_control.py       # 핵심 모듈: DynamixelControl 클래스
├── config.yaml                # Hydra 설정 파일 (서보 ID, 통신, 제어 모드 등)
├── README.md
├── .gitignore
│
├── examples/                  # 예제 스크립트
│   ├── position_control_9dof.py   # 9관절 위치 제어
│   ├── position_control_3dof.py   # 3관절(1다리) 위치 제어
│   ├── force_control_9dof.py      # 9관절 전류(토크) 제어
│   ├── force_control_3dof.py      # 3관절 전류(토크) 제어
│   ├── current_mode_read.py       # 전류 모드에서 위치 읽기 루프
│   ├── pd_joint_control.py        # PD 관절 공간 토크 제어
│   ├── speed_test.py              # 통신 속도 테스트
│   ├── set_initial_pose.py        # 초기 자세 설정 (standalone)
│   ├── one_arm_trajectory.py      # 원숭이 궤적 재생 (standalone)
│   └── bulk_read.py               # Bulk Read 예제 (standalone)
│
├── assets/                    # MuJoCo 로봇 모델 (MJCF)
│   ├── dkitty/                # D'Kitty 모델
│   └── monkey/                # Monkey 모델
│
├── monkey/                    # 원숭이 궤적 데이터 및 MuJoCo 시뮬레이션
│   ├── data.csv
│   ├── get_data_test.py
│   ├── mujoco_2_dkitty.py
│   └── mujoco_2_monkey.py
│
├── mujoco222/                 # MuJoCo 시뮬레이션 테스트
│   ├── mujoco_test1.py
│   ├── mujoco_test2_viewer.py
│   └── mujoco_test3_gclaw.py
│
├── mjmodel.xml                # MuJoCo 모델 파일
└── outputs/                   # Hydra 실행 로그 (자동 생성, git 무시)
```

## 요구사항

- Python 3.8+
- [Dynamixel SDK](https://github.com/ROBOTIS-GIT/DynamixelSDK) (`pip install dynamixel-sdk`)
- [Hydra](https://hydra.cc/) (`pip install hydra-core`)
- NumPy (`pip install numpy`)
- (선택) MuJoCo / mujoco-py — 시뮬레이션용

```bash
pip install dynamixel-sdk hydra-core numpy
```

## 하드웨어 설정

### 1. USB 포트 권한 설정

```bash
sudo chmod 777 /dev/ttyUSB0
```

### 2. USB 시리얼 레이턴시 최적화

```bash
# 현재 값 확인
cat /sys/bus/usb-serial/devices/ttyUSB0/latency_timer

# 1ms로 변경 (기본값 16ms → 성능 향상)
echo 1 | sudo tee /sys/bus/usb-serial/devices/ttyUSB0/latency_timer

# 변경 확인
cat /sys/bus/usb-serial/devices/ttyUSB0/latency_timer
```

### 3. config.yaml 설정

`config.yaml`에서 사용할 서보 ID, 통신 포트, 제어 모드 등을 설정합니다:

```yaml
dynamixel:
  ids: [10, 11, 12, 20, 21, 22, 30, 31, 32]  # 서보 ID
  device_name: "/dev/ttyUSB0"                  # USB 포트
  baudrate: 1000000                            # 1Mbps
  control_modes:
    default_mode: 0   # 0: 전류 제어, 3: 위치 제어
  current:
    max_current: 10   # 전류 제한 (안전)
```

## 사용법

### 기본 사용

```python
import hydra
from omegaconf import DictConfig
from dynamixel_control import DynamixelControl

@hydra.main(version_base=None, config_path=".", config_name="config")
def main(cfg: DictConfig):
    controller = DynamixelControl(cfg.dynamixel)
    controller.connect()

    try:
        # 위치 읽기
        positions = controller.get_joint_positions()          # raw (0~4095)
        positions_deg = controller.get_joint_positions("deg") # degrees
        positions_rad = controller.get_joint_positions("rad") # radians

        # 속도 읽기
        velocities = controller.get_joint_velocities()

        # 위치 제어 (default_mode: 3)
        controller.set_joint_positions([1000, 1700, 2500, ...])

        # 전류 제어 (default_mode: 0)
        controller.set_goal_current([0, 2, 4, ...])

    finally:
        controller.close_port()
```

### 예제 실행

```bash
# 9관절 위치 제어
python examples/position_control_9dof.py

# 3관절 전류 제어
python examples/force_control_3dof.py

# PD 토크 제어
python examples/pd_joint_control.py

# 통신 속도 테스트
python examples/speed_test.py
```

## DynamixelControl API

| 메서드 | 설명 |
|--------|------|
| `connect()` | 포트 열기, 보레이트 설정, 운영 모드 설정, 토크 활성화 |
| `get_joint_positions(unit)` | 모든 서보 현재 위치 읽기 (`None`/`"deg"`/`"rad"`) |
| `get_joint_velocities()` | 모든 서보 현재 속도 읽기 |
| `set_joint_positions(goal_pos)` | 모든 서보 목표 위치 설정 (위치 제어 모드) |
| `set_goal_current(currents)` | 모든 서보 목표 전류 설정 (전류 제어 모드) |
| `set_goal_current_one(id, current)` | 단일 서보 목표 전류 설정 |
| `set_goal_currents(ids, currents)` | 특정 서보들의 목표 전류 설정 |
| `enable_torque()` / `disable_torque()` | 토크 활성/비활성화 |
| `set_operating_mode_all(mode)` | 모든 서보 운영 모드 변경 |
| `close_port()` | 토크 비활성화 후 포트 닫기 |

## 제어 모드

| 모드 | 값 | 설명 |
|------|---|------|
| 전류 제어 | 0 | 목표 전류(토크) 입력 |
| 속도 제어 | 1 | 목표 속도 입력 |
| 위치 제어 | 3 | 목표 위치 입력 (0~4095) |
| 확장 위치 제어 | 4 | 다중 회전 위치 제어 |
| 전류 기반 위치 제어 | 5 | 위치 + 전류 제한 |
| PWM 제어 | 16 | PWM 직접 제어 |

## 참고 자료

- [Dynamixel X 시리즈 e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xh430-w350/)
- [Dynamixel Protocol 2.0](https://emanual.robotis.com/docs/kr/dxl/protocol2/)
- [Dynamixel FAQ](https://emanual.robotis.com/docs/kr/faq/faq_dynamixel/)
- [Dynamixel SDK (Python)](https://github.com/ROBOTIS-GIT/DynamixelSDK)
- [Hydra Configuration](https://hydra.cc/)