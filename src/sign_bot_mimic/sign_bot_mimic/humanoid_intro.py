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

# call Poses
pose_hallo = poses["pose_hallo"]
pose_ich = poses["pose_ich"]
pose_4 = poses["pose_4"]
pose_n = poses["pose_n"]
pose_e = poses["pose_e"]
pose_1 = poses["pose_1"]
pose_wir_start = poses["pose_wir_start"]
pose_wir_2 = poses["pose_wir_2"]
pose_wir_3 = poses["pose_wir_3"]
pose_wir_end = poses["pose_wir_end"]
pose_arbeiten = poses["pose_arbeiten"]
pose_zusammen_1 = poses["pose_zusammen_1"]
pose_zusammen_2 = poses["pose_zusammen_2"]
pose_du = poses["pose_du"]
pose_und = poses["pose_und"]
pose_aber = poses["pose_aber"]
pose_nicht_1 = poses["pose_nicht_1"]
pose_nicht_2 = poses["pose_nicht_2"]
pose_gefährlich = poses["pose_gefährlich"]
pose_fabrik = poses["pose_fabrik"]
pose_industrie = poses["pose_industrie"]
pose_können_1 = poses["pose_können_1"]
pose_können_2 = poses["pose_können_2"]
pose_reinigen = poses["pose_reinigen"]
pose_prüfen = poses["pose_prüfen"]
pose_messen = poses["pose_messen"]
pose_mein = poses["pose_mein"]
pose_gehirn = poses["pose_gehirn"]
pose_computer = poses["pose_computer"]
pose_automobile = poses["pose_automobile"]
pose_mag_1 = poses["pose_mag_1"]
pose_mag_2 = poses["pose_mag_2"]
pose_polizei = poses["pose_polizei"]
pose_kennen = poses["pose_kennen"]
pose_leer_1 = poses["pose_leer_1"]
pose_leer_2 = poses["pose_leer_2"]
pose_batterie = poses["pose_batterie"]
pose_einstecken = poses["pose_einstecken"]
pose_bitte = poses["pose_bitte"]
pose_fertig = poses["pose_fertig"]
pose_ausschalten = poses["pose_ausschalten"]
pose_sie = poses["pose_sie"]
pose_verstehen = poses["pose_verstehen"]
pose_danke_1 = poses["pose_danke_1"]
pose_danke_2 = poses["pose_danke_2"]

# Oscillation pose ranges
arbeiten_elbow_values = [-2.0, -1.75] * 2
hallo_wrist_values = [-0.33, 0.33] * 2
aber_wrist_y_values = [-0.4, -0.23] * 2
gefährlich_shoulder_z_values = [-0.33, -0.39] * 2
industrie_left_shoulder_values = [0, 0.3] * 2
industrie_right_shoulder_values = [0.3, 0] * 2
reinigen_right_wrist_values = [0.26, -0.29] * 2
prüfen_right_shoulder_values = [-0.50, -0.30] * 2
gehirn_elbow_values = [-1.90, -1.78] * 2
automobile_left_shoulder = [-0.7, -1] * 2  # 10 total steps (5 full oscillations)
automobile_right_shoulder = [1, 0.7] * 2
kennen_right_wrist = [0.2, 0.6] * 2
batterie_right_wrist_values = [0.16, 1.3] * 2 
ausschalten_wrist_osc_ranges = {
    'right_wrist_x': (1.091, 0.000),
    'right_wrist_y': (0.033, 0.661),
    'right_wrist_z': (-0.728, 0.298)
}
verstehen_shoulder_z_range = (0.265, 0.364)
verstehen_wrist_z_range = (-0.893, 0.066)


# Animation parameters
transition_duration = 0.3
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

# Hallo
neutral_pose = {name: 0.0 for name in joint_indices}
interpolate(neutral_pose, pose_hallo)
hold(pose_hallo)

hallo_current_pose = pose_hallo.copy()
for val in hallo_wrist_values:
    next_pose = hallo_current_pose.copy()
    next_pose['right_wrist_y'] = val
    interpolate(hallo_current_pose, next_pose)
    hallo_current_pose = next_pose

# Ich
interpolate(hallo_current_pose, pose_ich)
hold(pose_ich)

# 4
interpolate(pose_ich, pose_4)
hold(pose_4)

# n
interpolate(pose_4, pose_n)
hold(pose_n)

# e
interpolate(pose_n, pose_e)
hold(pose_e)

# 1
interpolate(pose_e, pose_1)
hold(pose_1)

# Return to neutral
interpolate(pose_1, neutral_pose)
hold(neutral_pose)

# Wir_start
interpolate(neutral_pose, pose_wir_start)
#hold(pose_wir_start)

# Wir_2
interpolate(pose_wir_start, pose_wir_2)
#hold(pose_wir_2)

# Wir_3
interpolate(pose_wir_2, pose_wir_3)
#hold(pose_wir_3)

# Wir_end
interpolate(pose_wir_3, pose_wir_end)
hold(pose_wir_end)

# zusammen_1
interpolate(pose_wir_end, pose_zusammen_1)
hold(pose_zusammen_1)

# zusammen_2
interpolate(pose_zusammen_1, pose_zusammen_2)
hold(pose_zusammen_2)

# arbeiten
interpolate(pose_zusammen_2, pose_arbeiten)
hold(pose_arbeiten)

arbeiten_current_pose = pose_arbeiten.copy()
for val in arbeiten_elbow_values:
    next_pose = arbeiten_current_pose.copy()
    next_pose['right_elbow'] = val
    interpolate(arbeiten_current_pose, next_pose)
    arbeiten_current_pose = next_pose
    
# du
interpolate(arbeiten_current_pose, pose_du)
hold(pose_du)

# und
interpolate(pose_du, pose_und)
hold(pose_und)

# ich
interpolate(pose_und, pose_ich)
hold(pose_ich)

# Return to neutral
interpolate(pose_ich, neutral_pose)
hold(neutral_pose)

# Aber
interpolate(neutral_pose, pose_aber)
hold(pose_aber)

aber_current_pose = pose_aber.copy()
for val in aber_wrist_y_values:
    next_pose = aber_current_pose.copy()
    next_pose['right_shoulder_y'] = val
    interpolate(aber_current_pose, next_pose)
    aber_current_pose = next_pose

# ich
interpolate(pose_aber, pose_ich)
hold(pose_ich)

# gefährlich
interpolate(pose_ich, pose_gefährlich)
hold(pose_gefährlich)

gefährlich_current_pose = pose_gefährlich.copy()
for val in gefährlich_shoulder_z_values:
    next_pose = gefährlich_current_pose.copy()
    next_pose['right_shoulder_z'] = -1*val
    next_pose['left_shoulder_z'] = val
    interpolate(gefährlich_current_pose, next_pose)
    gefährlich_current_pose = next_pose

# nicht start
interpolate(gefährlich_current_pose, pose_nicht_1)
hold(pose_nicht_1)

# nicht end
interpolate(pose_nicht_1, pose_nicht_2)
hold(pose_nicht_2)

# Return to neutral
interpolate(pose_nicht_2, neutral_pose)
hold(neutral_pose)

# ich
interpolate(neutral_pose, pose_ich)
hold(pose_ich)

# Return to neutral
interpolate(pose_ich, neutral_pose)
hold(neutral_pose)

# Fabrik
interpolate(neutral_pose, pose_fabrik)
hold(pose_fabrik)

# industrie
interpolate(pose_fabrik, pose_industrie)
hold(pose_industrie)

industrie_current_pose = pose_industrie.copy()
for i in range(6):
    left = industrie_left_shoulder_values[i%2]
    right = industrie_right_shoulder_values[i%2]
    next_pose = industrie_current_pose.copy()
    next_pose['left_shoulder_y'] = left
    next_pose['right_shoulder_y'] = right
    interpolate(industrie_current_pose, next_pose)
    hold(next_pose)
    industrie_current_pose = next_pose

# arbeiten
interpolate(industrie_current_pose, pose_arbeiten)
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

# ich
interpolate(neutral_pose, pose_ich)
hold(pose_ich)

# Prüfen
interpolate(pose_ich, pose_prüfen)
hold(pose_prüfen)

prüfen_current_pose = pose_prüfen.copy()
for val in prüfen_right_shoulder_values:
    next_pose = prüfen_current_pose.copy()
    next_pose['right_shoulder_x'] = val
    interpolate(prüfen_current_pose, next_pose)
    prüfen_current_pose = next_pose

# Return to neutral
interpolate(prüfen_current_pose, neutral_pose)
hold(neutral_pose)

# Reinigen
interpolate(neutral_pose, pose_reinigen)
hold(pose_reinigen)

reinigen_current_pose = pose_reinigen.copy()
for val in reinigen_right_wrist_values:
    next_pose = reinigen_current_pose.copy()
    next_pose['right_wrist_y'] = val
    interpolate(reinigen_current_pose, next_pose)
    reinigen_current_pose = next_pose

# Return to neutral
interpolate(reinigen_current_pose, neutral_pose)
hold(neutral_pose)

# Messen
interpolate(neutral_pose, pose_messen)
hold(pose_messen)

# können 1
interpolate(pose_messen, pose_können_1)
hold(pose_können_1)

# können 2
interpolate(pose_können_1, pose_können_2)
hold(pose_können_2)

# Return to neutral
interpolate(pose_können_2, neutral_pose)
hold(neutral_pose)

# Mein
interpolate(neutral_pose, pose_mein)
hold(pose_mein)

# gehirn
interpolate(pose_mein, pose_gehirn)
hold(pose_gehirn)

gehirn_current_pose = pose_gehirn.copy()
for val in gehirn_elbow_values:
    next_pose = gehirn_current_pose.copy()
    next_pose['right_elbow'] = val
    interpolate(gehirn_current_pose, next_pose)
    gehirn_current_pose = next_pose

# computer
interpolate(pose_gehirn, pose_computer)
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
    
# Return to neutral
interpolate(current, neutral_pose)
hold(neutral_pose)

# ich
interpolate(neutral_pose, pose_ich)
hold(pose_ich)

# Automobile
interpolate(neutral_pose, pose_automobile)
hold(pose_automobile)

# Automobile animation
auto_current_pose = pose_automobile.copy()
for i in range(3):
    left = automobile_left_shoulder[i%2]
    right = automobile_right_shoulder[i%2]
    next_pose = auto_current_pose.copy()
    next_pose['left_shoulder_z'] = left
    next_pose['right_shoulder_z'] = right
    interpolate(auto_current_pose, next_pose)
    hold(next_pose)
    auto_current_pose = next_pose

# Moegen start
interpolate(auto_current_pose, pose_mag_1)
hold(pose_mag_1)

# Moegen end
interpolate(pose_mag_1, pose_mag_2)
hold(pose_mag_2)

# ich
interpolate(pose_mag_2, pose_ich)
hold(pose_ich)

# Polizei
interpolate(pose_ich, pose_polizei)
hold(pose_polizei)

# kennen
interpolate(pose_polizei, pose_kennen)
hold(pose_kennen)

kennen_current_pose = pose_kennen.copy()
for val in kennen_right_wrist:
    next_pose = kennen_current_pose.copy()
    next_pose['right_wrist_x'] = val
    interpolate(kennen_current_pose, next_pose)
    kennen_current_pose = next_pose

# Return to neutral
interpolate(kennen_current_pose, neutral_pose)
hold(neutral_pose)

# ich
interpolate(neutral_pose, pose_ich)
hold(pose_ich)

# leer
interpolate(pose_ich, pose_leer_1)
hold(pose_leer_1)

interpolate(pose_leer_1, pose_leer_2)
hold(pose_leer_2)

# batterie
interpolate(pose_leer_2, pose_batterie)
hold(pose_batterie)

# batterie animation
batterie_current_pose = pose_batterie.copy()
for i in range(5):
    right = batterie_right_wrist_values[i%2]
    next_pose = batterie_current_pose.copy()
    next_pose['right_wrist_z'] = right
    interpolate(batterie_current_pose, next_pose)
    hold(next_pose)
    batterie_current_pose = next_pose

# einstecken
interpolate(batterie_current_pose, pose_einstecken)
hold(pose_einstecken)

# Return to neutral
interpolate(pose_einstecken, neutral_pose)
hold(neutral_pose)

# bitte
interpolate(neutral_pose, pose_bitte)
hold(pose_bitte)

# Return to neutral
interpolate(pose_bitte, neutral_pose)
hold(neutral_pose)

# ich
interpolate(neutral_pose, pose_ich)
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


# du
interpolate(pose_fertig, pose_du)
hold(pose_du)

# mich
interpolate(pose_du, pose_ich)
hold(pose_ich)

#ausschalten
interpolate(pose_ich, pose_ausschalten)
hold(pose_ausschalten)

# ausschalten animation
ausschalten_current_pose = pose_ausschalten.copy()
for i in range(2):
    # Swap wrist values
    next_pose = ausschalten_current_pose.copy()
    for joint, (v1, v2) in ausschalten_wrist_osc_ranges.items():
        current_val = ausschalten_current_pose.get(joint, 0.0)
        next_pose[joint] = v2 if np.isclose(current_val, v1, atol=0.01) else v1

    interpolate(ausschalten_current_pose, next_pose)
    hold(next_pose)
    ausschalten_current_pose = next_pose

# können 1
interpolate(ausschalten_current_pose, pose_können_1)
hold(pose_können_1)

# können 2
interpolate(pose_können_1, pose_können_2)
hold(pose_können_2)

# Return to neutral
interpolate(pose_können_2, neutral_pose)
hold(neutral_pose)

# sie
interpolate(neutral_pose, pose_sie)
hold(pose_sie)

# verstehen
interpolate(pose_sie, pose_verstehen)
hold(pose_verstehen)

# verstehen animation
shoulder_z_range = (0.265, 0.364)
wrist_z_range = (-0.893, 0.066)
verstehen_current_pose = pose_verstehen.copy()
for i in range(4):
    next_pose = verstehen_current_pose.copy()

    # Toggle values
    next_pose['right_shoulder_z'] = (
        shoulder_z_range[1] if np.isclose(verstehen_current_pose['right_shoulder_z'], shoulder_z_range[0], atol=0.01)
        else shoulder_z_range[0]
    )
    next_pose['right_wrist_z'] = (
        wrist_z_range[1] if np.isclose(verstehen_current_pose['right_wrist_z'], wrist_z_range[0], atol=0.01)
        else wrist_z_range[0]
    )

    interpolate(verstehen_current_pose, next_pose)
    hold(next_pose)
    verstehen_current_pose = next_pose


# Return to neutral
interpolate(verstehen_current_pose, neutral_pose)
hold(neutral_pose)

# wenn nicht - bitte sagen sie mir

# danke start
interpolate(neutral_pose, pose_danke_1)
hold(pose_danke_1)

# danke end
interpolate(pose_danke_1, pose_danke_2)
hold(pose_danke_2)
