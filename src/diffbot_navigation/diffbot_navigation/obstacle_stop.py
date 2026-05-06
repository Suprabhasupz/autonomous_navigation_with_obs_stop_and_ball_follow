#!/usr/bin/env python3

import numpy as np

import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge

from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from std_msgs.msg import Bool


class ObstacleStop(Node):

    def __init__(self):

        super().__init__('obstacle_stop')

        # Stop robot if obstacle is within 5 meters
        self.stop_distance = 5.0

        # Small center ROI only
        self.roi_width_ratio = 0.08
        self.roi_height_ratio = 0.08

        self.bridge = CvBridge()

        self.obstacle_detected = False

        # Depth image subscriber
        self.create_subscription(
            Image,
            '/depth_image',
            self.depth_callback,
            10
        )

        # Incoming velocity from planner
        self.create_subscription(
            Twist,
            '/cmd_vel_raw',
            self.cmd_callback,
            10
        )

        # Final velocity output
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Obstacle status
        self.bool_pub = self.create_publisher(
            Bool,
            '/obstacle_detected',
            10
        )

    def depth_callback(self, msg):

        try:

            depth = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='32FC1'
            )

        except Exception as e:

            self.get_logger().error(
                f'Depth conversion failed: {e}'
            )

            return

        h, w = depth.shape

        # Small center ROI
        roi_w = int(w * self.roi_width_ratio)
        roi_h = int(h * self.roi_height_ratio)

        x1 = (w - roi_w) // 2
        x2 = x1 + roi_w

        y1 = (h - roi_h) // 2
        y2 = y1 + roi_h

        roi = depth[y1:y2, x1:x2]

        # Ignore robot body and bad pixels
        valid = roi[
            np.isfinite(roi) &
            (roi > 2.0) &
            (roi < 15.0)
        ]

        detected = False

        if len(valid) > 20:

            # Nearest obstacle
            obstacle_distance = np.min(valid)

            self.get_logger().info(
                f'Obstacle distance: '
                f'{obstacle_distance:.2f} m'
            )

            # Stop if obstacle within 5m
            if obstacle_distance <= self.stop_distance:

                detected = True

                self.get_logger().warn(
                    'Obstacle detected — STOPPING'
                )

        self.obstacle_detected = detected

        msg_bool = Bool()
        msg_bool.data = detected

        self.bool_pub.publish(msg_bool)

    def cmd_callback(self, msg):

        # STOP ROBOT
        if self.obstacle_detected:

            stop = Twist()

            stop.linear.x = 0.0
            stop.angular.z = 0.0

            self.cmd_pub.publish(stop)

            return

        # Pass velocity normally
        self.cmd_pub.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = ObstacleStop()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':

    main()