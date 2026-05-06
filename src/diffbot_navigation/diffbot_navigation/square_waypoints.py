#!/usr/bin/env python3

import rclpy

from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path


class SquareWaypoints(Node):

    def __init__(self):

        super().__init__('square_waypoints')

        self.pub = self.create_publisher(
            Path,
            '/path',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_path
        )

    def publish_path(self):

        path = Path()

        path.header.frame_id = 'odom'

        points = [
            (2.0, 0.0),
            (6.0, 0.0),
            (6.0, 4.0),
            (2.0, 4.0),
            (2.0, 0.0)
        ]

        for x, y in points:

            pose = PoseStamped()

            pose.header.frame_id = 'odom'

            pose.pose.position.x = x
            pose.pose.position.y = y

            pose.pose.orientation.w = 1.0

            path.poses.append(pose)

        self.pub.publish(path)


def main(args=None):

    rclpy.init(args=args)

    node = SquareWaypoints()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()