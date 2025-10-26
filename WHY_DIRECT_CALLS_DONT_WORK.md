# Why Direct Motor Calls Don't Work

## The Problem

You tried to use:
```python
from robot import goto_angle, motor_shoulder
goto_angle(motor_shoulder, -5)
```

This **doesn't work** because:

## Architecture Explanation

### Two Separate Systems:

1. **Your PC (Windows)** - Runs `main.py`
   - Has Python, OpenCV, YOLO
   - Has your webcam
   - **Does NOT have** pybricks library
   - **Cannot** directly control LEGO motors

2. **LEGO Hub (Pybricks OS)** - Runs `robot_hub.py`
   - Has pybricks library
   - Connected to motors
   - **Does NOT have** camera, OpenCV, or YOLO
   - **Cannot** run computer vision code

### Why the Import Fails:

```python
from robot import goto_angle  # ❌ This tries to import pybricks code
```

When you run `main.py` on your PC:
- Python tries to import `robot.py`
- `robot.py` contains `from pybricks.hubs import InventorHub`
- Your PC doesn't have pybricks installed (and can't, it's hub-only)
- **Result:** Import error or the functions won't work

## The Solution: Communication Between PC and Hub

You need a **communication channel** between the two systems:

```
┌─────────────────┐         Commands          ┌─────────────────┐
│   Your PC       │  ──────────────────────>  │   LEGO Hub      │
│   main.py       │                            │   robot_hub.py  │
│   + Camera      │  <──────────────────────  │   + Motors      │
│   + YOLO        │         Feedback           │                 │
└─────────────────┘                            └─────────────────┘
```

### Current Status (What You Have Now):

✅ **`main.py`** outputs commands:
```
ROBOT_CMD:SHOULDER:5
ROBOT_CMD:SHOULDER:-5
```

✅ **`robot_hub.py`** runs on hub and stays connected

❌ **Missing:** Bridge to send commands from PC to hub

### Option 1: Manual Testing (Works Now)

**Terminal 1:**
```powershell
python -m pybricksdev run ble -n test robot_hub.py
```

**Terminal 2:**
```powershell
python .\main.py --target_object bottle --use_robot
```

**Manual step:** Watch Terminal 2 for commands, then manually test movement in Terminal 1

### Option 2: Automated Bridge (Needs Implementation)

Create a script that:
1. Starts `robot_hub.py` on the hub
2. Starts `main.py` on PC
3. Captures `ROBOT_CMD` output from main.py
4. Sends commands to robot_hub.py via pybricksdev

**This is what `bridge.py` and `run_robot_tracking.py` are designed to do** (work in progress)

### Option 3: Shared File/Socket (Alternative)

- PC writes commands to a file/socket
- Hub reads from file/socket and executes
- Requires both processes to have access to shared resource

## What Changed in Your Code

### Before (Broken):
```python
from robot import goto_angle, motor_shoulder  # ❌ Can't import hub code on PC

if robot_controller:
    goto_angle(motor_shoulder, -5)  # ❌ motor_shoulder doesn't exist on PC
```

### After (Working):
```python
# No imports from robot.py ✅

if robot_controller:
    print(f"ROBOT_CMD:SHOULDER:-5")  # ✅ Just output the command
```

## Next Steps to Get Full Automation

### Quick Win: Use pybricksdev Interactive Terminal

You can send commands to a running hub program:

1. Start robot:
```powershell
python -m pybricksdev run ble -n test robot_hub.py
```

2. While it's running, you could potentially send commands through the pybricksdev connection (this would require modifying robot_hub.py to read from a specific input source)

### Full Solution: Implement the Bridge

The `run_robot_tracking.py` script needs to:
1. Start both processes
2. Parse stdout from `main.py`
3. Send extracted commands to `robot_hub.py` via pybricksdev's stdin

This requires understanding pybricksdev's API for bidirectional communication.

## Summary

| What | Where it Runs | Can Control Motors? | Can Run Camera? |
|------|---------------|---------------------|-----------------|
| `main.py` | Your PC | ❌ No | ✅ Yes |
| `robot_hub.py` | LEGO Hub | ✅ Yes | ❌ No |
| `bridge.py` | Your PC | ❌ No (just forwards) | ❌ No |

**Bottom line:** 
- PC code can't directly call motor functions
- You need a communication bridge
- Current workaround: commands are printed, you verify they're correct
- Future: automated bridge sends commands to hub

Would you like me to implement a working automated bridge using subprocess communication?
