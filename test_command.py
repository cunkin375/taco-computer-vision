"""
Quick test to manually send a command and verify robot responds
"""
import time

COMMANDS_FILE = r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands.txt"

print("Writing test command to commands.txt...")
with open(COMMANDS_FILE, 'w', encoding='utf-8') as f:
    f.write("SHOULDER_UP\n")

print("Command written!")
print("Make sure robot_runner.py is running in another terminal.")
print("The shoulder should move UP by 30 degrees (fast and dramatic).")
print("\nWaiting 5 seconds before sending next command...")
time.sleep(5)

print("\nWriting SHOULDER_DOWN command...")
with open(COMMANDS_FILE, 'w', encoding='utf-8') as f:
    f.write("SHOULDER_DOWN\n")

print("Command written!")
print("The shoulder should move DOWN by 30 degrees.")
print("\nDone! Check if the robot moved.")
