# Approach Summary — R1 Eval Submission

> Rename this file to `SUMMARY.md` before submission. Delete this quote block.
> Aim for 1–2 pages of substance. Diagrams welcome.

## 1. How I ran the project

- **Total time spent:** _e.g. ~7 hours over 2 days_
- **Toolchain:** Ubuntu 22.04 / ROS 2 Humble / Gazebo Ignition Fortress / Python or C++
- **Anything unusual** (laptop GPU, SSH-only, Docker, etc.):

## 2. Stage 1 — Bringup

- Anything non-trivial about getting the URDF to spawn cleanly:
- TF tree shape (one-line description or `rqt_tf_tree` screenshot):

## 3. Stage 2 — Stereo camera

- The Gazebo `<sensor>` block you added (paste the snippet, or link the file/lines):
- Optical-frame handling — did you add a child link with a 90° rotation? Why or why not:
- One sanity check you ran on the depth values (e.g., "pointed robot at a 2 m wall, median depth = 2.04 m"):

## 4. Stage 3 — Pure pursuit + obstacle stop

- Lookahead distance you settled on, and how you tuned it:
- **Tracking error** you observed on the hand-crafted square loop (cross-track or RMS):
- The bottleneck that limits accuracy further:
- How `cmd_vel` is gated by the obstacle layer (one-line architecture description):
- **How the obstacle layer fails.** Every safety layer fails somewhere — tell us where yours does. Examples we'd accept: false positive on shadows, false negative on transparent objects, ROI misses lateral hazards, race condition with the controller, etc.

## 5. Stage 4 — Ball follow

- HSV range you used and how you picked it:
- The math from `(u, v, depth)` → 3D point in camera frame → goal in `odom` frame. A short formula or code snippet is fine:
- Failure modes you saw (lighting, ball too close / too far, ball at edge of frame, NaN depth pixels):
- How "single dynamic waypoint" interacts with pure pursuit's lookahead — anything you had to do differently:

## 6. ROS 2 architecture

A small node + topic diagram (mermaid, ASCII, or `rqt_graph` screenshot). Mark which topics are inputs vs. outputs of your nodes.

## 7. Honest assessment

- **Works reliably:**
- **Works most of the time:**
- **Doesn't work / not finished:**

## 8. What I would do in another week

1–3 concrete items, not "make it better".
