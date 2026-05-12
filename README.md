# Autonomous Navigation with Obstacle Stop and Ball Follow

## Overview

This project implements a complete ROS 2 + Ignition Gazebo autonomous navigation pipeline for a differential drive robot.

The system includes:

* Differential drive robot simulation
* RGB + Depth camera integration
* ROS 2 ↔ Ignition Gazebo topic bridging
* Pure pursuit path following
* Obstacle stop layer using depth image processing
* Dynamic ball-follow behavior using HSV segmentation and depth lookup
* Ball teleoperation inside Ignition Gazebo

Repository:

[https://github.com/Suprabhasupz/autonomous_navigation_with_obs_stop_and_ball_follow](https://github.com/Suprabhasupz/autonomous_navigation_with_obs_stop_and_ball_follow)
git clone https://github.com/Suprabhasupz/autonomous_navigation_with_obs_stop_and_ball_follow

---

# Project Stages

## Stage 1 — Robot Simulation

Implemented:

* Differential drive robot in Ignition Gazebo
* URDF/SDF robot description
* Wheel joints and differential drive plugin
* TF tree
* Odometry publishing
* Joint state publishing

Main plugins used:

* DiffDrive
* JointStatePublisher
* PosePublisher

---

## Stage 2 — Camera Integration

Integrated sensors:

* RGB camera
* Depth camera

Topics:

| Topic        | Type                   |
| ------------ | ---------------------- |
| /camera      | RGB image              |
| /depth_image | Depth image            |
| /camera_info | Camera intrinsics      |
| /odom        | Robot odometry         |
| /cmd_vel     | Robot velocity command |

ROS ↔ Gazebo communication implemented using:

* ros_gz_bridge

---

## Stage 3 — Pure Pursuit + Obstacle Stop

### Path Follower

The `path_follower` node:

* Subscribes to `/path`
* Subscribes to `/odom`
* Computes steering using pure pursuit
* Publishes `/cmd_vel_raw`

Features:

* Waypoint following
* Goal detection
* Dynamic target following
* Configurable lookahead distance

Parameters:

| Parameter            | Description            |
| -------------------- | ---------------------- |
| lookahead_distance   | Pure pursuit lookahead |
| max_linear_velocity  | Maximum robot speed    |
| max_angular_velocity | Maximum turn speed     |
| goal_tolerance       | Goal reach threshold   |

---

### Obstacle Stop

The `obstacle_stop` node:

* Subscribes to `/depth_image`
* Subscribes to `/cmd_vel_raw`
* Publishes gated `/cmd_vel`
* Publishes `/obstacle_detected`

Functionality:

1. Extracts central ROI from depth image
2. Filters invalid depth values
3. Computes obstacle distance
4. Stops robot when obstacle is within stop distance

Obstacle detection pipeline:

```python
roi = depth[y1:y2, x1:x2]

valid = roi[
    np.isfinite(roi) &
    (roi > 0.5) &
    (roi < 15.0)
]

obstacle_distance = np.percentile(valid, 20)
```

If:

```python
obstacle_distance <= stop_distance
```

robot motion is stopped.

---

## Stage 4 — Ball Follow

### Ball Teleop

A red ball is spawned inside Ignition Gazebo.

The `ball_teleop` node:

* Uses keyboard control
* Moves ball using Ignition `set_pose` service

Controls:

| Key | Action   |
| --- | -------- |
| W   | Forward  |
| S   | Backward |
| A   | Left     |
| D   | Right    |
| Q   | Quit     |

---

### Ball Tracker

The `ball_tracker` node:

* Subscribes to RGB image
* Subscribes to depth image
* Subscribes to camera info
* Performs HSV segmentation
* Finds ball centroid
* Reads depth at centroid
* Converts pixel to 3D point
* Transforms point to odom frame using TF
* Publishes dynamic waypoint to `/path`

HSV segmentation:

```python
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
mask = mask1 + mask2
```

Depth lookup:

```python
depth = self.depth_image[v, u]
```

3D projection:

```python
X = (u - cx) * Z / fx
Y = (v - cy) * Z / fy
Z = depth
```

TF transform:

```python
lookup_transform('odom', 'stereo_cam')
```

Published output:

```text
/path
```

The robot dynamically follows the moving ball.

---

# System Architecture

```text
Red Ball (Gazebo)
        ↓
RGB + Depth Camera
        ↓
ball_tracker
        ↓
/path
        ↓
path_follower
        ↓
/cmd_vel_raw
        ↓
obstacle_stop
        ↓
/cmd_vel
        ↓
Robot Motion
```

---

# Package Structure

```text
(diffbot_ws)
├── src
│   ├── diffbot_description
│   ├── diffbot_navigation
│   └── ros_gz_bridge
```

Main nodes:

```text
path_follower.py
obstacle_stop.py
square_waypoints.py
random_waypoints.py
ball_tracker.py
ball_teleop.py
```

---

# Build Instructions

## Create Workspace

```bash
mkdir -p ~/diffbot_ws/src
cd ~/diffbot_ws
```

---

## Build Workspace

```bash
cd ~/diffbot_ws

colcon build --symlink-install
```

---

## Source Workspace

```bash
source ~/diffbot_ws/install/setup.bash
```

---

# Running the Project

## Launch Ignition Gazebo

```bash
ros2 launch diffbot_description gazebo.launch.py
```

---

## Manual Robot Teleoperation

To manually drive the robot using keyboard teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

This publishes velocity commands to:

```text
/cmd_vel
```

Controls:

```text
u i o
j k l
m , .
```

Example:

* `i` → move forward
* `,` → move backward
* `j` → turn left
* `l` → turn right
* `k` → stop robot

---

## Launch Navigation Stack

```bash
ros2 launch diffbot_navigation navigation.launch.py
```

This starts:

* path_follower
* obstacle_stop

---

# Stage 3 Testing

## Launch Navigation Stack

```bash
ros2 launch diffbot_navigation navigation.launch.py
```

This launches:

* path_follower
* obstacle_stop
* square_waypoints

---


This publishes randomly generated waypoints for autonomous navigation testing.

---

# Stage 4 Running Instructions
Terminal 1 — Gazebo
cd ~/diffbot_ws

source install/setup.bash

ros2 launch diffbot_description gazebo.launch.py

Wait until:

✅ robot appears
✅ red ball appears

Terminal 2 — Navigation stack
cd ~/diffbot_ws

source install/setup.bash

ros2 launch diffbot_navigation navigation.launch.py

This starts:

✅ path_follower
✅ obstacle_stop

Terminal 3 — Ball tracker
cd ~/diffbot_ws

source install/setup.bash

ros2 run diffbot_navigation ball_tracker

This node:

✅ detects red ball
✅ computes 3D position
✅ publishes /path

Terminal 4 — Ball teleop
cd ~/diffbot_ws

source install/setup.bash

ros2 run diffbot_navigation ball_teleop

Controls:

W → move forward
S → move backward
A → move left
D → move right
Q → quit
Expected behavior
Move ball
   ↓
Robot sees red ball
   ↓
Robot follows ball
   ↓
Obstacle appears
   ↓
Robot stops
```

Controls:

```text
W → move forward
S → move backward
A → move left
D → move right
Q → quit
```



# Expected Final Behavior

## Ball Following

1. User teleoperates red ball
2. RGB camera detects red object
3. Depth image provides distance
4. Ball position transformed into odom frame
5. Pure pursuit generates velocity command
6. Robot follows moving ball

---

## Obstacle Stop

1. Depth ROI continuously monitored
2. Obstacle detected within threshold
3. `/cmd_vel` gated to zero
4. Robot stops safely before collision

---

# Videos

The repository includes:

* Stage 3 clean navigation demo
* Stage 3 obstacle stop demo
* Stage 4 ball follow demo

Demonstrations include:

* Waypoint following
* Random navigation
* Obstacle stopping
* Dynamic ball following
* Teleoperated target tracking


