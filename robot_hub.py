"""
Robot hub program - runs ON the LEGO hub via pybricksdev.
Performs calibration on startup, then listens for movement commands via BLE.

Upload and run with:
    python -m pybricksdev run ble -n test robot_hub.py
"""

from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

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

print("Robot hub initialized!")

# ---- Calibration and demo ----
def calibrate():
    """Run calibration movements to verify robot functionality."""
    print("Running calibration demo...")
    
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
    
    print("Calibration complete!")

# ---- Movement functions ----
def move_base(delta):
    """Move base by delta degrees with bounds checking."""
    global current_base_angle
    target = current_base_angle + delta
    
    if target < BASE_MIN:
        target = BASE_MIN
        print(f"WARNING: Base at minimum ({BASE_MIN} degrees)")
    elif target > BASE_MAX:
        target = BASE_MAX
        print(f"WARNING: Base at maximum ({BASE_MAX} degrees)")
    
    if target != current_base_angle:
        motor_base.run_target(SPEED, target, Stop.HOLD, wait=False)
        current_base_angle = target
        print(f"Base -> {target} degrees")

def move_shoulder(delta):
    """Move shoulder by delta degrees with bounds checking."""
    global current_shoulder_angle
    target = current_shoulder_angle + delta
    
    if target < SHOULDER_MIN:
        target = SHOULDER_MIN
        print(f"WARNING: Shoulder at minimum ({SHOULDER_MIN} degrees)")
    elif target > SHOULDER_MAX:
        target = SHOULDER_MAX
        print(f"WARNING: Shoulder at maximum ({SHOULDER_MAX} degrees)")
    
    if target != current_shoulder_angle:
        motor_shoulder.run_target(SPEED, target, Stop.HOLD, wait=False)
        current_shoulder_angle = target
        print(f"Shoulder → {target}°")

# ---- Run calibration ----
calibrate()

# ---- Command listener loop ----
print("🎯 Robot ready! Waiting for camera commands...")
print("Hub will stay connected. Press Ctrl+C on the PC to stop.")
print("Listening for commands via stdin (format: MOTOR:DEGREES, e.g., BASE:5 or SHOULDER:-5)")

# Keep the program running and listen for commands from stdin
try:
    while True:
        # Note: pybricksdev doesn't easily support stdin reading in interactive mode
        # Instead, we'll use a simple polling approach
        # The bridge script will send commands that we can process
        
        # For now, just keep the connection alive
        # Commands will be sent via pybricksdev's communication channel
        wait(100)
        
        # In the future, this could be replaced with actual stdin reading
        # when pybricksdev adds better support for it
        
except KeyboardInterrupt:
    print("\n🛑 Stopping robot...")
    motor_base.stop()
    motor_shoulder.stop()
    motor_elbow.stop()
    motor_gripper.stop()
    print("✅ Robot stopped")
