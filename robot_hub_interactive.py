"""
Robot hub program with command input support.
This version attempts to read commands from stdin when available.

Upload and run with:
    python -m pybricksdev run ble -n test robot_hub_interactive.py
"""

from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait
import sys
import select

# ---- Initialize hub ----
hub = InventorHub()

# ---- Motors ----
motor_base = Motor(Port.A)
motor_shoulder = Motor(Port.B)
motor_elbow = Motor(Port.C)
motor_gripper = Motor(Port.F)

# ---- Settings ----
SPEED = 200

# ---- Motor bounds (degrees) ----
SHOULDER_MIN = 0
SHOULDER_MAX = 90
BASE_MIN = -90
BASE_MAX = 90

# ---- Global state ----
current_shoulder_angle = 0
current_base_angle = 0

# ---- Reset angles ----
motor_base.reset_angle(0)
motor_shoulder.reset_angle(0)
motor_elbow.reset_angle(0)
motor_gripper.reset_angle(0)

print("🤖 Robot hub initialized!")

# ---- Calibration and demo ----
def calibrate():
    """Run calibration movements to verify robot functionality."""
    print("🤖 Running calibration demo...")
    
    # Base
    print("Testing base rotation...")
    motor_base.run_target(SPEED, 45, Stop.HOLD, wait=True)
    wait(500)
    motor_base.run_target(SPEED, -45, Stop.HOLD, wait=True)
    wait(500)
    motor_base.run_target(SPEED, 0, Stop.HOLD, wait=True)
    wait(500)
    
    # Shoulder
    print("Testing shoulder movement...")
    motor_shoulder.run_target(SPEED, 45, Stop.HOLD, wait=True)
    wait(500)
    motor_shoulder.run_target(SPEED, 0, Stop.HOLD, wait=True)
    wait(500)
    
    # Elbow
    print("Testing elbow movement...")
    motor_elbow.run_target(SPEED, 60, Stop.HOLD, wait=True)
    wait(500)
    motor_elbow.run_target(SPEED, 0, Stop.HOLD, wait=True)
    wait(500)
    
    # Gripper
    print("Testing gripper...")
    motor_gripper.run_target(SPEED, 30, Stop.HOLD, wait=True)
    wait(500)
    motor_gripper.run_target(SPEED, 0, Stop.HOLD, wait=True)
    wait(500)
    
    print("✅ Calibration complete!")

# ---- Movement functions ----
def move_base(delta):
    """Move base by delta degrees with bounds checking."""
    global current_base_angle
    target = current_base_angle + delta
    
    if target < BASE_MIN:
        target = BASE_MIN
        print(f"⚠️ Base at minimum ({BASE_MIN}°)")
    elif target > BASE_MAX:
        target = BASE_MAX
        print(f"⚠️ Base at maximum ({BASE_MAX}°)")
    
    if target != current_base_angle:
        motor_base.run_target(SPEED, target, Stop.HOLD, wait=False)
        current_base_angle = target
        print(f"Base → {target}°")

def move_shoulder(delta):
    """Move shoulder by delta degrees with bounds checking."""
    global current_shoulder_angle
    target = current_shoulder_angle + delta
    
    if target < SHOULDER_MIN:
        target = SHOULDER_MIN
        print(f"⚠️ Shoulder at minimum ({SHOULDER_MIN}°)")
    elif target > SHOULDER_MAX:
        target = SHOULDER_MAX
        print(f"⚠️ Shoulder at maximum ({SHOULDER_MAX}°)")
    
    if target != current_shoulder_angle:
        motor_shoulder.run_target(SPEED, target, Stop.HOLD, wait=False)
        current_shoulder_angle = target
        print(f"Shoulder → {target}°")

def process_command(cmd_string):
    """Process a command string like 'BASE:5' or 'SHOULDER:-5'."""
    try:
        parts = cmd_string.strip().split(':')
        if len(parts) != 2:
            return
        
        motor_name = parts[0].upper()
        degrees = int(parts[1])
        
        if motor_name == 'BASE':
            move_base(degrees)
        elif motor_name == 'SHOULDER':
            move_shoulder(degrees)
        else:
            print(f"Unknown motor: {motor_name}")
    except Exception as e:
        print(f"Error processing command '{cmd_string}': {e}")

# ---- Run calibration ----
calibrate()

# ---- Command listener loop ----
print("🎯 Robot ready! Waiting for camera commands...")
print("Commands: BASE:5, SHOULDER:-5, etc.")
print("Type commands directly or send via bridge script")

# Keep running and process commands
try:
    command_buffer = ""
    while True:
        # Try to read input if available (this works in REPL mode)
        try:
            # Check if input is available (non-blocking on some systems)
            if select.select([sys.stdin], [], [], 0.0)[0]:
                char = sys.stdin.read(1)
                if char:
                    if char == '\n':
                        if command_buffer:
                            process_command(command_buffer)
                            command_buffer = ""
                    else:
                        command_buffer += char
        except:
            # select not available or stdin not readable, just continue
            pass
        
        wait(50)
        
except KeyboardInterrupt:
    print("\n🛑 Stopping robot...")
    motor_base.stop()
    motor_shoulder.stop()
    motor_elbow.stop()
    motor_gripper.stop()
    print("✅ Robot stopped")
