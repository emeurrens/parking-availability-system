from ultralytics import YOLO

try:
    model = YOLO('LPR_detector.pt')
except Exception as e:
    print(f'Stinky exception: {e}')

try:
    results = model('dataset-card.jpg')
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Probs object for classification outputs
        obb = result.obb  # Oriented boxes object for OBB outputs
        # result.show()  # display to screen
        result.save(filename="result.jpg")  # save to disk
except Exception as e:
    print(e)
