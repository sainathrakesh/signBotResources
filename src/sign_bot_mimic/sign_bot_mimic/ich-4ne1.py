import pybullet as p
import numpy as np
import time
import os

# Connect to PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)
dt = 1.0 / 240.0  # Use higher framerate for smooth animation
p.setTimeStep(dt)

# Load robot
startPos = np.array([0, 0, 1.1])
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
robot = p.loadURDF("/home/pepper/sign_bot_neura_challenge/src/4ne1_gamma_revc_urdf/4ne1_g-10000_primitiv-kinematic_rev.C/urdf/4ne1_g-10000_primitiv-kinematic_rev.C.urdf", startPos, startOrientation, useFixedBase=True)

# Get joint indices
joint_indices = {}
for i in range(p.getNumJoints(robot)):
    joint_name = p.getJointInfo(robot, i)[1].decode('utf-8')
    joint_indices[joint_name] = i

# Define poses
pose_ich = {     'right_shoulder_y': -0.75,
    'right_shoulder_x': -0.45,
    'right_shoulder_z': 1.25,
    'right_elbow': -2.00,
    'right_wrist_z': -0.75,
    'right_wrist_y': -0.75,
    'right_wrist_x': 0.5,
    'right_thumb_1_joint': 0.75,
    'right_thumb_2_joint': 2.00,
    'right_thumb_3_joint': 1.5,
    'right_index_1_joint': 1.0,
    'right_index_2_joint': -0.1,
    'right_middle_1_joint': 1.5,
    'right_middle_2_joint': 1.5,
    'right_ring_1_joint': 1.3,
    'right_ring_2_joint': 1.5,
    'right_little_1_joint': 1.5,
    'right_little_2_joint': 1.5 }
pose_4   = {     'right_shoulder_y': -0.5,
    'right_shoulder_x': -0.5,
    'right_shoulder_z': 1.25,
    'right_elbow': -1.5,
    'right_wrist_z': -0.5,
    'right_wrist_y': -0.5,
    'right_thumb_1_joint': 1.0,
    'right_thumb_2_joint': 0.5,
    'right_thumb_3_joint': 1.0,
    'right_thumb_4_joint': 2.0 }
pose_n   = {     'right_elbow': -2.0,
    'right_wrist_z': 1.25,
    'right_wrist_x': -0.5,
    'right_thumb_1_joint': 0.25,
    'right_thumb_2_joint': 0.5,
    'right_thumb_3_joint': 1.0,
    'right_thumb_4_joint': 0.5,
    'right_index_1_joint': 1.5,
    'right_middle_1_joint': 1.5,
    'right_ring_1_joint': 1.5,
    'right_ring_2_joint': 1.5,
    'right_little_1_joint': 1.5,
    'right_little_2_joint': 2.0 }
pose_e   = {     'right_shoulder_x': -0.15,
    'right_elbow': -2.0,
    'right_wrist_z': 1.0,
    'right_wrist_x': -1.0,
    'right_thumb_2_joint': 0.5,
    'right_thumb_3_joint': 1.25,
    'right_thumb_4_joint': 0.75,
    'right_index_2_joint': 1.75,
    'right_middle_2_joint': 1.75,
    'right_ring_2_joint': 1.75,
    'right_little_2_joint': 1.75 }
pose_1   = {     'right_elbow': -2.00,
    'right_index_1_joint': 1.5,
    'right_index_2_joint': 1.5,
    'right_middle_1_joint': 1.5,
    'right_middle_2_joint': 1.5,
    'right_ring_1_joint': 1.5,
    'right_ring_2_joint': 1.5,
    'right_little_1_joint': 1.5,
    'right_little_2_joint': 1.5 }

# Sequence of signs
poses = [pose_ich, pose_4, pose_n, pose_e, pose_1]

# Animation config
transition_duration = 0.75  # seconds
hold_duration = 0.5         # seconds
transition_frames = int(transition_duration / dt)
hold_frames = int(hold_duration / dt)

# Animation helpers
def interpolate_between(from_pose, to_pose):
    for t in range(transition_frames):
        alpha = t / transition_frames
        for name, idx in joint_indices.items():
            from_val = from_pose.get(name, 0.0)
            to_val = to_pose.get(name, 0.0)
            value = (1 - alpha) * from_val + alpha * to_val
            p.setJointMotorControl2(robot, idx, p.POSITION_CONTROL, targetPosition=value)
        p.stepSimulation()
        time.sleep(dt)

def hold_pose(pose):
    for _ in range(hold_frames):
        for name, idx in joint_indices.items():
            value = pose.get(name, 0.0)
            p.setJointMotorControl2(robot, idx, p.POSITION_CONTROL, targetPosition=value)
        p.stepSimulation()
        time.sleep(dt)

# Animate sentence "Ich bin 4NE1"
while True:
    # Start from neutral
    current_pose = {name: 0.0 for name in joint_indices.keys()}

    for next_pose in poses:
        interpolate_between(current_pose, next_pose)
        hold_pose(next_pose)
        current_pose = next_pose  # continue from this pose

    # At the end, return to neutral
    neutral_pose = {name: 0.0 for name in joint_indices.keys()}
    interpolate_between(current_pose, neutral_pose)
    hold_pose(neutral_pose)
