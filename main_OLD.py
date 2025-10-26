import argparse
import cv2
import os

import supervision as sv
from ultralytics import YOLO
import subprocess
import threading
import queue
import sys
import time

# Absolute path to the shared commands file (PC-side queue)
COMMANDS_FILE_PATH = r"C:\\Users\\hackathon\\dev\\taco\\taco-computer-vision\\commands.txt"

def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 Video Capture")
    parser.add_argument(
        '--webcam_resolution',
        default = [640, 480],
        type = int,
        nargs = 2,
        help = 'Webcam resolution width height'
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
        help='Enable robot motor control (requires robot_controller module and connected hardware)'
    )
    parser.add_argument(
        '--movement_step',
        default=30,
        type=int,
        help='Degrees to move robot per adjustment (default: 30 for dramatic movements)'
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
    
    # Rate limiting for robot commands
    last_command_time = 0
    command_cooldown = 0.05  # 50ms between commands (20 commands/sec for ultra-fast tracking!)
    
    # Track if we need to send a command this frame
    command_to_send = None
    
    # Debug output
    print(f"[STARTUP] Robot control enabled: {args.use_robot}")
    print(f"[STARTUP] Target object: {args.target_object}")
    print(f"[STARTUP] Center zone: {center_left:.1f} to {center_right:.1f}")
    if args.use_robot:
        print(f"[STARTUP] ✓ Robot commands will be sent to: {COMMANDS_FILE_PATH}")
        # Clear any old commands at startup
        try:
            with open(COMMANDS_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write("")
        except Exception:
            pass
    else:
        print(f"[STARTUP] ✗ Robot control disabled (use --use_robot flag to enable)")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    # Use OpenCV's bundled haarcascade path so the XML is found reliably
    cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
    cascade = cv2.CascadeClassifier(cascade_path)

    if not cap.isOpened():
        raise SystemExit(f"Could not open camera at index 0. Try running `webcam.py` to enumerate camera indices.")

    if cascade.empty():
        raise SystemExit(f"Failed to load cascade classifier from {cascade_path}. Check your OpenCV installation.")

    model = YOLO("yolov8l.pt")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to read frame from camera, stopping")
            break
        
        # Reset command for this frame
        command_to_send = None
        
        # run yolo model on the frame (keep as color BGR input for YOLO)
        result = model(frame)[0]
        # convert to grayscale for the Haar cascade detector
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        objects, reject_levels, confidence_levels = cascade.detectMultiScale3(
            gray, 
            scaleFactor = 1.1, 
            minNeighbors = 3, 
            outputRejectLevels = True
        )
        # Draw bounding boxes on a copy of the frame
        out = frame.copy()
        # Draw YOLO boxes (support multiple result shapes/backends)
        try:
            xyxy = result.boxes.xyxy.cpu().numpy()
        except Exception:
            try:
                xyxy = result.boxes.xyxy.numpy()
            except Exception:
                # fallback to list-of-lists
                xyxy = getattr(result.boxes, 'xyxy', [])

        # Gather confs and classes if available
        try:
            confs = result.boxes.conf.cpu().numpy()
        except Exception:
            try:
                confs = result.boxes.conf.numpy()
            except Exception:
                confs = getattr(result.boxes, 'conf', [])

        try:
            classes = result.boxes.cls.cpu().numpy()
        except Exception:
            try:
                classes = result.boxes.cls.numpy()
            except Exception:
                classes = getattr(result.boxes, 'cls', [])

        # Draw each YOLO detection
        for i, b in enumerate(xyxy):
            try:
                x1, y1, x2, y2 = map(int, b[:4])
            except Exception:
                continue
            # build label text if class and confidence are available
            label = None
            try:
                cls_i = int(classes[i]) if len(classes) > i else None
            except Exception:
                cls_i = None
            try:
                conf_i = float(confs[i]) if len(confs) > i else None
            except Exception:
                conf_i = None

            if cls_i is not None and conf_i is not None:
                name = model.names.get(cls_i, str(cls_i)) if hasattr(model, 'names') else str(cls_i)
                label = f"{name} {conf_i:.2f}"
            elif conf_i is not None:
                label = f"{conf_i:.2f}"

            # Check if this detection matches the target object
            if args.target_object and args.use_robot and cls_i is not None:
                detected_name = model.names.get(cls_i, '').lower() if hasattr(model, 'names') else ''
                # Removed debug spam for speed
                if detected_name == args.target_object.lower():
                    # Calculate overlap between bounding box and center zone
                    # Find the intersection between bbox [x1, x2] and center zone [center_left, center_right]
                    overlap_left = max(x1, center_left)
                    overlap_right = min(x2, center_right)
                    overlap_width = max(0, overlap_right - overlap_left)
                    
                    bbox_width = x2 - x1
                    overlap_fraction = overlap_width / bbox_width if bbox_width > 0 else 0
                    
                    # If majority (>50%) of bbox is within center zone, it's centered
                    if overlap_fraction > 0.5:
                        # Robot is already centered, stop motors
                        command_to_send = 'STOP\n'
                    else:
                        # Rate limiting: only send command if cooldown has passed
                        current_time = time.time()
                        time_since_last = current_time - last_command_time
                        if time_since_last < command_cooldown:
                            # Cooldown active - skip this frame
                            command_to_send = None  # Don't send during cooldown
                        else:
                            # Calculate bounding box center for left/right determination
                            bbox_center_x = (x1 + x2) / 2
                            bbox_center_y = (y1 + y2) / 2
                            
                            # Horizontal tracking (base motor) - 40 DEGREE MOVEMENTS
                            if bbox_center_x < center_left:
                                command_to_send = 'BASE:300\n'  # Rotate base left 40 degrees
                                print(f"⬅️  LEFT")
                            elif bbox_center_x > center_right:
                                command_to_send = 'BASE:-300\n'  # Rotate base right 40 degrees
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
        # Draw Haar cascade face detections (objects is typically an array of rects)
        try:
            for rect in objects:
                # some return shapes: (x, y, w, h)
                if len(rect) >= 4:
                    x, y, w, h = map(int, rect[:4])
                    cv2.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 2)
        except Exception:
            # ignore drawing errors
            pass
        # Show the annotated frame
        cv2.imshow('Video Feed', out)
        
        # Write command to file at END of frame processing (after all detections)
        if args.use_robot:
            try:
                with open(COMMANDS_FILE_PATH, 'w', encoding='utf-8') as qf:
                    if command_to_send:
                        qf.write(command_to_send)
                        print(f"📤 SENT: {command_to_send.strip()}")  # Debug: show what's being sent
                    else:
                        qf.write("")  # Clear file when no command needed
            except Exception as e:
                print(f"❌ Error writing commands file: {e}")

        # exit on 'q' key
        if cv2.waitKey(27) & 0xFF == ord('q'):
            break
    # end main loop
    cap.release()
    
    # Shutdown message (no hub process to stop in this flow)
    pass
        

if __name__ == "__main__":
    try:
        main()
    finally:
        # Best-effort cleanup
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass


