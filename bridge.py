"""
Bridge script that connects camera tracking to robot control.
Automatically starts robot hub, runs calibration, then starts camera tracking.
Pipes ROBOT_CMD output from camera to the robot hub for execution.

Usage:
    python bridge.py --target_object bottle
"""

import subprocess
import sys
import argparse
import re
import time
import threading
import queue

def parse_args():
    parser = argparse.ArgumentParser(description="Robot Camera Tracking Bridge")
    parser.add_argument('--target_object', required=True, help='Object to track')
    parser.add_argument('--robot_name', default='test', help='BLE name of robot hub')
    parser.add_argument('--movement_step', default=5, type=int, help='Movement step in degrees')
    parser.add_argument('--center_threshold', default=0.2, type=float, help='Center zone threshold')
    parser.add_argument('--webcam_resolution', default=[640, 480], nargs=2, type=int)
    parser.add_argument('--skip_calibration', action='store_true', help='Skip robot initialization (robot already running)')
    return parser.parse_args()


def read_output(pipe, output_queue, prefix=""):
    """Read from pipe and put lines in queue."""
    try:
        for line in iter(pipe.readline, ''):
            if line:
                output_queue.put((prefix, line.rstrip()))
    except Exception as e:
        output_queue.put((prefix, f"Error reading: {e}"))
    finally:
        pipe.close()


def start_robot(robot_name):
    """Start robot hub program via pybricksdev."""
    print("\n" + "="*60)
    print("🤖 STEP 1: Starting robot hub...")
    print("="*60)
    
    cmd = [
        sys.executable, '-m', 'pybricksdev',
        'run', 'ble',
        '-n', robot_name,
        'robot_hub.py'
    ]
    
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor robot startup
        print("⏳ Uploading robot_hub.py to LEGO hub...")
        calibration_complete = False
        
        for line in iter(process.stdout.readline, ''):
            line = line.rstrip()
            print(f"[ROBOT] {line}")
            
            if "Calibration complete" in line or "Robot ready" in line:
                calibration_complete = True
                break
            
            # Check if process died
            if process.poll() is not None:
                print("\n❌ Robot process ended unexpectedly")
                return None, None
        
        if not calibration_complete:
            print("\n⏳ Waiting for calibration to complete...")
            time.sleep(3)
        
        print("\n✅ Robot hub is running and calibrated!")
        
        # Start thread to continue reading robot output
        robot_queue = queue.Queue()
        robot_thread = threading.Thread(
            target=read_output,
            args=(process.stdout, robot_queue, "ROBOT"),
            daemon=True
        )
        robot_thread.start()
        
        return process, robot_queue
        
    except FileNotFoundError:
        print("\n❌ Error: pybricksdev not found!")
        print("   Install with: pip install pybricksdev")
        return None, None
    except Exception as e:
        print(f"\n❌ Error starting robot: {e}")
        return None, None


def start_camera(args):
    """Start camera tracking script."""
    print("\n" + "="*60)
    print("📷 STEP 2: Starting camera tracking...")
    print("="*60)
    print(f"Target: {args.target_object}")
    print(f"Movement step: {args.movement_step}°")
    print(f"Center threshold: {args.center_threshold}\n")
    
    cmd = [
        sys.executable, 'main.py',
        '--target_object', args.target_object,
        '--movement_step', str(args.movement_step),
        '--center_threshold', str(args.center_threshold),
        '--webcam_resolution', str(args.webcam_resolution[0]), str(args.webcam_resolution[1]),
        '--use_robot'
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Start thread to read camera output
        camera_queue = queue.Queue()
        camera_thread = threading.Thread(
            target=read_output,
            args=(process.stdout, camera_queue, "CAMERA"),
            daemon=True
        )
        camera_thread.start()
        
        return process, camera_queue
        
    except Exception as e:
        print(f"\n❌ Error starting camera: {e}")
        return None, None


def send_command_to_robot(robot_process, motor, degrees):
    """Send movement command to robot hub via stdin."""
    try:
        if robot_process and robot_process.stdin and not robot_process.stdin.closed:
            # Format command for robot to execute
            # We send Python code that calls the move functions directly
            if motor == "BASE":
                command = f"move_base({degrees})\n"
            elif motor == "SHOULDER":
                command = f"move_shoulder({degrees})\n"
            else:
                return False
            
            robot_process.stdin.write(command)
            robot_process.stdin.flush()
            return True
    except Exception as e:
        print(f"⚠️  Error sending command to robot: {e}")
    return False


def main():
    args = parse_args()
    
    print("\n" + "="*70)
    print("🌉 ROBOT CAMERA TRACKING BRIDGE")
    print("="*70)
    print("\nThis script will:")
    print("  1. Start robot hub and run calibration")
    print("  2. Start camera tracking")
    print("  3. Automatically send movement commands from camera to robot")
    print("\nPress Ctrl+C to stop everything\n")
    
    robot_process = None
    camera_process = None
    robot_queue = None
    camera_queue = None
    
    try:
        # Step 1: Start robot
        if not args.skip_calibration:
            robot_process, robot_queue = start_robot(args.robot_name)
            if not robot_process:
                print("\n❌ Failed to start robot. Exiting.")
                return 1
            time.sleep(1)
        else:
            print("\n⏭️  Skipping robot initialization (--skip_calibration)")
        
        # Step 2: Start camera
        camera_process, camera_queue = start_camera(args)
        if not camera_process:
            print("\n❌ Failed to start camera. Exiting.")
            if robot_process:
                robot_process.terminate()
            return 1
        
        print("\n" + "="*70)
        print("✅ BRIDGE ACTIVE - Camera and Robot Connected!")
        print("="*70)
        print("\nMonitoring camera output and sending commands to robot...")
        print("Press 'q' in the video window or Ctrl+C here to stop\n")
        
        # Main loop: process output from both queues
        command_count = 0
        last_command_time = 0
        MIN_COMMAND_INTERVAL = 0.3  # Minimum seconds between commands (debouncing)
        
        while True:
            # Check camera output
            if camera_queue:
                try:
                    while not camera_queue.empty():
                        prefix, line = camera_queue.get_nowait()
                        print(f"[{prefix}] {line}")
                        
                        # Parse robot commands
                        match = re.match(r'ROBOT_CMD:(\w+):(-?\d+)', line)
                        if match:
                            motor = match.group(1)
                            degrees = int(match.group(2))
                            
                            # Debounce commands to prevent overload
                            current_time = time.time()
                            if current_time - last_command_time >= MIN_COMMAND_INTERVAL:
                                if send_command_to_robot(robot_process, motor, degrees):
                                    command_count += 1
                                    print(f"  ✓ Sent to robot: {motor} {degrees:+d}° (total: {command_count})")
                                    last_command_time = current_time
                                else:
                                    print(f"  ✗ Failed to send command")
                        
                        # Check for stop command
                        if "ROBOT_CMD:STOP" in line:
                            print("\n🛑 Stop command received")
                            raise KeyboardInterrupt
                            
                except queue.Empty:
                    pass
            
            # Check robot output
            if robot_queue:
                try:
                    while not robot_queue.empty():
                        prefix, line = robot_queue.get_nowait()
                        print(f"[{prefix}] {line}")
                except queue.Empty:
                    pass
            
            # Check if processes are still running
            if camera_process and camera_process.poll() is not None:
                print("\n📷 Camera process ended")
                break
            
            if robot_process and robot_process.poll() is not None:
                print("\n🤖 Robot process ended")
                break
            
            time.sleep(0.05)  # Small delay to prevent CPU overload
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        print("\n🛑 Shutting down...")
        
        # Stop camera
        if camera_process:
            print("  Stopping camera...")
            camera_process.terminate()
            try:
                camera_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                camera_process.kill()
        
        # Stop robot
        if robot_process:
            print("  Stopping robot...")
            robot_process.terminate()
            try:
                robot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                robot_process.kill()
        
        print("\n✅ Bridge closed")
        print(f"   Total commands sent: {command_count if 'command_count' in locals() else 0}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
