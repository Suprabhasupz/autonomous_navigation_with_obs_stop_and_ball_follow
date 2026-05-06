from launch import LaunchDescription
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    pkg_share = get_package_share_directory('diffbot_navigation')

    params = os.path.join(
        pkg_share,
        'config',
        'params.yaml'
    )

    return LaunchDescription([

        Node(
            package='diffbot_navigation',
            executable='path_follower',
            name='path_follower',
            parameters=[params],
            output='screen'
        ),

        Node(
            package='diffbot_navigation',
            executable='obstacle_stop',
            name='obstacle_stop',
            parameters=[params],
            output='screen'
        ),

        Node(
            package='diffbot_navigation',
            executable='square_waypoints',
            name='square_waypoints',
            output='screen'
        )
    ])