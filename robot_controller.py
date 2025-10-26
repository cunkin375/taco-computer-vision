"""
Robot controller module for camera-based object tracking.
Provides calibration and incremental movement functions.
"""

from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

# ---- Motor bounds (degrees) ----
SHOULDER_MIN = 0
SHOULDER_MAX = 90
BASE_MIN = -90
BASE_MAX = 90
ELBOW_MIN = 0
ELBOW_MAX = 120
GRIPPER_MIN = 0
GRIPPER_MAX = 60

# ---- Settings ----
SPEED = 200

# ---- Global state ----
hub = None
motor_base = None
motor_shoulder = None
motor_elbow = None
motor_gripper = None

current_shoulder_angle = 0
current_base_angle = 0


def initialize():
    """Initialize the robot hub and motors."""
    global hub, motor_base, motor_shoulder, motor_elbow, motor_gripper
    global current_shoulder_angle, current_base_angle
    
    print("🤖 Initializing robot...")
    hub = InventorHub()
    
    motor_base = Motor(Port.A)
    motor_shoulder = Motor(Port.B)
    motor_elbow = Motor(Port.C)
    motor_gripper = Motor(Port.F)
    
    # Reset angles
    motor_base.reset_angle(0)
    motor_shoulder.reset_angle(0)
    motor_elbow.reset_angle(0)
    motor_gripper.reset_angle(0)
    
    current_shoulder_angle = 0
    current_base_angle = 0
    
    print("✅ Robot initialized!")


def calibrate_and_demo():
    """Run calibration and demo movements to verify robot functionality."""
    if motor_base is None:
        raise RuntimeError("Robot not initialized. Call initialize() first.")
    
    print("🤖 Running calibration and demo...")
    
    # Base demo
    print("Testing base rotation...")
    motor_base.run_target(SPEED, 45, Stop.HOLD, wait=True)
    wait(500)
    motor_base.run_target(SPEED, -45, Stop.HOLD, wait=True)
    wait(500)
    motor_base.run_target(SPEED, 0, Stop.HOLD, wait=True)
    wait(500)
    
    # Shoulder demo
    print("Testing shoulder movement...")
    motor_shoulder.run_target(SPEED, 45, Stop.HOLD, wait=True)
    wait(500)
    motor_shoulder.run_target(SPEED, 0, Stop.HOLD, wait=True)
    wait(500)
    
    # Elbow demo
    print("Testing elbow movement...")
    motor_elbow.run_target(SPEED, 60, Stop.HOLD, wait=True)
    wait(500)
    motor_elbow.run_target(SPEED, 0, Stop.HOLD, wait=True)
    wait(500)
    
    # Gripper demo
    print("Testing gripper...")
    motor_gripper.run_target(SPEED, 30, Stop.HOLD, wait=True)
    wait(500)
    motor_gripper.run_target(SPEED, 0, Stop.HOLD, wait=True)
    wait(500)
    
    print("✅ Calibration and demo complete!")


def move_shoulder(delta_degrees):
    """
    Move shoulder by delta_degrees (positive = up, negative = down).
    Respects bounds and updates current position.
    
    Args:
        delta_degrees: Amount to move in degrees (e.g., 5 or -5)
    
    Returns:
        True if movement succeeded, False if out of bounds
    """
    global current_shoulder_angle
    
    if motor_shoulder is None:
        raise RuntimeError("Robot not initialized. Call initialize() first.")
    
    target = current_shoulder_angle + delta_degrees
    
    # Clamp to bounds
    if target < SHOULDER_MIN:
        target = SHOULDER_MIN
        print(f"⚠️ Shoulder at minimum ({SHOULDER_MIN}°)")
    elif target > SHOULDER_MAX:
        target = SHOULDER_MAX
        print(f"⚠️ Shoulder at maximum ({SHOULDER_MAX}°)")
    
    if target != current_shoulder_angle:
        motor_shoulder.run_target(SPEED, target, Stop.HOLD, wait=False)
        current_shoulder_angle = target
        return True
    
    return False


def move_base(delta_degrees):
    """
    Move base by delta_degrees (positive = right, negative = left).
    Respects bounds and updates current position.
    
    Args:
        delta_degrees: Amount to move in degrees (e.g., 5 or -5)
    
    Returns:
        True if movement succeeded, False if out of bounds
    """
    global current_base_angle
    
    if motor_base is None:
        raise RuntimeError("Robot not initialized. Call initialize() first.")
    
    target = current_base_angle + delta_degrees
    
    # Clamp to bounds
    if target < BASE_MIN:
        target = BASE_MIN
        print(f"⚠️ Base at minimum ({BASE_MIN}°)")
    elif target > BASE_MAX:
        target = BASE_MAX
        print(f"⚠️ Base at maximum ({BASE_MAX}°)")
    
    if target != current_base_angle:
        motor_base.run_target(SPEED, target, Stop.HOLD, wait=False)
        current_base_angle = target
        return True
    
    return False


def get_current_angles():
    """Return current shoulder and base angles."""
    return {
        'shoulder': current_shoulder_angle,
        'base': current_base_angle
    }


def shutdown():
    """Stop all motors and release resources."""
    if motor_base:
        motor_base.stop()
    if motor_shoulder:
        motor_shoulder.stop()
    if motor_elbow:
        motor_elbow.stop()
    if motor_gripper:
        motor_gripper.stop()
    print("🛑 Robot shutdown complete")
