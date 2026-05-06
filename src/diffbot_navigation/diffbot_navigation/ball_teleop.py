#!/usr/bin/env python3

import os
import sys
import tty
import termios

import rclpy
from rclpy.node import Node


class BallTeleop(Node):

    def __init__(self):

        super().__init__('ball_teleop')

        self.x = 3.0
        self.y = 2.0
        self.z = 0.3

        self.step = 0.3

        self.get_logger().info(
            'Use W/S/A/D to move red ball'
        )

        self.run()

    def get_key(self):

        fd = sys.stdin.fileno()

        old_settings = termios.tcgetattr(fd)

        try:

            tty.setraw(fd)

            key = sys.stdin.read(1)

        finally:

            termios.tcsetattr(
                fd,
                termios.TCSADRAIN,
                old_settings
            )

        return key

    def move_ball(self):

        cmd = f'''
ign service -s /world/car_world/set_pose \
--reqtype ignition.msgs.Pose \
--reptype ignition.msgs.Boolean \
--timeout 1000 \
--req 'name: "red_ball",
position: {{
x: {self.x},
y: {self.y},
z: {self.z}
}},
orientation: {{
w: 1.0
}}'
'''

        os.system(cmd)

        self.get_logger().info(
            f'Ball moved to '
            f'({self.x:.2f}, {self.y:.2f})'
        )

    def run(self):

        while rclpy.ok():

            key = self.get_key()

            if key == 'w':

                self.x += self.step

            elif key == 's':

                self.x -= self.step

            elif key == 'a':

                self.y += self.step

            elif key == 'd':

                self.y -= self.step

            elif key == 'q':

                break

            self.move_ball()


def main(args=None):

    rclpy.init(args=args)

    node = BallTeleop()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':

    main()