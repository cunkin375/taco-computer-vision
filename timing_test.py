"""
Test to see real-time timing between command written and robot movement
Run this while both main.py and robot_runner.py are running
"""
import time
import os
from datetime import datetime

COMMANDS_FILE = r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands.txt"

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {msg}")

log("Monitoring commands.txt for timing analysis...")
log("Make sure robot_runner.py is running in another terminal!")
log("=" * 70)

last_content = ""
last_write_time = None

try:
    while True:
        if os.path.exists(COMMANDS_FILE):
            current_content = open(COMMANDS_FILE, 'r').read().strip()
            
            if current_content != last_content:
                if current_content:
                    log(f"📝 COMMAND WRITTEN: '{current_content}'")
                    last_write_time = time.time()
                else:
                    if last_write_time:
                        elapsed = time.time() - last_write_time
                        log(f"🗑️  COMMAND CLEARED (took {elapsed:.2f}s from write to clear)")
                        log(f"   ⮑ This means robot_runner took {elapsed:.2f}s to process")
                    else:
                        log(f"🗑️  File cleared")
                
                last_content = current_content
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    log("\nStopped monitoring")
