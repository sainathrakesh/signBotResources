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
pose_ja1 = poses["pose_ja1"]
pose_ja2 = poses["pose_ja2"]
pose_fertig = poses["pose_fertig"]

neutral_pose = {name: 0.0 for name in joint_indices}

# ja
interpolate(neutral_pose, pose_ja1)
interpolate(pose_ja1, pose_ja2)
hold(pose_ja2)

# Ich
interpolate(pose_ja2, pose_ich)
hold(pose_ich)

# fertig
interpolate(pose_ich, pose_fertig)
hold(pose_fertig)

#fertig animation
fertig_elbow_start = -1.587
fertig_elbow_end = -2.000
fertig_current_pose = pose_fertig.copy()
for i in range(1):
    # Bend elbow to -2.000
    next_pose = fertig_current_pose.copy()
    next_pose['right_elbow'] = fertig_elbow_end
    interpolate(fertig_current_pose, next_pose)
    hold(next_pose)

    # Return elbow to -1.587
    back_pose = next_pose.copy()
    back_pose['right_elbow'] = fertig_elbow_start
    interpolate(next_pose, back_pose)
    hold(back_pose)

    fertig_current_pose = back_pose



# Return to neutral
interpolate(fertig_current_pose, neutral_pose)
hold(neutral_pose)
