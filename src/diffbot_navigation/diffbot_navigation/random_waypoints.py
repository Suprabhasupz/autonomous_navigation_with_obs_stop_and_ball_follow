#!/usr/bin/env python3

import random

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path


class RandomWaypoints(Node):

    def __init__(self):
        super().__init__('random_waypoints')

        self.pub = self.create_publisher(Path, '/path', 10)

        self.timer = self.create_timer(2.0, self.publish_path)

    def publish_path(self):

        path = Path()
        path.header.frame_id = 'odom'

        for _ in range(random.randint(5, 10)):

            pose = PoseStamped()
            pose.header.frame_id = 'odom'

            pose.pose.position.x = random.uniform(-5.0, 5.0)
            pose.pose.position.y = random.uniform(-5.0, 5.0)

            pose.pose.orientation.w = 1.0

            path.poses.append(pose)

        self.pub.publish(path)


def main(args=None):
    rclpy.init(args=args)
    node = RandomWaypoints()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()