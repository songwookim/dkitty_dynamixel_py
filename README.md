- for use, you should refer config.yaml file and change dafault mode index(select above one)
-  for XM430 series
- Reference
    | https://emanual.robotis.com/docs/kr/faq/faq_dynamixel/
    | https://emanual.robotis.com/docs/kr/dxl/protocol2/
```
sudo chmod -R 777 /dev/ttyUSB0
```

### 1. Dynamixel Setting
```
set linux telecommunication speed
1) cat /sys/bus/usb-serial/devices/ttyUSB0/latency_timer
2) sudo vi /sys/bus/usb-serial/devices/ttyUSB0/latency_timer
   # change to 16 -> 1
3) cat /sys/bus/usb-serial/devices/ttyUSB0/latency_timer

# 1Mbps
3.160716789
3.359743268

# 57600
3.173044829
4.150020205

# 115200
3.115620801
3.708370134



```