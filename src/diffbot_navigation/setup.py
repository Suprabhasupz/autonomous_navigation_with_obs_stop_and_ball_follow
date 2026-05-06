from setuptools import setup
from glob import glob
import os

package_name = 'diffbot_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='suprabha',
    maintainer_email='suprabha@todo.todo',
    description='Pure pursuit navigation with obstacle stop',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'path_follower = diffbot_navigation.path_follower:main',
            'obstacle_stop = diffbot_navigation.obstacle_stop:main',
            'square_waypoints = diffbot_navigation.square_waypoints:main',
            'random_waypoints = diffbot_navigation.random_waypoints:main',
            'ball_tracker = diffbot_navigation.ball_tracker:main',
            'ball_teleop = diffbot_navigation.ball_teleop:main',
        ],
    },
)
