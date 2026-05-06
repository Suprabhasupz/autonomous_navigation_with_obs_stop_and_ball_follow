import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    package_name = "diffbot_description"
    pkg_share = get_package_share_directory(package_name)

    # -------------------------
    # 🔥 Fix mesh loading (IMPORTANT)
    # -------------------------
    resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=pkg_share
    )

    # -------------------------
    # Gazebo (Ignition)
    # -------------------------
    world_file = os.path.join(
        pkg_share,
        "worlds",
        "industrial-warehouse.sdf"   # ✅ your correct world
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={
            "gz_args": world_file
        }.items()
    )

    # -------------------------
    # Spawn robot (SDF)
    # -------------------------
    sdf_file = os.path.join(
        pkg_share,
        "urdf",      # your SDF location
        "r1_eval.sdf"
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-file", sdf_file,
            "-name", "diffbot",
            "-x", "0",
            "-y", "0",
            "-z", "0.2"
        ],
        output="screen"
    )

    # -------------------------
    # ROS <-> Gazebo Bridge
    # -------------------------
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock"
        ],
        output="screen"
    )

    # -------------------------
    # RViz (URDF required)
    # -------------------------
    urdf_file = os.path.join(
        pkg_share,
        "urdf",
        "r1_eval.urdf"
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description": open(urdf_file).read(),
            "use_sim_time": True
        }]
    )

    rviz_config = os.path.join(
        pkg_share,
        "rviz",
        "view.rviz"
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        output="screen"
    )

    # -------------------------
    # Launch
    # -------------------------
    return LaunchDescription([
        resource_path,
        gazebo,
        spawn_robot,
        bridge,
        robot_state_publisher,
        rviz
    ])