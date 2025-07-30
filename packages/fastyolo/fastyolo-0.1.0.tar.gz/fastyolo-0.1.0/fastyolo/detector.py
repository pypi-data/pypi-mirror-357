import cv2
from PIL import Image
from fastai.vision.all import PILImage

def run_hybrid_detection(frame, yolo_model, classifier, threshold=0.85):
    results = yolo_model(frame)[0]
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cropped = frame[y1:y2,x1:x2]
        
        img = PILImage.create(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        label, _, probs = classifier.predict(img)

        if probs.max() > threshold: 
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 225, 0), 2)
            cv2.putText(frame, f"{label} {probs.max():.2f}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 225, 0), 2)

    return frame
