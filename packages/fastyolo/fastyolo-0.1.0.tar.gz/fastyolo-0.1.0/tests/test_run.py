import cv2
from ultralytics import YOLO
from fastyolo.classifier import load_classifier
from fastyolo.detector import run_hybrid_detection

def main():
    yolo_model = YOLO("yolov8n.pt")
    classifier = load_classifier("tests/dog_classifier.pk1")
    cap = cv2.VideoCapture(0)

    assert cap.isOpened(), "Webcam not asscessible."

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        run_hybrid_detection(frame, yolo_model, classifier, threshold=0.85)
        cv2.imshow("Hybrid Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cap.destroyAllWindows()

if __name__ == "__main__":
    main()

