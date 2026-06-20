# This simple script load humanoid.urdf and creates a slider for each joint. It also prints a list of all joint names, including the fixed joints.
# Pybullet is used for visualization

import pybullet as p
import numpy as np
import time

physicsClient = p.connect(p.GUI)#or p.DIRECT for non-graphical version
p.setGravity(0,0,-9.81)
dt = 1.0 / 1000.0
p.setTimeStep(dt)

startPos = np.array([0,0,1.1])
startOrientation = p.getQuaternionFromEuler([0,0,0])
robot = p.loadURDF("urdf/4ne1_g-10000_primitiv-kinematic_rev.C.urdf",startPos, startOrientation, useFixedBase=True)

num_joints = p.getNumJoints(robot)
# Now we can create a slider for each joint
sliders = []
for joint_index in range(num_joints):
    joint_info = p.getJointInfo(robot, joint_index)
    joint_name = joint_info[1].decode("utf-8")
    sliders.append(p.addUserDebugParameter(joint_name, -np.pi, np.pi, 0))
# We can also print all joint names
for joint_index in range(num_joints):
    joint_info = p.getJointInfo(robot, joint_index)
    print(joint_info[1])

# Now simulate the robot and use pd control mode to set all joint angles to the slider values
while True:
    p.stepSimulation()
    for joint_index, slider in enumerate(sliders):
        joint_info = p.getJointInfo(robot, joint_index)
        joint_name = joint_info[1].decode("utf-8")
        joint_angle = p.readUserDebugParameter(slider)
        p.setJointMotorControl2(robot, joint_index, p.POSITION_CONTROL, targetPosition=joint_angle)
    time.sleep(dt)
