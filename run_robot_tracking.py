"""
Launcher script that:
1. Uploads and runs robot_hub.py on the LEGO hub via pybricksdev
2. Waits for calibration to complete
3. Launches the camera tracking script
4. Sends movement commands to the robot

Usage:
    python run_robot_tracking.py --target_object bottle
"""

import argparse
import subprocess
import time
import sys
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Robot Camera Tracking System")
    parser.add_argument(
        '--target_object',
        required=True,
        type=str,
        help='Object name to track (e.g., "cup", "bottle", "person")'
    )
    parser.add_argument(
        '--robot_name',
        default='test',
        type=str,
        help='BLE name of the robot hub (default: "test")'
    )
    parser.add_argument(
        '--movement_step',
        default=5,
        type=int,
        help='Degrees to move per adjustment (default: 5)'
    )
    parser.add_argument(
        '--center_threshold',
        default=0.2,
        type=float,
        help='Center zone width as fraction of frame (default: 0.2)'
    )
    parser.add_argument(
        '--webcam_resolution',
        default=[640, 480],
        type=int,
        nargs=2,
        help='Webcam resolution width height (default: 640 480)'
    )
    parser.add_argument(
        '--skip_calibration',
        action='store_true',
        help='Skip robot calibration (assume robot is already running)'
    )
    return parser.parse_args()


def upload_and_run_robot(robot_name):
    """Upload robot_hub.py to the LEGO hub and start it."""
    print("\n" + "="*60)
    print("🤖 Step 1: Uploading robot program to hub...")
    print("="*60)
    
    if not os.path.exists('robot_hub.py'):
        print("❌ Error: robot_hub.py not found!")
        print("   Make sure robot_hub.py is in the current directory.")
        return False
    
    cmd = [
        sys.executable, '-m', 'pybricksdev',
        'run', 'ble',
        '-n', robot_name,
        'robot_hub.py'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("\n⏳ Uploading and running calibration on robot...")
    print("   (This will take ~20-30 seconds for calibration to complete)")
    print("   Watch the hub for calibration movements!\n")
    
    try:
        # Start the robot program in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor output for calibration completion
        calibration_done = False
        for line in iter(process.stdout.readline, ''):
            print(f"[ROBOT] {line.rstrip()}")
            if "Calibration complete" in line or "Robot ready" in line:
                calibration_done = True
                break
            # Check if process has ended prematurely
            if process.poll() is not None:
                break
        
        if not calibration_done:
            print("\n⏳ Waiting additional time for calibration...")
            time.sleep(5)
        
        print("\n✅ Robot calibration complete!")
        return process
        
    except FileNotFoundError:
        print("\n❌ Error: pybricksdev not found!")
        print("   Install with: pip install pybricksdev")
        return None
    except Exception as e:
        print(f"\n❌ Error starting robot: {e}")
        return None


def main():
    args = parse_args()
    
    print("\n" + "="*60)
    print("🎯 ROBOT CAMERA TRACKING SYSTEM")
    print("="*60)
    
    # Step 1: Upload and calibrate robot (unless skipped)
    robot_process = None
    if not args.skip_calibration:
        robot_process = upload_and_run_robot(args.robot_name)
        if not robot_process:
            print("\n❌ Failed to start robot. Exiting.")
            return 1
    else:
        print("\n⏭️  Skipping robot calibration (--skip_calibration)")
    
    # Step 2: Start camera tracking
    print("\n" + "="*60)
    print("📷 Step 2: Starting camera tracking...")
    print("="*60)
    print(f"Target object: {args.target_object}")
    print(f"Movement step: {args.movement_step}°")
    print(f"Center threshold: {args.center_threshold}")
    print("\nPress 'q' in the video window to quit\n")
    
    time.sleep(2)  # Brief pause before starting camera
    
    # Import and run main camera script
    try:
        # Modify sys.argv to pass arguments to main.py
        original_argv = sys.argv.copy()
        sys.argv = [
            'main.py',
            '--target_object', args.target_object,
            '--movement_step', str(args.movement_step),
            '--center_threshold', str(args.center_threshold),
            '--webcam_resolution', str(args.webcam_resolution[0]), str(args.webcam_resolution[1]),
            '--use_robot'
        ]
        
        # Import and run main
        import main
        main.main()
        
        # Restore argv
        sys.argv = original_argv
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Camera tracking error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if robot_process:
            print("\n🛑 Stopping robot...")
            robot_process.terminate()
            try:
                robot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                robot_process.kill()
        
        print("\n✅ Shutdown complete")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
