"""
Test BASE motor movement directly
"""
import sys
import subprocess
from pathlib import Path

# Generate a test script for BASE:20 command
test_script = """
from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop

hub = InventorHub()
motor_base = Motor(Port.A)

SPEED = 1000
BASE_MIN = -90
BASE_MAX = 90

print("Testing BASE motor...")
print(f"Current angle: {motor_base.angle()}")

# Move base by +20 degrees
current = motor_base.angle()
target = current + 20
if target > BASE_MAX:
    target = BASE_MAX

print(f"Moving from {current} to {target} degrees...")
motor_base.run_target(SPEED, target, Stop.HOLD, wait=True)

print(f"Final angle: {motor_base.angle()}")
print("Done!")
"""

# Write to temp file
temp_file = Path("_test_base_motor.py")
temp_file.write_text(test_script, encoding="utf-8")

# Run on hub
cmd = [
    sys.executable,
    "-m", "pybricksdev",
    "run", "ble",
    "-n", "test",
    str(temp_file)
]

print("Sending BASE:20 test to hub...")
print("Watch the robot - the BASE motor should rotate!")
print()

proc = subprocess.run(cmd, capture_output=False, text=True)

if proc.returncode == 0:
    print("\n✓ Command completed successfully!")
    print("Did the base motor move?")
else:
    print(f"\n✗ Command failed with code {proc.returncode}")
