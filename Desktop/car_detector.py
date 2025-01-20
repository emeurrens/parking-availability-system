from ultralytics import YOLO

try:
    model = YOLO('LPR_detector.pt')
except Exception as e:
    print(f'Stinky exception: {e}')

try:
    results = model('dataset-card.jpg')
    # ultralytics documentation covers how to observe inferences, taken from ultralytics page
    for result in results:
        boxes = result.boxes  
        masks = result.masks  
        keypoints = result.keypoints 
        probs = result.probs  
        obb = result.obb  
        result.save(filename="result.jpg")
except Exception as e:
    print(e)
