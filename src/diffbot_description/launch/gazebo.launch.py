import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution

from launch_ros.actions import Node


def generate_launch_description():

    # ------------------------------------------------
    # PACKAGES
    # ------------------------------------------------
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")

    pkg_project_description = get_package_share_directory(
        "diffbot_description"
    )

    # ------------------------------------------------
    # FILE PATHS
    # ------------------------------------------------

    # SDF robot
    sdf_file = os.path.join(
        pkg_project_description,
        "urdf",
        "r1_eval.sdf"
    )

    # RViz config
    rviz_config = os.path.join(
        pkg_project_description,
        "rviz",
        "rviz.rviz"
    )

    # Bridge config
    bridge_config = os.path.join(
        pkg_project_description,
        "config",
        "ros_gz_bridge.yaml"
    )

    # URDF (only for RViz TF visualization)
    urdf_file = os.path.join(
        pkg_project_description,
        "urdf",
        "r1_eval.urdf"
    )

    # World
    world_file = PathJoinSubstitution([
        pkg_project_description,
        "worlds",
        "empty.sdf"
    ])

    # ------------------------------------------------
    # LOAD URDF
    # ------------------------------------------------
    with open(urdf_file, "r") as infp:
        robot_desc = infp.read()

    # ------------------------------------------------
    # GAZEBO
    # ------------------------------------------------
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_ros_gz_sim,
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={
            "gz_args": world_file
        }.items(),
    )

    # ------------------------------------------------
    # SPAWN ROBOT
    # ------------------------------------------------
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "fr_robot_sim_r1",
            "-file", sdf_file,
            "-x", "0",
            "-y", "0",
            "-z", "0.2"
        ],
        output="screen",
    )

    # ------------------------------------------------
    # ROBOT STATE PUBLISHER
    # ------------------------------------------------
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_desc,
                "use_sim_time": True
            }
        ],
        output="screen",
    )

    # ------------------------------------------------
    # JOINT STATE PUBLISHER
    # ------------------------------------------------
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[
            {
                "use_sim_time": True
            }
        ],
        output="screen",
    )

    # ------------------------------------------------
    # ROS <-> GAZEBO BRIDGE
    # ------------------------------------------------
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[
            {
                "config_file": bridge_config
            }
        ],
        output="screen",
    )

    # ------------------------------------------------
    # RVIZ
    # ------------------------------------------------
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=[
            "-d",
            rviz_config
        ],
        output="screen",
    )

    # ------------------------------------------------
    # FINAL LAUNCH
    # ------------------------------------------------
    return LaunchDescription([
        gz_sim,
        spawn_robot,
        robot_state_publisher,
        joint_state_publisher,
        bridge,
        rviz_node
    ])