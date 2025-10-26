# Using the Bridge Script for Automated Robot Control

## Overview

The `bridge.py` script automatically connects your camera tracking to robot control in a single command. It:

1. ✅ Starts the robot hub via pybricksdev
2. ✅ Runs robot calibration 
3. ✅ Starts the camera tracking
4. ✅ **Automatically sends movement commands** from camera to robot
5. ✅ Handles shutdown cleanly when you press Ctrl+C

## Quick Start (One Command!)

```powershell
python bridge.py --target_object bottle
```

That's it! The bridge handles everything automatically.

## What Happens

### Step 1: Robot Initialization
```
🤖 STEP 1: Starting robot hub...
⏳ Uploading robot_hub.py to LEGO hub...
[ROBOT] 🤖 Robot hub initialized!
[ROBOT] 🤖 Running calibration demo...
[ROBOT] Testing base rotation...
[ROBOT] Testing shoulder movement...
[ROBOT] ✅ Calibration complete!
✅ Robot hub is running and calibrated!
```

### Step 2: Camera Starts
```
📷 STEP 2: Starting camera tracking...
Target: bottle
Movement step: 5°
[CAMERA] 🤖 Robot control enabled
```

### Step 3: Automatic Control
```
✅ BRIDGE ACTIVE - Camera and Robot Connected!
Monitoring camera output and sending commands to robot...

[CAMERA] Look left
[CAMERA] ROBOT_CMD:SHOULDER:-5
  ✓ Sent to robot: SHOULDER -5° (total: 1)
[ROBOT] Shoulder → -5°

[CAMERA] Look left
[CAMERA] ROBOT_CMD:SHOULDER:-5
  ✓ Sent to robot: SHOULDER -5° (total: 2)
[ROBOT] Shoulder → -10°

[CAMERA] Centered
```

## Command-Line Options

```powershell
# Basic usage
python bridge.py --target_object bottle

# Custom movement step (smaller = more precise)
python bridge.py --target_object cup --movement_step 3

# Adjust center threshold
python bridge.py --target_object person --center_threshold 0.3

# Different robot name
python bridge.py --target_object bottle --robot_name myrobot

# Skip robot initialization (if robot already running)
python bridge.py --target_object bottle --skip_calibration
```

### All Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--target_object` | (required) | Object name from names.txt |
| `--robot_name` | `test` | BLE name of your LEGO hub |
| `--movement_step` | `5` | Degrees to move per command |
| `--center_threshold` | `0.2` | Center zone width (0.1-0.4) |
| `--webcam_resolution` | `640 480` | Camera resolution |
| `--skip_calibration` | False | Skip robot init (already running) |

## How It Works

### Architecture:

```
┌──────────────────┐
│   bridge.py      │  ← You run this one script
│   (on your PC)   │
└────────┬─────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐
│  robot_hub.py    │             │    main.py       │
│  (on LEGO hub)   │             │   (on your PC)   │
│                  │             │                  │
│ • Calibrates     │             │ • Opens camera   │
│ • Moves motors   │◄────────────│ • Runs YOLO      │
│ • Stays running  │  Commands   │ • Outputs cmds   │
└──────────────────┘             └──────────────────┘
```

### Communication Flow:

1. **Camera** detects object is left of center
2. **Camera** prints: `ROBOT_CMD:SHOULDER:-5`
3. **Bridge** captures this output
4. **Bridge** sends `move_shoulder(-5)` to robot
5. **Robot** executes command and moves
6. Loop continues until object is centered

### Debouncing:

The bridge includes automatic command debouncing:
- Minimum 0.3 seconds between commands
- Prevents overwhelming the robot with too many rapid commands
- Ensures smooth, controlled movements

## Requirements

1. **Hardware:**
   - LEGO Spike/Mindstorms hub with Pybricks firmware
   - Motors connected to ports A (base), B (shoulder), C (elbow), F (gripper)
   - USB webcam
   - Bluetooth connection to hub

2. **Software:**
   - Python 3.8+
   - pybricksdev: `pip install pybricksdev`
   - ultralytics (YOLO): `pip install ultralytics`
   - opencv-python: `pip install opencv-python`

3. **Files:**
   - `bridge.py` - Main bridge script
   - `robot_hub.py` - Robot control program
   - `main.py` - Camera tracking script
   - `yolov8l.pt` - YOLO model weights
   - `names.txt` - Object class names

## Troubleshooting

### "Could not find hub"
- Turn on the LEGO hub
- Check Bluetooth is enabled on PC
- Verify hub name: `python -m pybricksdev list`
- Use `--robot_name` to specify correct name

### "Camera not found"
- Run `python webcam.py` to find camera index
- Check camera isn't used by another app
- Try different USB port

### Robot doesn't move
- Check motors are connected to correct ports
- Verify calibration completed successfully
- Look for error messages in bridge output
- Try running `robot_hub.py` manually first

### Commands sent but robot unresponsive
- Pybricksdev may not support stdin in all modes
- Try the manual two-terminal approach instead
- Check for error messages in robot output

### Object detected but no commands
- Verify `--target_object` matches exactly (case-insensitive)
- Check object is actually detected (appears in video window)
- Try different lighting/background

## Manual Mode (Two Terminals)

If the bridge doesn't work, you can run manually:

**Terminal 1:**
```powershell
python -m pybricksdev run ble -n test robot_hub.py
```

**Terminal 2:**
```powershell
python .\main.py --target_object bottle --use_robot
```

Watch Terminal 2 for commands and verify robot responds.

## Advanced Usage

### Test Movement Commands Manually

After starting robot with bridge, you can manually send commands:

```powershell
# While bridge is running, robot will respond to camera commands
# Or start robot separately and send Python commands via REPL
```

### Modify Movement Speed

Edit `robot_hub.py` line 20:
```python
SPEED = 200  # Change to 100 (slower) or 300 (faster)
```

### Adjust Motor Bounds

Edit `robot_hub.py` lines 23-26:
```python
SHOULDER_MIN = 0
SHOULDER_MAX = 90
BASE_MIN = -90
BASE_MAX = 90
```

## Examples

### Track a cup with precise movements:
```powershell
python bridge.py --target_object cup --movement_step 3 --center_threshold 0.15
```

### Track a person with larger center zone:
```powershell
python bridge.py --target_object person --movement_step 7 --center_threshold 0.35
```

### Use with already-running robot:
```powershell
# Terminal 1: Start robot manually
python -m pybricksdev run ble -n test robot_hub.py

# Terminal 2: Start bridge without robot initialization
python bridge.py --target_object bottle --skip_calibration
```

## Stopping the Bridge

- Press **Ctrl+C** in the bridge terminal
- Or press **'q'** in the video window
- Both methods will cleanly stop camera and robot

## Success Indicators

You'll know it's working when you see:

✅ `✅ Robot hub is running and calibrated!`
✅ `✅ BRIDGE ACTIVE - Camera and Robot Connected!`
✅ `✓ Sent to robot: SHOULDER -5° (total: X)`
✅ `[ROBOT] Shoulder → -10°` (robot confirms movement)

## Next Steps

- Fine-tune `--movement_step` and `--center_threshold` for your setup
- Try tracking different objects
- Adjust camera position for best view
- Monitor the robot movements and adjust bounds if needed

---

**That's it!** The bridge makes robot control fully automatic. Just run one command and watch your robot track objects! 🎉
