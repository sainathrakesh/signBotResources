import pybullet as p
import numpy as np
import time
import json
import os

# Setup
p.connect(p.GUI)
p.setGravity(0, 0, -9.81)
dt = 1.0 / 240.0
p.setTimeStep(dt)

# load Poses
pose_path = os.path.join(os.path.dirname(__file__), "poses.json")
with open(pose_path, "r") as f:
    poses = json.load(f)

urdf_location = poses["URDF"]["location"]
# Load robot
start_pos = [0, 0, 1.1]
start_orientation = p.getQuaternionFromEuler([0, 0, 0])
robot = p.loadURDF(
    urdf_location,
    start_pos,
    start_orientation,
    useFixedBase=True
)

# Joint index mapping
joint_indices = {}
for i in range(p.getNumJoints(robot)):
    joint_name = p.getJointInfo(robot, i)[1].decode("utf-8")
    joint_indices[joint_name] = i

# Animation parameters
transition_duration = 0.2
hold_duration = 0.3
transition_frames = int(transition_duration / dt)
hold_frames = int(hold_duration / dt)

def interpolate(from_pose, to_pose):
    for t in range(transition_frames):
        alpha = t / transition_frames
        for name, idx in joint_indices.items():
            from_val = from_pose.get(name, 0.0)
            to_val = to_pose.get(name, 0.0)
            val = (1 - alpha) * from_val + alpha * to_val
            p.setJointMotorControl2(robot, idx, p.POSITION_CONTROL, targetPosition=val)
        p.stepSimulation()
        time.sleep(dt)

def hold(pose):
    for _ in range(hold_frames):
        for name, idx in joint_indices.items():
            p.setJointMotorControl2(robot, idx, p.POSITION_CONTROL, targetPosition=pose.get(name, 0.0))
        p.stepSimulation()
        time.sleep(dt)


#######################################################################################################################
###############################################    SIMULATION  ########################################################
#######################################################################################################################

pose_ja1 = poses["pose_ja1"]
pose_ja2 = poses["pose_ja2"]
pose_einverstanden_1 = poses["pose_einverstanden_1"]
pose_einverstanden_2 = poses["pose_einverstanden_2"]

neutral_pose = {name: 0.0 for name in joint_indices}

# ja
interpolate(neutral_pose, pose_ja1)
interpolate(pose_ja1, pose_ja2)
hold(pose_ja2)

# Go to base pose
interpolate(pose_ja2, pose_einverstanden_1)
hold(pose_einverstanden_1)

# Go to second pose
neutral_pose = {name: 0.0 for name in joint_indices}
interpolate(pose_einverstanden_1, pose_einverstanden_2)
hold(pose_einverstanden_2)


# Return to neutral
interpolate(pose_einverstanden_2, neutral_pose)
hold(neutral_pose)
