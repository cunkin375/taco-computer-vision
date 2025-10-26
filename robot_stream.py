"""
Persistent connection bridge for instant robot tracking.
Launches robot_hub.py on the LEGO hub and streams commands from commands.txt via stdin.
This eliminates Bluetooth reconnection overhead for real-time tracking.
"""

import subprocess
import time
import os
import sys

# Absolute path to the shared commands file
COMMANDS_FILE_PATH = r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands.txt"
HUB_SCRIPT_PATH = r"C:\Users\hackathon\dev\taco\taco-computer-vision\robot_hub.py"
COMMANDS_LOG_PATH = r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands_log.txt"

# Path to virtual environment's pybricksdev
VENV_PYBRICKSDEV = r"C:\Users\hackathon\dev\taco\taco-computer-vision\taco\Scripts\pybricksdev.exe"

def main():
    print("=" * 60)
    print("PERSISTENT ROBOT TRACKING BRIDGE")
    print("=" * 60)
    print(f"Commands file: {COMMANDS_FILE_PATH}")
    print(f"Hub script: {HUB_SCRIPT_PATH}")
    print(f"Command log: {COMMANDS_LOG_PATH}")
    print()
    
    # Ensure commands file exists
    if not os.path.exists(COMMANDS_FILE_PATH):
        print(f"Creating commands file: {COMMANDS_FILE_PATH}")
        with open(COMMANDS_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("")
    
    # Initialize log file with header
    with open(COMMANDS_LOG_PATH, 'w', encoding='utf-8') as log:
        log.write("=" * 60 + "\n")
        log.write("ROBOT TRACKING COMMAND LOG\n")
        log.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("=" * 60 + "\n\n")
    
    # Launch hub script with persistent connection
    print("🔷 Connecting to LEGO hub via Bluetooth...")
    print("   This may take 5-10 seconds on first connection...")
    print()
    
    try:
        # Start pybricksdev with hub script - keeps connection open
        # Use virtual environment's pybricksdev if available, otherwise use system
        pybricksdev_cmd = VENV_PYBRICKSDEV if os.path.exists(VENV_PYBRICKSDEV) else "pybricksdev"
        
        process = subprocess.Popen(
            [pybricksdev_cmd, "run", "ble", HUB_SCRIPT_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        print("✓ Hub process started!")
        print("✓ Waiting for hub initialization...")
        
        # Create a thread to continuously print hub output for debugging
        import threading
        def print_hub_output():
            for line in process.stdout:
                print(f"[HUB] {line.rstrip()}")
        
        output_thread = threading.Thread(target=print_hub_output, daemon=True)
        output_thread.start()
        
        # Give hub time to initialize motors and print any startup errors
        time.sleep(3)
        
        # Check if process already died
        if process.poll() is not None:
            print("\n❌ ERROR: Hub process exited during initialization!")
            sys.exit(1)
        
        print()
        print("=" * 60)
        print("🤖 ROBOT READY - STREAMING COMMANDS")
        print("=" * 60)
        print("Now run: python main.py --use_robot --target_object bottle")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()
        
        last_command = None
        command_count = 0
        start_time = time.time()
        
        # Main streaming loop - read commands.txt and send to hub stdin
        while process.poll() is None:  # While hub process is running
            try:
                # Read current command from file
                if os.path.exists(COMMANDS_FILE_PATH):
                    with open(COMMANDS_FILE_PATH, 'r', encoding='utf-8') as f:
                        command = f.read().strip()
                    
                    # Only send if command changed (avoid spam)
                    if command and command != last_command:
                        # Send to hub via stdin
                        process.stdin.write(command + '\n')
                        process.stdin.flush()
                        
                        command_count += 1
                        elapsed = time.time() - start_time
                        timestamp = time.strftime('%H:%M:%S')
                        
                        # Print to console
                        print(f"[{command_count:04d}] {timestamp} ➜ {command}")
                        
                        # Log to file with timestamp and elapsed time
                        with open(COMMANDS_LOG_PATH, 'a', encoding='utf-8') as log:
                            log.write(f"[{command_count:04d}] {timestamp} (+{elapsed:.1f}s) | {command}\n")
                        
                        last_command = command
                    
                    elif not command and last_command:
                        # Command cleared - reset state
                        last_command = None
                
                # Small delay to avoid CPU spinning
                time.sleep(0.05)  # 50ms = ~20Hz polling
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Stopping bridge...")
                break
            except Exception as e:
                print(f"Error reading/sending command: {e}")
                time.sleep(0.1)
        
        # Clean shutdown
        print("\n🛑 Terminating hub connection...")
        process.stdin.close()
        process.terminate()
        process.wait(timeout=5)
        
        # Write session summary to log
        with open(COMMANDS_LOG_PATH, 'a', encoding='utf-8') as log:
            log.write("\n" + "=" * 60 + "\n")
            log.write(f"Session ended: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"Total commands: {command_count}\n")
            log.write("=" * 60 + "\n")
        
        print(f"✓ Bridge stopped cleanly")
        print(f"✓ Commands logged to: {COMMANDS_LOG_PATH}")
        print(f"✓ Total commands sent: {command_count}")
        
    except FileNotFoundError:
        print("❌ ERROR: pybricksdev not found!")
        print("   Install with: pip install pybricksdev")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
