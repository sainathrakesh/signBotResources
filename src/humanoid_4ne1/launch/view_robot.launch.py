import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue



def generate_launch_description():
    pkg_share = FindPackageShare('humanoid_4ne1')

    # Default file paths
    default_urdf_path = PathJoinSubstitution([
        pkg_share, 'urdf', 'neura_4ne1_g3.urdf'
    ])

    default_rviz_config_path = PathJoinSubstitution([
        pkg_share, 'rviz', 'default.rviz'
    ])

    # Launch configurations
    urdf_model = LaunchConfiguration('urdf_model')
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    use_gui = LaunchConfiguration('gui')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')

    # Declare launch arguments
    return LaunchDescription([

        DeclareLaunchArgument(
            name='urdf_model',
            default_value=default_urdf_path,
            description='Absolute path to robot URDF file'
        ),

        DeclareLaunchArgument(
            name='rviz_config_file',
            default_value=default_rviz_config_path,
            description='Full path to the RViz config file to use'
        ),

        DeclareLaunchArgument(
            name='gui',
            default_value='True',
            description='Flag to enable joint_state_publisher_gui'
        ),

        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='True',
            description='Use simulation clock if true'
        ),

        DeclareLaunchArgument(
            name='use_rviz',
            default_value='True',
            description='Whether to start RViz'
        ),

        DeclareLaunchArgument(
            name='use_robot_state_pub',
            default_value='True',
            description='Whether to start robot_state_publisher'
        ),

        # Joint State Publisher
        Node(
            condition=UnlessCondition(use_gui),
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen'
        ),

        # Joint State Publisher GUI
        Node(
            condition=IfCondition(use_gui),
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),

        # Robot State Publisher
        Node(
            condition=IfCondition(use_robot_state_pub),
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': ParameterValue(Command(['cat ', urdf_model]), value_type=str)
            }]
        ),

        # RViz
        Node(
            condition=IfCondition(use_rviz),
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_file],
            output='screen'
        )
    ])
