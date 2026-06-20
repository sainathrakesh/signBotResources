import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import yaml
import os
from ament_index_python.packages import get_package_share_directory

class SignJointPublisher(Node):
    def __init__(self):
        super().__init__('sign_joint_publisher')
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)

        # List of all joints used in your signs
        full_joint_names = self.joint_names + [
            'left_shoulder_y', 'left_shoulder_x', 'left_shoulder_z', 'left_elbow',
            'left_wrist_z', 'left_wrist_y', 'left_wrist_x',
            'torso_z', 'torso_x', 'torso_y', 'head_z', 'head_x', 'head_y',
            'left_hip_y', 'left_hip_x', 'left_hip_z', 'left_knee', 'left_ankle_y', 'left_ankle_x',
            'right_hip_y', 'right_hip_x', 'right_hip_z', 'right_knee', 'right_ankle_y', 'right_ankle_x'
        ]
        msg = JointState()
        msg.name = full_joint_names
        msg.position = [self.current_pose.get(j, 0.0) for j in full_joint_names]


        # Load poses from installed share path
        pose_file = os.path.join(
            get_package_share_directory('sign_bot_publisher'),
            'config', 'sign_poses.yaml'
        )
        with open(pose_file, 'r') as f:
            self.sign_poses = yaml.safe_load(f)

        # Define the sign sequence here
        self.sign_sequence = ['ich']
        self.pose_index = 0

        # Set timing
        self.transition_time = 1.0   # seconds
        self.hold_time = 0.5         # seconds
        self.dt = 1.0 / 100.0        # 100 Hz
        self.transition_steps = int(self.transition_time / self.dt)
        self.hold_steps = int(self.hold_time / self.dt)

        # Initialize state
        self.current_pose = {name: 0.0 for name in self.joint_names}
        self.next_pose = self.sign_poses[self.sign_sequence[self.pose_index]]
        self.t_step = 0
        self.phase = 'transition'
        self.hold_counter = 0

        self.timer = self.create_timer(self.dt, self.update)

    def update(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names

        if self.phase == 'transition':
            alpha = self.t_step / self.transition_steps
            position = [
                (1 - alpha) * self.current_pose.get(j, 0.0) + alpha * self.next_pose.get(j, 0.0)
                for j in self.joint_names
            ]
            self.t_step += 1
            if self.t_step >= self.transition_steps:
                self.phase = 'hold'
                self.t_step = 0
                self.current_pose = self.next_pose.copy()
        elif self.phase == 'hold':
            position = [self.current_pose.get(j, 0.0) for j in self.joint_names]
            self.hold_counter += 1
            if self.hold_counter >= self.hold_steps:
                self.pose_index += 1
                if self.pose_index < len(self.sign_sequence):
                    self.next_pose = self.sign_poses[self.sign_sequence[self.pose_index]]
                    self.phase = 'transition'
                    self.t_step = 0
                    self.hold_counter = 0
                else:
                    self.get_logger().info("Finished all signs.")
                    self.destroy_node()
                    rclpy.shutdown()
                    return
        else:
            position = [0.0] * len(self.joint_names)

        msg.position = position
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SignJointPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
