# ref : https://github.com/openai/mujoco-py/blob/master/examples/body_interaction.py
# ref2 : https://www.freecodecamp.org/news/how-to-set-an-environment-variable-in-linux/ (set path Variable export..)
# error -> Missing GL GLEW  
# pip freeze | xargs pip uninstall -y
# >> https://talkingaboutme.tistory.com/entry/RL-mujocopy-ERROR-GLEW-initalization-error-Missing-GL-version


import mujoco_py
import os


from threading import Lock
# reload_package(mujoco_py)
mj_path = mujoco_py.utils.discover_mujoco() # ./bin/simulate ./model/humanoid.xml
mj_path = mj_path+'/model/humanoid.xml'
xml_path = os.path.join(mj_path)
model = mujoco_py.load_model_from_path(xml_path)

sim = mujoco_py.MjSim(model)
viewer = mujoco_py.MjViewer(sim)
t= 0
while True :
    sim.step()
    viewer.render()
viewer.close()