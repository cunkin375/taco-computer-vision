"""
Simple test to verify hub connection
"""
import subprocess
import sys

HUB_NAME = "test"  # Change this to match your hub's actual name

print(f"Attempting to connect to hub named '{HUB_NAME}'...")
print("Make sure:")
print("  1. Hub is powered on")
print("  2. Hub is running Pybricks firmware (shows Pybricks logo)")
print("  3. Hub is not connected to any other device")
print("  4. Bluetooth is enabled on your PC")
print("\nSearching...\n")

# Try to run a simple command
cmd = [
    sys.executable,
    "-m", "pybricksdev",
    "run", "ble",
    "-n", HUB_NAME,
    "-"  # Read from stdin
]

try:
    # Send a minimal script
    test_script = """
from pybricks.hubs import InventorHub
hub = InventorHub()
print("Connection successful!")
"""
    
    proc = subprocess.run(
        cmd,
        input=test_script,
        text=True,
        capture_output=True,
        timeout=30
    )
    
    print("STDOUT:")
    print(proc.stdout)
    print("\nSTDERR:")
    print(proc.stderr)
    print(f"\nReturn code: {proc.returncode}")
    
    if proc.returncode == 0:
        print("\n✅ SUCCESS! Hub is connected and working.")
    else:
        print("\n❌ FAILED! Check the errors above.")
        
except subprocess.TimeoutExpired:
    print("\n❌ TIMEOUT! Could not find or connect to hub within 30 seconds.")
    print("Check that the hub is on and in Pybricks mode.")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
