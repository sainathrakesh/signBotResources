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


pose_ich = poses["pose_ich"]
pose_computer = poses["pose_computer"]
pose_arbeiten = poses["pose_arbeiten"]
arbeiten_elbow_values = [-2.0, -1.75] * 2

neutral_pose = {name: 0.0 for name in joint_indices}

# Ich
interpolate(neutral_pose, pose_ich)
hold(pose_ich)

# computer
interpolate(pose_ich, pose_computer)
hold(pose_computer)

osc_max = 0.5
osc_min = 0.0

right_fingers_alt = [
    ['right_index_1_joint', 'right_ring_1_joint'],
    ['right_middle_1_joint', 'right_little_1_joint']
]

left_fingers_alt = [
    ['left_middle_1_joint', 'left_little_1_joint'],
    ['left_index_1_joint', 'left_ring_1_joint']
]

current = pose_computer.copy()
for i in range(5):
    next_pose = current.copy()

    # Set alternating finger groups
    r_group = right_fingers_alt[i % 2]
    l_group = left_fingers_alt[i % 2]

    # Right hand oscillation
    for joint in r_group:
        next_pose[joint] = osc_max if current[joint] == osc_min else osc_min

    # Left hand oscillation
    for joint in l_group:
        next_pose[joint] = osc_max if current[joint] == osc_min else osc_min

    interpolate(current, next_pose)
    hold(next_pose)
    current = next_pose
    

# arbeiten
interpolate(current, pose_arbeiten)
hold(pose_arbeiten)

arbeiten_current_pose = pose_arbeiten.copy()
for val in arbeiten_elbow_values:
    next_pose = arbeiten_current_pose.copy()
    next_pose['right_elbow'] = val
    interpolate(arbeiten_current_pose, next_pose)
    arbeiten_current_pose = next_pose

# Return to neutral
interpolate(arbeiten_current_pose, neutral_pose)
hold(neutral_pose)
