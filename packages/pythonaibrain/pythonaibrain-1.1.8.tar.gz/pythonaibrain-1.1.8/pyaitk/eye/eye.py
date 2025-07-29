import cv2
import os
import importlib.resources
from ultralytics import YOLO

def yolo_detect_objects(frame, model, target_class="person"):
    """
    Runs YOLOv8 detection on a frame.
    Returns detected classes list and the annotated frame.
    """
    results = model(frame)[0]  # Run detection on frame

    # Extract detected class names from results
    detected_classes = [model.names[int(box.cls[0])] for box in results.boxes]

    # Annotated frame with bounding boxes
    annotated_frame = results.plot()

    if target_class in detected_classes:
        return detected_classes, annotated_frame
    else:
        return [], annotated_frame  # No target_class detected

def EYE():
    try:
        # Try loading model using importlib.resources (Python 3.9+)
        path = importlib.resources.files(__package__) / "yolov8n.pt"
        model = YOLO(str(path))
    except Exception:
        # Fallback: load from current script directory
        here = os.path.dirname(os.path.abspath(__file__), "eye", "yolov8n.pt")
        model_path = os.path.join(here, "yolov8n.pt")
        model = YOLO(model_path)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return []

    detected_objects = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detected_objects, annotated_frame = yolo_detect_objects(frame, model, target_class="person")

        cv2.imshow("YOLOv8 Detection", annotated_frame)

        # Exit loop if person detected or 'q' pressed
        if "person" in detected_objects or cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return detected_objects
