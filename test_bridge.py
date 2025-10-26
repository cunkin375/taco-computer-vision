"""
Simple test to verify bridge.py is working correctly.
This simulates camera output without actually running YOLO.
"""

import time

print("🤖 Robot control enabled")
print("   NOTE: Make sure robot_hub.py is already running on the hub!")
print("   This script will send movement commands via console output.")

print("\nSimulating camera tracking...\n")

# Simulate detection sequence
commands = [
    ("Look left", "ROBOT_CMD:SHOULDER:-5"),
    ("Look left", "ROBOT_CMD:SHOULDER:-5"),
    ("Look left", "ROBOT_CMD:SHOULDER:-5"),
    ("Centered", None),
    ("Look right", "ROBOT_CMD:SHOULDER:5"),
    ("Look right", "ROBOT_CMD:SHOULDER:5"),
    ("Centered", None),
    ("Look left", "ROBOT_CMD:SHOULDER:-5"),
    ("Centered", None),
]

try:
    for direction, cmd in commands:
        print(direction)
        if cmd:
            print(cmd)
        time.sleep(1)  # Wait 1 second between commands
    
    print("\nROBOT_CMD:STOP")
    print("\n✅ Test complete!")

except KeyboardInterrupt:
    print("\n\n⚠️ Test interrupted")
    print("ROBOT_CMD:STOP")
