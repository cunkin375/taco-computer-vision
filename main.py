import argparse
import cv2

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
    webcam_source = 2

    cap = cv2.VideoCapture(webcam_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("yolov8l.pt")

    while True:
        ret, frame = cap.read()
        cv2.imshow('Video Feed', frame)

        # run yolo model on first frame
        result = model(frame)[0]

        # exit on 'q' key 
        if cv2.waitKey(27) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()


