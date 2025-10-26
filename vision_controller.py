import cv2
import os
import time
from ultralytics import YOLO
import subprocess

# Command to send to the hub via pybricksdev
def send_robot_command(command):
    print(f"📤 Sending command: {command}")
    subprocess.run(["python", "-m", "pybricksdev", "run", "ble", "--wait", f"robot.py", command])

# ---- YOLO Setup ----
model = YOLO("yolov8l.pt")
target_object = "person"
frame_width = 640
frame_height = 480

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

frame_center_x = frame_width / 2
center_zone_width = frame_width * 0.2
center_left = frame_center_x - center_zone_width / 2
center_right = frame_center_x + center_zone_width / 2

last_action = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]

    for box in results.boxes:
        cls = int(box.cls)
        name = model.names.get(cls, "").lower()
        if name == target_object:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox_center_x = (x1 + x2) / 2

            if bbox_center_x < center_left:
                action = "left"
            elif bbox_center_x > center_right:
                action = "right"
            else:
                action = "center"

            if action != last_action:
                if action == "left":
                    send_robot_command("left")
                elif action == "right":
                    send_robot_command("right")
                elif action == "center":
                    send_robot_command("center")
                last_action = action

    cv2.imshow("YOLO Vision", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
