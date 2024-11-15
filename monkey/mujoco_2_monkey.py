# ref1 : https://mujoco.readthedocs.io/en/2.2.0/programming.html  (mujoco222 install)
# ref2 : https://github.com/vikashplus/robel_sim/tree/9d774735f5d6a599774d01d8808f411054f8cf28/dclaw (dclaw mujoco200)
# ref3 : export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libGLEW.so   << add must be add
import mujoco_py
import math
import os

mj_path = mujoco_py.utils.discover_mujoco()
mj_path = mj_path+'/model/robel_sim/monkey/kitty-v2.1.xml'
xml_path = os.path.join(mj_path)
model = mujoco_py.load_model_from_path(xml_path)
sim = mujoco_py.MjSim(model)
mjstate = mujoco_py.MjSimState
viewer = mujoco_py.MjViewer(sim)
t= 0

 

# data
import csv
import os
import numpy as np
import time

datas = list()

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "data.csv"
abs_file_path = os.path.join(script_dir, rel_path)
f = open(abs_file_path,'r')
rea = csv.reader(f)
for row in rea:
    row = [float(i) for i in row]
    row[0:7:2] = np.subtract(row[0:7:2], np.pi/2)
    datas.append(row)
f.close


# these ID must be remapped to real dynamixel ID
# ctrl value's unit is degree and dynamixel rotate 2000 -> = 0 degree

# sim's degree range is 1.57
i = 0
while True:  
    # for idx, data in enumerate(datas) :
    # sim.data.body_xpos = [0 0 10]

    data = datas[i] 
    sim.data.ctrl[0] = 0   # actuator ID 10 
    sim.data.ctrl[1] = data[6]                         # actuator ID 11``
    sim.data.ctrl[2] = data[7]                         # actuator ID 12
    sim.data.ctrl[3] = np.pi/2                         # actuator ID 12

    sim.data.ctrl[4] = 0   # actuator ID 21      # actuator ID 20  (actuqcwactor degree which is abs(45) bounded by .mjcf)
    sim.data.ctrl[5] = data[3]  # actuator ID 22
    sim.data.ctrl[6] = data[2]                         # actuator ID 12
    sim.data.ctrl[7] = np.pi/2                         # actuator ID 12

    sim.data.ctrl[8] = 0 # actuator ID 30
    sim.data.ctrl[9] =  data[4]   # actuator ID 31
    sim.data.ctrl[10] = data[5]   # actuator ID 32
    sim.data.ctrl[11] = np.pi/2                         # actuator ID 12

    sim.data.ctrl[12] = 0          # actuator ID 40
    sim.data.ctrl[13] = data[0]    # actuator ID 41
    sim.data.ctrl[14] = data[1]    # actuator ID 42
    sim.data.ctrl[15] = np.pi/2    # actuator ID 12
    if(t%100==0):
        i+=1
    t += 1
    sim.step(t)
        
    viewer.render()
    if t > 100 and os.getenv('TESTING') is not None:
        break
    if len(datas) <= i:
        break
#print(sim.data.qpos)