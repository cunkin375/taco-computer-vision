import argparse
import cv2
import os
import time

import supervision as sv
from ultralytics import YOLO

# Absolute path to the shared commands file
COMMANDS_FILE_PATH = r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands.txt"

def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 Video Capture with Robot Tracking")
    parser.add_argument(
        '--webcam_resolution',
        default=[640, 480],
        type=int,
        nargs=2,
        help='Webcam resolution width height'
    )
    parser.add_argument(
        '--target_object',
        default=None,
        type=str,
        help='Object name to track (must match a class in names.txt, e.g. "cup", "bottle", "person")'
    )
    parser.add_argument(
        '--center_threshold',
        default=0.2,
        type=float,
        help='Fraction of frame width for center zone (default: 0.2 = 20%% of width centered)'
    )
    parser.add_argument(
        '--use_robot',
        action='store_true',
        help='Enable robot motor control via commands.txt'
    )
    parser.add_argument(
        '--camera',
        default=0,
        type=int,
        help='Camera index (default: 0)'
    )
    return parser.parse_args()

def main():
    args = parse_args()
    frame_width, frame_height = args.webcam_resolution
    frame_center_x = frame_width / 2
    
    # Calculate center zone boundaries
    center_zone_width = frame_width * args.center_threshold
    center_left = frame_center_x - (center_zone_width / 2)
    center_right = frame_center_x + (center_zone_width / 2)

    # Robot control setup
    robot_enabled = args.use_robot
    last_command_time = 0
    command_cooldown = 0.1  # 100ms between commands for fast tracking
    
    if robot_enabled:
        print("[STARTUP] Robot control enabled: True")
        print(f"[STARTUP] Target object: {args.target_object}")
        print(f"[STARTUP] Center zone: {center_left} to {center_right}")
        print(f"[STARTUP] ✓ Robot commands will be sent to: {COMMANDS_FILE_PATH}")
        print()
        
        # Initialize commands file
        with open(COMMANDS_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("")
    else:
        print("[STARTUP] ✗ Robot control disabled (use --use_robot flag to enable)")

    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    if not cap.isOpened():
        raise SystemExit(f"Could not open camera at index {args.camera}. Try running `webcam.py` to enumerate camera indices.")

    # Load YOLO model
    model = YOLO("yolov8l.pt")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to read frame from camera, stopping")
            break
            
        # Run YOLO model
        result = model(frame)[0]
        
        # Draw output frame
        out = frame.copy()
        
        # Process YOLO detections
        try:
            xyxy = result.boxes.xyxy.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)
            confidences = result.boxes.conf.cpu().numpy()
        except Exception:
            xyxy = []
            class_ids = []
            confidences = []

        # Track if we found our target object
        target_found = False
        command_to_send = None

        for i, (box, class_id, conf) in enumerate(zip(xyxy, class_ids, confidences)):
            x1, y1, x2, y2 = map(int, box)
            
            # Get class name safely using YOLO's built-in names
            class_name = model.names.get(class_id, f"class_{class_id}")
            label = f"{class_name} {conf:.2f}"
            
            # Check if this is our target object
            if args.target_object and class_name == args.target_object:
                target_found = True
                
                # Only send robot commands if enabled and cooldown has passed
                current_time = time.time()
                if robot_enabled and (current_time - last_command_time) >= command_cooldown:
                    
                    # Calculate bounding box center for left/right determination
                    bbox_center_x = (x1 + x2) / 2
                    bbox_center_y = (y1 + y2) / 2
                    
                    # Horizontal tracking (base motor) - 40 DEGREE MOVEMENTS
                    if bbox_center_x < center_left:
                        command_to_send = 'BASE:40\n'  # Rotate base left 40 degrees
                        print(f"⬅️  LEFT")
                    elif bbox_center_x > center_right:
                        command_to_send = 'BASE:-40\n'  # Rotate base right 40 degrees
                        print(f"➡️  RIGHT")
                    else:
                        # Vertical tracking (shoulder motor) when horizontally centered
                        frame_center_y = frame_height / 2
                        if bbox_center_y < frame_center_y - 50:
                            command_to_send = 'SHOULDER_UP\n'
                            print(f"⬆️  UP")
                        elif bbox_center_y > frame_center_y + 50:
                            command_to_send = 'SHOULDER_DOWN\n'
                            print(f"⬇️  DOWN")
                        else:
                            command_to_send = None  # Both centered

                    # Update last command time if we're sending a command
                    if command_to_send is not None:
                        last_command_time = current_time

            cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if label:
                cv2.putText(out, label, (x1, max(10, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Write command to file if we have one
        if command_to_send is not None:
            with open(COMMANDS_FILE_PATH, 'w', encoding='utf-8') as qf:
                qf.write(command_to_send)
            print(f"📤 SENT: {command_to_send.strip()}")
        elif robot_enabled and args.target_object and not target_found:
            # Clear command file if target is lost
            with open(COMMANDS_FILE_PATH, 'w', encoding='utf-8') as qf:
                qf.write("")

        # Show the frame
        cv2.imshow("YOLOv8 Tracking", out)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    if robot_enabled:
        # Send STOP command on exit
        with open(COMMANDS_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("")
        print("✓ Robot control stopped")


if __name__ == "__main__":
    main()


