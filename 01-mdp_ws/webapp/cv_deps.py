import cv2
import torch
from ultralytics import YOLO

# Configuration
confs = {
    "yolo_model": "mdp-det-v0.pt",  # Or any other model you want to use
    "camera_port": 0
}
FLIP_IMAGE = False  # Set this to True to flip the image and bounding boxes

class CVModel:
    def __init__(self, yolo_model_name):
        self.yolo_model_name = yolo_model_name
        self.model = None
        self.results = None
        self.results_tensor = None

    def set_model(self):
        self.model = YOLO(self.yolo_model_name)
        torch.backends.cudnn.benchmark = True
    
    def predict(self, frame):
        self.results = self.model.predict(source=frame, verbose=False, conf=0.6, iou=0.5)[0]
        # Debugging print
        print(f"Predicted {len(self.results.boxes)} boxes")
    
    def inference_locations(self):
        if self.results is None:
            print("No results to process")
            return
        
        boxes = self.results.boxes
        xywhn = boxes.xywhn  # A 2D tensor of shape (N, 4) where N is the number of detected objects
        conf = boxes.conf  # A 1D tensor of shape (N,) containing the confidence scores of the detected objects
        cls = boxes.cls  # A 1D tensor of shape (N,) containing the class labels of the detected objects

        conf = conf.reshape(-1, 1)
        cls = cls.reshape(-1, 1)
        self.results_tensor = torch.cat((xywhn, conf, cls), dim=1)

        # Debugging print
        print(f"Inference locations: {self.results_tensor}")

class CvVisualizer:
    def __init__(self, camera_port):
        self.camera_port = camera_port
        self.cap = cv2.VideoCapture(self.camera_port)
        self.cap_frame = None
        self.h = self.w = self.mid_h = self.mid_w = 0

    def readStream(self):
        ret, self.cap_frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from the camera stream")

    def get_frame_details(self):
        if self.cap_frame is None:
            raise RuntimeError("Frame not read")
        self.h, self.w, _ = self.cap_frame.shape
        self.mid_h = int(self.h / 2)
        self.mid_w = int(self.w / 2)

    def showStream(self, frame):
        cv2.imshow("frame", frame)

    def closeStream(self):
        cv2.destroyAllWindows()
        self.cap.release()

class ObjectTracker:
    def __init__(self):
        self.cvmodel = None
        self.cvvisualizer = None
        self.cap_frame = None
        self.mid_w = self.mid_h = 0
        self.w = self.h = 0  # Add these attributes to store frame width and height

    def set_cvmodel(self, cvmodel: CVModel):
        self.cvmodel = cvmodel

    def set_cvvisualizer(self, cvvisualizer: CvVisualizer):
        self.cvvisualizer = cvvisualizer
        # Update width and height from cvvisualizer
        self.w = self.cvvisualizer.w
        self.h = self.cvvisualizer.h
        self.mid_w = self.cvvisualizer.mid_w
        self.mid_h = self.cvvisualizer.mid_h

    def openStream(self):
        if self.cvvisualizer:
            self.cvvisualizer.readStream()
            self.cvvisualizer.get_frame_details()
            # Update width and height from cvvisualizer after getting frame details
            self.w = self.cvvisualizer.w
            self.h = self.cvvisualizer.h
            self.mid_w = self.cvvisualizer.mid_w
            self.mid_h = self.cvvisualizer.mid_h
            return True

    def closeStream(self):
        if self.cvvisualizer:
            self.cvvisualizer.closeStream()

    def process_frame(self):
        if self.cvvisualizer.cap_frame is None:
            return

        # Check if flipping is enabled
        if FLIP_IMAGE:
            # Flip frame horizontally
            self.proc_frame = cv2.flip(self.cvvisualizer.cap_frame, 1)
        else:
            self.proc_frame = self.cvvisualizer.cap_frame

        # Draw bounding boxes and labels
        if self.cvmodel.results_tensor is not None:
            print(f"Number of detections: {len(self.cvmodel.results_tensor)}")  # Debugging print

            for box in self.cvmodel.results_tensor:
                # Unpack the bounding box information
                x_center, y_center, width, height, conf, cls = box
                # Scale the values back to the frame dimensions
                x_center, y_center, width, height = x_center * self.w, y_center * self.h, width * self.w, height * self.h

                # Calculate the new bounding box coordinates
                x1, y1 = int(x_center - width / 2), int(y_center - height / 2)
                x2, y2 = int(x_center + width / 2), int(y_center + height / 2)

                # Check if flipping is enabled
                if FLIP_IMAGE:
                    # Adjust the x1, x2 values for the flipped image
                    x1 = self.w - x1
                    x2 = self.w - x2

                # Draw the bounding box
                color = (0, 255, 0)  # Green color for bounding box
                self.proc_frame = cv2.rectangle(self.proc_frame, (x1, y1), (x2, y2), color, 2)

                # Draw the label and confidence
                label = f"Class {int(cls)}: {conf:.2f}"

                # Adjust label position for the flipped image
                if FLIP_IMAGE:
                    label_x = x1
                    label_y = y1 - 10  # Place label slightly above the bounding box
                else:
                    label_x = x1
                    label_y = y1 - 10  # Place label slightly above the bounding box

                # Draw the label on the image
                self.proc_frame = cv2.putText(self.proc_frame, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Debugging print to confirm that the bounding boxes are being drawn
        print("Processed frame with bounding boxes")
