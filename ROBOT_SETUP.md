# Robot Camera Tracking - Setup Guide

This system uses a webcam with YOLO object detection to track objects and control a LEGO robot to keep the object centered in view.

## Quick Start (2-Step Process)

### Step 1: Start the Robot

Open a **first terminal** and run:

```powershell
python -m pybricksdev run ble -n test robot_hub.py
```

**What this does:**
- Connects to your LEGO hub via Bluetooth (make sure it's named "test" or change `-n test` to match your hub name)
- Uploads `robot_hub.py` to the hub
- Runs calibration (you'll see the robot move all motors to verify they work)
- Keeps the robot program running and ready to receive commands

**Expected output:**
```
🤖 Robot hub initialized!
🤖 Running calibration demo...
Testing base rotation...
Testing shoulder movement...
Testing elbow movement...
Testing gripper...
✅ Calibration complete!
🎯 Robot ready! Waiting for camera commands...
```

**Leave this terminal open** - the robot program must keep running!

---

### Step 2: Start the Camera Tracking

Open a **second terminal** and run:

```powershell
python .\main.py --target_object bottle --use_robot
```

**What this does:**
- Opens your webcam
- Runs YOLO object detection to find "bottle" (or whatever object you specify)
- Prints "Look left", "Look right", or "Centered" based on where the object is
- When `--use_robot` is enabled, prints commands like `ROBOT_CMD:BASE:5` or `ROBOT_CMD:BASE:-5`

**To manually control the robot** based on these commands, you can:
1. Watch the camera terminal for `ROBOT_CMD` lines
2. The robot will need to read these commands (see Advanced Setup below for automation)

---

## Usage Examples

### Track different objects:

```powershell
# Track a cup
python .\main.py --target_object cup --use_robot

# Track a person
python .\main.py --target_object person --use_robot

# Track a bottle with smaller movements (3 degrees instead of 5)
python .\main.py --target_object bottle --use_robot --movement_step 3
```

### Adjust sensitivity:

```powershell
# Wider center zone (easier to achieve "centered")
python .\main.py --target_object bottle --use_robot --center_threshold 0.3

# Narrower center zone (more precise centering required)
python .\main.py --target_object bottle --use_robot --center_threshold 0.1
```

### Camera-only mode (no robot):

```powershell
# Just print directions, don't send robot commands
python .\main.py --target_object bottle
```

---

## Available Objects to Track

See `names.txt` for the full list. Common objects include:
- person
- bicycle, car, motorcycle
- bottle, cup, wine glass
- chair, couch, dining table
- laptop, mouse, keyboard, cell phone
- book, clock, vase

---

## Command Reference

### CLI Arguments for `main.py`:

| Argument | Default | Description |
|----------|---------|-------------|
| `--target_object` | None (required) | Object name to track from `names.txt` |
| `--use_robot` | False | Enable robot control mode |
| `--movement_step` | 5 | Degrees to move robot per adjustment |
| `--center_threshold` | 0.2 | Width of center zone (0.1-0.4 recommended) |
| `--webcam_resolution` | 640 480 | Webcam resolution (width height) |

### Robot Commands Output:

When `--use_robot` is enabled, the camera script prints commands in this format:

```
ROBOT_CMD:BASE:5       # Move base right 5 degrees
ROBOT_CMD:BASE:-5      # Move base left 5 degrees
ROBOT_CMD:STOP         # Stop/shutdown
```

---

## How It Works

### Camera Detection Logic:

1. **Object Detection**: YOLO finds all objects in the frame
2. **Target Matching**: Checks if any detected object matches `--target_object`
3. **Position Calculation**:
   - Computes bounding box of the detected object
   - Calculates what fraction of the box is in the center zone
4. **Decision**:
   - If >50% of box is in center zone → "Centered" (no movement)
   - If box is left of center zone → "Look left" (move base left)
   - If box is right of center zone → "Look right" (move base right)

### Robot Movement Bounds:

Defined in `robot_hub.py`:
- **Base**: -90° to +90° (left/right rotation)
- **Shoulder**: 0° to 90° (up/down - currently not used for tracking)

The robot automatically prevents movements beyond these bounds.

---

## Troubleshooting

### Problem: "Could not find hub"

**Solution:**
- Make sure the LEGO hub is turned on
- Check that Bluetooth is enabled on your PC
- Verify the hub name with: `python -m pybricksdev list`
- Update `-n test` to match your hub's actual name

### Problem: "Camera not found"

**Solution:**
- Run `python webcam.py` to list available camera indices
- Try different camera indices by modifying `main.py` line 53: `cv2.VideoCapture(0)` → `cv2.VideoCapture(1)` etc.

### Problem: "Object detected but robot doesn't move"

**Current Status:**
- The camera script prints `ROBOT_CMD` lines to console
- For **automatic** robot control, you need to pipe these commands to the robot
- See "Advanced Setup" below for automation

### Problem: Robot moves too fast/slow

**Solution:**
- Adjust `--movement_step`: smaller values = slower, more precise
- Adjust `--center_threshold`: larger values = less frequent movements

---

## Advanced Setup (Automated Robot Control)

To automatically send camera commands to the robot, you'll need to set up bidirectional communication between the two terminals. Here are a few approaches:

### Option 1: Use `run_robot_tracking.py` launcher (Recommended)

```powershell
python run_robot_tracking.py --target_object bottle
```

This script:
1. Automatically starts the robot with calibration
2. Waits for calibration to complete
3. Starts the camera tracking
4. Manages both processes together

### Option 2: Manual pipe setup (Advanced)

Create a named pipe or use socket communication between the camera script and robot. (Contact me if you need help implementing this.)

---

## Files in This Project

- `main.py` - Camera tracking script with YOLO detection
- `robot_hub.py` - Robot program that runs ON the LEGO hub
- `robot_controller.py` - Python API for robot control (PC-side, not currently used)
- `webcam.py` - Simple webcam viewer and camera enumeration utility
- `run_robot_tracking.py` - Launcher script (work in progress)
- `names.txt` - List of objects YOLO can detect
- `yolov8l.pt` - YOLO model weights

---

## Tips for Best Results

1. **Lighting**: Ensure good, even lighting on the object
2. **Background**: Simple backgrounds work better than cluttered ones
3. **Distance**: Keep object 1-3 meters from camera for best detection
4. **Object Size**: Larger objects in frame are detected more reliably
5. **Movement**: Start with `--movement_step 3` for smoother tracking
6. **Center Zone**: Start with default 0.2, adjust based on desired precision

---

## Next Steps / Future Enhancements

- [ ] Vertical tracking using shoulder motor
- [ ] Smoothing/debouncing to reduce jitter
- [ ] Automatic robot command forwarding via BLE
- [ ] Distance estimation to maintain object at optimal range
- [ ] Multi-object tracking (track closest/largest instance)
- [ ] Save tracking data to log file

---

## Need Help?

Common issues:
1. **Robot not calibrating**: Check hub battery, motor connections, port assignments
2. **Object not detected**: Try different lighting, distance, or a different object
3. **Flickering labels**: Use `--center_threshold 0.3` for more stable centering
4. **Robot hitting limits**: Movements accumulate - restart robot program to reset to center

For more details, see the code comments in `main.py` and `robot_hub.py`.
