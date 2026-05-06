#!/usr/bin/env python3

#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry, Path


class PathFollower(Node):

    def __init__(self):
        super().__init__('path_follower')

        self.declare_parameter('lookahead_distance', 1.0)
        self.declare_parameter('max_linear_velocity', 0.8)
        self.declare_parameter('max_angular_velocity', 1.5)
        self.declare_parameter('goal_tolerance', 0.3)

        self.lookahead_distance = self.get_parameter(
            'lookahead_distance').value

        self.max_linear_velocity = self.get_parameter(
            'max_linear_velocity').value

        self.max_angular_velocity = self.get_parameter(
            'max_angular_velocity').value

        self.goal_tolerance = self.get_parameter(
            'goal_tolerance').value

        self.path = []

        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0

        self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10)

        self.create_subscription(
            Path,
            '/path',
            self.path_callback,
            10)

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel_raw',
            10)

        self.timer = self.create_timer(
            0.1,
            self.control_loop)

    def odom_callback(self, msg):

        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

        self.robot_yaw = math.atan2(siny_cosp, cosy_cosp)

    def path_callback(self, msg):

        self.path = msg.poses

        self.get_logger().info(
            f'Received path with {len(self.path)} waypoints'
        )

    def stop_robot(self):

        twist = Twist()

        twist.linear.x = 0.0
        twist.angular.z = 0.0

        self.cmd_pub.publish(twist)

    def control_loop(self):
        if len(self.path) == 0:
            return

        # initialize current waypoint index
        if not hasattr(self, 'current_waypoint_index'):
            self.current_waypoint_index = 0

        # stop at final goal
        if self.current_waypoint_index >= len(self.path):

            self.get_logger().info('Goal reached')

            self.stop_robot()
            return

        # current target waypoint
        target_pose = self.path[
            self.current_waypoint_index
        ].pose

        tx = target_pose.position.x
        ty = target_pose.position.y

        # distance to current waypoint
        distance = math.hypot(
            tx - self.robot_x,
            ty - self.robot_y
        )

        # move to next waypoint
        if distance < self.goal_tolerance:

            self.current_waypoint_index += 1

            return

        dx = tx - self.robot_x
        dy = ty - self.robot_y

        target_angle = math.atan2(dy, dx)

        alpha = target_angle - self.robot_yaw

        while alpha > math.pi:
            alpha -= 2.0 * math.pi

        while alpha < -math.pi:
            alpha += 2.0 * math.pi

        linear = self.max_linear_velocity

        angular = (
            2.0 * linear * math.sin(alpha)
        ) / self.lookahead_distance

        angular = max(
            -self.max_angular_velocity,
            min(self.max_angular_velocity, angular)
        )

        twist = Twist()

        twist.linear.x = linear
        twist.angular.z = angular

        self.cmd_pub.publish(twist)

def main(args=None):

    rclpy.init(args=args)

    node = PathFollower()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()