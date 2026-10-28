# Importing the YOLO model from the ultralytics package
from ultralytics import YOLO

# Defining the ObjectDetector class
class ObjectDetector:
    def __init__(self):
        # Loading the YOLOv8 nano model (optimized for speed and lightweight performance)
        self.model = YOLO('yolov8n.pt')

    def detect_objects(self, frame):
        """
        Detecting objects in a frame.
        Returning a list of dictionaries containing label, confidence, position, and bounding box.
        bbox = (x1, y1, x2, y2)

        Args:
            frame (numpy.ndarray): Image frame for object detection.

        Returns:
            list of dict: Each dict contains 'label', 'confidence', 'position', and 'bbox'.
        """
        # Running the model on the input frame without verbose output
        results = self.model(frame, verbose=False)
        # Initializing an empty list for storing detection details
        detections = []

        # Iterating through each result in the model output
        for r in results:
            # Iterating through each bounding box in the result
            for box in r.boxes:
                # Extracting the class index from the box
                cls = int(box.cls[0])
                # Extracting the confidence score as a float
                conf = float(box.conf[0])
                # Retrieving the label name from the model's class names
                label = self.model.names[cls]

                # Converting bounding box coordinates to integers
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Calculating horizontal center of the bounding box
                center_x = (x1 + x2) // 2

                # Getting the width dimension of the frame
                width = frame.shape[1]
                # Determining position based on horizontal center location
                if center_x < width // 3:
                    position = "left"
                elif center_x > 2 * width // 3:
                    position = "right"
                else:
                    position = "center"

                # Appending detection information as dictionary to the detections list
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "position": position,
                    "bbox": (x1, y1, x2, y2)
                })

        # Returning the completed list of detection dictionaries
        return detections
