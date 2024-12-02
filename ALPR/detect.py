import cv2
import os
import shutil
from ultralytics import YOLO

def model_track():
    model = YOLO("ALPR/LPR_detector.pt")

    video_path = "ALPR/car_test.mp4"
    cap = cv2.VideoCapture(video_path)

    if not os.path.exists("ALPR/detections"):
        os.makedirs("ALPR/detections")

    frame_count = 0
    cached_ids = set()
    
    while cap.isOpened():
        success, frame = cap.read()

        if success:
            results = model.track(frame, persist=True, conf=0.6, verbose=False)

            annotated_frame = results[0].plot()
            cv2.imshow("YOLO11 License Plate Detection", annotated_frame)

            if results[0].boxes:
                for box in results[0].boxes:
                    if box.id:
                        object_id = int(box.id)
                        if object_id not in cached_ids:
                            cached_ids.add(object_id)
                            save_path = f"ALPR/detections/frame_{frame_count:04d}.jpg"
                            cv2.imwrite(save_path, annotated_frame)

            frame_count += 1

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()
    shutil.rmtree("ALPR/detections")


def main():
    model_track()

if __name__ == "__main__":
    main()