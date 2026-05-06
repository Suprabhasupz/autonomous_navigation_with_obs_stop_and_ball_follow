# FarmRobo R1 — Take-Home Evaluation Project

**Title:** *R1 in Gazebo — Bringup → Stereo → Pure Pursuit → Ball Follow*

**Estimated effort:** 2 days of focused work.
**Deadline:** As communicated separately. Ask early if you need an extension.

---

## 1. Why this project

Four small stages, each building on the previous. We use this to evaluate three things:

1. **Simulation skill** — bringing a URDF up in Gazebo and adding a sensor.
2. **ROS 2 skill** — clean node design, parameters, launch files.
3. **Path planning + perception integration** — pure pursuit, obstacle-aware motion, simple vision.

You may use AI tools (ChatGPT, Claude, Cursor, Copilot, Gemini, etc.). You **must** document usage per stage — see Section 5.

We will read the **git history**. Each stage is a separate branch + tag. Force-pushes or squash-everything-at-the-end disqualify the audit.

---

## 2. The robot

URDF: `urdf/r1_eval.urdf`. Wheel meshes in `meshes/`. Other links are box primitives.

| Item | Value |
|---|---|
| Drive | Skid-steer / diff-drive (Ignition `DiffDrive` plugin) |
| Wheel separation | 0.65725 m |
| Wheel radius | 0.065 m |
| Cmd topic | `/cmd_vel` (geometry_msgs/Twist) |
| Odom topic | `/odom` (publishes TF too) |
| Camera link | `stereo_cam` (Orbbec Gemini 336L placeholder, pitched 30° nose-down, mounted at z = 1.314 m) |

The URDF does **not** yet contain a Gazebo `<sensor>` block for the depth camera — that's Stage 2.

**Toolchain we expect:** Ubuntu 22.04, ROS 2 Humble, Gazebo Ignition Fortress (the URDF references `libignition-gazebo6-*` plugins). Python or C++, your choice — pick one and stick with it.

---

## 3. The four stages

You will build a ROS 2 package called **`fr_r1_sim_task`**. Work stage-by-stage. Don't start a stage until the previous one runs.

### Stage 1 — Bringup + teleop

- Spawn `r1_eval.urdf` in Gazebo on a flat ground plane.
- `robot_state_publisher` + clean TF tree.
- Drive the robot with `teleop_twist_keyboard` (or any teleop) on `/cmd_vel`.
- A single launch file brings everything up.

**Done when:** you can teleop the robot in a circle and `/odom` looks sane in `rviz2`.

**Deliverable:** branch `stage/1-bringup`, merged to `main`, tag `s1-bringup`. Short screen recording: `media/s1_teleop.mp4`.

### Stage 2 — Stereo camera publishing

- Add a `<gazebo reference="stereo_cam">` sensor block. Publish, on ROS 2 topics:
  - color image
  - depth image
  - `camera_info`
- Add the standard 90° optical-frame child link if your driver convention requires it.
- Place a couple of objects in the world and verify depth values look correct in `rqt_image_view`.

**Done when:** `ros2 topic hz` shows real frame rates on all three topics and the depth image visually matches the scene.

**Deliverable:** branch `stage/2-camera`, merged, tag `s2-camera`. Screen recording: `media/s2_camera.mp4` (rqt showing color + depth side by side).

### Stage 3 — Pure pursuit + obstacle stop

Two nodes, plus a config YAML.

- **`path_follower`** — subscribes to `/odom` and a waypoint list (`nav_msgs/Path` or your own message; document your choice), publishes `/cmd_vel`. Pure pursuit. Parameters: `lookahead_distance`, `max_linear_velocity`, `max_angular_velocity`. Stops cleanly when the last waypoint is reached.
- **`obstacle_stop`** — subscribes to the depth image, decides if anything is within `stop_distance` (default 2.0 m) inside a configurable central ROI, and **gates `/cmd_vel`**: when an obstacle is present, the robot does not move. Document your gating mechanism (twist mux, intermediate topic, in-process gate — your call). Publish `/obstacle_detected` (`std_msgs/Bool`) for visibility.

**Test with:**
- a hand-crafted waypoint list (e.g., a square loop)
- a randomly-generated list (a small Python script that publishes 5–10 random waypoints inside a 10 m × 10 m area)

Place one box obstacle in the world that intersects one of the test paths.

**Done when:** robot follows both lists, and stops in front of the obstacle when one is in the way.

**Deliverable:** branch `stage/3-planner`, merged, tag `s3-planner`. Two videos: `media/s3_clean.mp4`, `media/s3_obstacle_stop.mp4`.

### Stage 4 — Ball follow (integration demo)

- Spawn a brightly-coloured sphere (e.g., red) in the Gazebo world. Make it teleop-able — a second small node that listens on `/ball/cmd_vel` and moves the sphere model in Gazebo. (Hint: Ignition has a `pose-publisher` and you can use the `/world/<name>/set_pose` service to teleport the ball, or attach a planar mover plugin. Either is fine.)
- **`ball_tracker`** node — subscribes to the color + depth + `camera_info` topics from Stage 2:
  - HSV-segment the ball in the color image.
  - Look up the depth at the ball's centroid.
  - Project to a 3D point in the camera frame, then transform to the `odom` frame using TF.
  - Publish that point as the current goal for `path_follower`.
- The `path_follower` from Stage 3 now treats the ball's pose as its **single dynamic waypoint** and chases it. Obstacle-stop layer stays active.

**Constraint — read this:** ball detection must be **classical HSV segmentation + depth lookup**. No YOLO, no neural detector. We want to see your camera-intrinsics + depth-to-3D math, not a black-box model.

**Done when:** you can teleop the ball, the robot follows, and the robot stops when something gets in the way.

**Deliverable:** branch `stage/4-ball-follow`, merged, tag `s4-follow`. Video: `media/s4_ball_follow.mp4`. Bonus marks for a run that includes an obstacle stop mid-chase.

---

## 4. Submission layout

```
fr_r1_sim_task/
├── README.md                  # Your README — how to run your code
├── SUMMARY.md                 # Approach write-up (use SUMMARY_TEMPLATE.md)
├── AI_USAGE.md                # Per-stage prompt log (use AI_USAGE_TEMPLATE.md)
├── src/r1_row_follow/         # The ROS 2 package
│   ├── package.xml, setup.py / CMakeLists.txt
│   ├── r1_row_follow/         # source
│   ├── launch/
│   ├── config/
│   ├── worlds/
│   ├── urdf/                  # may edit r1_eval.urdf
│   └── meshes/
└── media/
    ├── s1_teleop.mp4
    ├── s2_camera.mp4
    ├── s3_clean.mp4
    ├── s3_obstacle_stop.mp4
    └── s4_ball_follow.mp4
```

Videos can be screen recordings (`peek`, `kazam`, OBS), ≤ 60 s each is fine.

---

## 5. AI tool usage — required documentation

Use `AI_USAGE_TEMPLATE.md`. The structure is **one section per stage**. For each stage, log:

1. Which AI tools / models you used in that stage.
2. The 3–5 most impactful prompts of that stage — prompt + short outcome + what you changed in the response before using it.
3. Anything the tool got wrong that you had to override.

If you exported chats with a Chrome extension (e.g. *AI Conversation Exporter*, *ChatGPT Exporter*, *Save ChatGPT*), commit them under `ai_chats/` and link them per stage instead of pasting full transcripts.

We do **not** penalise using AI to write code. We **do** penalise code you cannot walk through line-by-line on a follow-up call.

---

## 6. Approach summary — required

`SUMMARY.md` is a short write-up. Use `SUMMARY_TEMPLATE.md`. We weight the summary as much as the code.

---

## 7. Git discipline

This is part of the evaluation:

- One branch per stage: `stage/1-bringup`, `stage/2-camera`, `stage/3-planner`, `stage/4-ball-follow`.
- Merge to `main` only when the stage actually runs.
- Tag each merged stage: `s1-bringup`, `s2-camera`, `s3-planner`, `s4-follow`.
- Commit small and often. We read `git log`.
- **No force-pushes.** No final "squash everything" commit. We want to see the journey, including dead ends.

---

## 8. What we evaluate

| Stage | Weight | Pass criteria |
|---|---|---|
| S1 — Bringup + teleop | 15% | Robot drives, TF clean, single launch file |
| S2 — Stereo publishing | 20% | Color + depth + camera_info, depth values realistic |
| S3 — Pure pursuit + obstacle stop | 35% | Tracks both hand-crafted and random waypoints; stops on obstacle |
| S4 — Ball follow | 20% | HSV + depth → 3D → goal → pure pursuit chases ball |
| Code quality, summary, AI doc, git history | 10% | Honest, readable, traceable |

---

## 9. Submission steps

1. Push to a **public GitHub repo** and share with us the link.
2. We respond within 3 working days with a follow-up call or decision.

---

Good luck.
