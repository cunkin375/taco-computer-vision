import argparse
import cv2
import os

import supervision as sv
from ultralytics import YOLO

def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 Video Capture")
    parser.add_argument(
        '--webcam_resolution',
        default = [640, 480],
        type = int,
        nargs = 2,
        help = 'Webcam resolution width height'
    )
    return parser.parse_args()

def main():
    args = parse_args()
    frame_width, frame_height = args.webcam_resolution

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

        # run yolo model on the frame (keep as color BGR input for YOLO)
        result = model(frame)[0]

        # convert to grayscale for the Haar cascade detector
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects, reject_levels, confidence_levels = cascade.detectMultiScale3(
            gray, scaleFactor=1.1, minNeighbors=3, outputRejectLevels=True
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

        # exit on 'q' key
        if cv2.waitKey(27) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    try:
        main()
    finally:
        # Best-effort cleanup
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass


