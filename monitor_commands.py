"""
Debug script to test if main.py detects bottles and writes commands
Run this while main.py is running to see what's happening
"""
import time
import os

COMMANDS_FILE = r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands.txt"

print("Monitoring commands.txt for changes...")
print("Make sure you're running: python main.py --use_robot --target_object bottle")
print("(Note: --use_robot flag is REQUIRED!)\n")

last_size = -1
last_content = ""

try:
    while True:
        try:
            if os.path.exists(COMMANDS_FILE):
                with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content != last_content:
                    if content:
                        print(f"✓ Command detected: {content.strip()}")
                    else:
                        print("  (File cleared)")
                    last_content = content
            else:
                print("! commands.txt doesn't exist yet")
                
        except Exception as e:
            print(f"Error reading file: {e}")
        
        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("\nStopped monitoring.")
