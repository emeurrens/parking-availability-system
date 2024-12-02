from inference_sdk import InferenceHTTPClient
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def run_detection_pipeline(detection_path, client):
    try:
        result = client.run_workflow(
            workspace_name="samer-khatib",
            workflow_id="license-plate-ocr",
            images={
                "image": detection_path
            },
            parameters={
                "lot_id": "f24dacb0-9513-45d9-90f8-b07e5dee5271"
            }
        )
        print(f"Detection result for {detection_path}: {result}")
    except Exception as e:
        print(f"Error saving detection for {detection_path}: {e}")

class FolderMonitorHandler(FileSystemEventHandler):
    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="K9QeT12yd94HPXevY7Ju"
        )

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            run_detection_pipeline(event.src_path, self.client)

def monitor_folder(folder_path):
    event_handler = FolderMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print(f"Monitoring folder: {folder_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    monitor_folder("ALPR/detections")

if __name__ == "__main__":
    main()