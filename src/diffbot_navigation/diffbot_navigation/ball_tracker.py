#!/usr/bin/env python3

import cv2
import math
import numpy as np

import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge

from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PointStamped

import tf2_ros
from tf2_geometry_msgs import do_transform_point


class BallTracker(Node):

    def __init__(self):

        super().__init__('ball_tracker')

        self.bridge = CvBridge()

        self.rgb_image = None
        self.depth_image = None

        self.fx = None
        self.fy = None
        self.cx = None
        self.cy = None

        self.create_subscription(
            Image,
            '/camera',
            self.rgb_callback,
            10
        )

        self.create_subscription(
            Image,
            '/depth_image',
            self.depth_callback,
            10
        )

        self.create_subscription(
            CameraInfo,
            '/camera_info',
            self.camera_info_callback,
            10
        )

        self.path_pub = self.create_publisher(
            Path,
            '/path',
            10
        )

        self.tf_buffer = tf2_ros.Buffer()

        self.tf_listener = tf2_ros.TransformListener(
            self.tf_buffer,
            self
        )

        self.timer = self.create_timer(
            0.1,
            self.process
        )

    def rgb_callback(self, msg):

        self.rgb_image = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

    def depth_callback(self, msg):

        self.depth_image = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='32FC1'
        )

    def camera_info_callback(self, msg):

        self.fx = msg.k[0]
        self.fy = msg.k[4]

        self.cx = msg.k[2]
        self.cy = msg.k[5]

    def process(self):

        if self.rgb_image is None:
            return

        if self.depth_image is None:
            return

        if self.fx is None:
            return

        hsv = cv2.cvtColor(
            self.rgb_image,
            cv2.COLOR_BGR2HSV
        )

        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(
            hsv,
            lower_red1,
            upper_red1
        )

        mask2 = cv2.inRange(
            hsv,
            lower_red2,
            upper_red2
        )

        mask = mask1 + mask2

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contours) == 0:
            return

        largest = max(
            contours,
            key=cv2.contourArea
        )

        M = cv2.moments(largest)

        if M['m00'] == 0:
            return

        u = int(M['m10'] / M['m00'])
        v = int(M['m01'] / M['m00'])

        depth = self.depth_image[v, u]

        if not math.isfinite(depth):
            return

        Z = depth

        X = (u - self.cx) * Z / self.fx
        Y = (v - self.cy) * Z / self.fy

        point_cam = PointStamped()

        point_cam.header.frame_id = 'stereo_cam'

        point_cam.point.x = X
        point_cam.point.y = Y
        point_cam.point.z = Z

        try:

            transform = self.tf_buffer.lookup_transform(
                'odom',
                'stereo_cam',
                rclpy.time.Time()
            )

            point_odom = do_transform_point(
                point_cam,
                transform
            )

        except Exception as e:

            self.get_logger().warn(str(e))

            return

        path = Path()

        path.header.frame_id = 'odom'

        pose = PoseStamped()

        pose.header.frame_id = 'odom'

        pose.pose.position.x = point_odom.point.x
        pose.pose.position.y = point_odom.point.y
        pose.pose.position.z = 0.0

        pose.pose.orientation.w = 1.0

        path.poses.append(pose)

        self.path_pub.publish(path)

        self.get_logger().info(
            f'Ball at: '
            f'({point_odom.point.x:.2f}, '
            f'{point_odom.point.y:.2f})'
        )


def main(args=None):

    rclpy.init(args=args)

    node = BallTracker()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':

    main()