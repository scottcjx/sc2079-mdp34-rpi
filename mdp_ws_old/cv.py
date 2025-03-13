#cv.py 

import cv2
import time
import torch
from ultralytics import YOLO


data_dict = {
    '0':'11',
    '1':'12',
    '2':'13',
    '3':'14',
    '4':'15',
    '5':'16',
    '6':'17',
    '7':'18',
    '8':'19',
    '9':'20',
    '10':'21',
    '11':'22',
    '12':'23',
    '13':'24',
    '14':'25',
    '15':'26',
    '16':'27',
    '17':'28',
    '18':'29',
    '19':'30',
    '20':'31',
    '21':'33',
    '22':'34',
    '23':'35',
    '24':'36',
    '25':'40',
    '27':'36',
    '28':'37',
    '29':'39', #left arrow
    '30':'38' #right arrow
}

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

    def inference_locations(self):
        if self.results is None:
            return
        
        boxes = self.results.boxes
        xywhn = boxes.xywhn  # A 2D tensor of shape (N, 4) where N is the number of detected objects
        conf = boxes.conf  # A 1D tensor of shape (N,) containing the confidence scores of the detected objects
        cls = boxes.cls  # A 1D tensor of shape (N,) containing the class labels of the detected objects

        conf = conf.reshape(-1, 1)
        cls = cls.reshape(-1, 1)
        self.results_tensor = torch.cat((xywhn, conf, cls), dim=1)

class CvVisualizer:
    def __init__(self, camera_port):
        self.camera_port = camera_port
        self.cap = cv2.VideoCapture(self.camera_port)
        self.cap_frame = None
        self.h = self.w = self.mid_h = self.mid_w = 0
    
    def read_stream(self):
        while self.read_stream_active:
            ret, frame = self.cvvisualizer.cap.read()
            if not ret:
                print("Failed to read frame")
                break
            with self.lock:  # Locking when updating cap_frame
                self.cap_frame = frame
            time.sleep(0.02)

    def get_frame_details(self):
        if self.cap_frame is None:
            raise RuntimeError("Frame not read")
        
        self.h, self.w, _ = self.cap_frame.shape
        self.mid_h = int(self.h / 2)
        self.mid_w = int(self.w / 2)

    def showStream(self, frame):
        if frame is not None:
            cv2.imshow("frame", frame)
        else:
            print("Empty frame passed to showStream")

    
    def closeStream(self):
        cv2.destroyAllWindows()
        self.cap.release()

class ObjectTracker:
    FLIP_FRAME = 1

    def __init__(self):
        self.cvmodel = None
        self.cvvisualizer = None
        self.cap_frame = None
        self.mid_w = self.mid_h = 0
        self.x_req = self.y_req = 0
        self.w = self.h = 0  # Add these attributes to store frame width and height
        #####
        self.proc_frame = None  # Add proc_frame attribute
        #####

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
            #self.cvvisualizer.readStream()
            self.cvvisualizer.read_stream()
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
#####
    def screenshot(self):
        """Capture and display a screenshot from the current frame"""
        if self.proc_frame is not None:
            # Display the screenshot in a separate window
            cv2.imshow("Screenshot", self.proc_frame)
            
            # Create a screenshots directory if it doesn't exist
            import os
            import datetime
            
            screenshot_dir = "screenshots"
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
                print(f"Created directory: {screenshot_dir}")
            
            # Save to disk with timestamp in the screenshots directory
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = os.path.join(screenshot_dir, f'screenshot_{timestamp}.png')
            cv2.imwrite(filename, self.proc_frame)
            print(f"Screenshot saved as {filename}")
#####
    def run(self):
        self.openStream()
        while True:
            #self.cvvisualizer.readStream()
            self.cvvisualizer.read_stream()
            self.cvmodel.predict(self.cvvisualizer.cap_frame)
            self.cvmodel.inference_locations()
            self.process_frame()
            self.cvvisualizer.showStream(self.proc_frame)
            """
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.closeStream()
                break
            """
            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.closeStream()
                break
            elif key == ord('c'):
                # Take a screenshot when 'c' is pressed
                self.screenshot()

    def process_frame(self):
        if self.cvvisualizer.cap_frame is None:
            return
        
        if self.FLIP_FRAME:
            # Flip frame horizontally
            self.proc_frame = cv2.flip(self.cvvisualizer.cap_frame, 1)
        else:
            self.proc_frame = self.cvvisualizer.cap_frame.copy()

        # Draw bounding boxes and labels
        if self.cvmodel.results_tensor is not None:
            for box in self.cvmodel.results_tensor:
                # Unpack the bounding box information
                x_center, y_center, width, height, conf, cls = box
                # Scale the values back to the frame dimensions
                x_center, y_center, width, height = x_center * self.w, y_center * self.h, width * self.w, height * self.h

                # Calculate the new bounding box coordinates
                x1, y1 = int(x_center - width / 2), int(y_center - height / 2)
                x2, y2 = int(x_center + width / 2), int(y_center + height / 2)

                # Adjust the x1, x2 values for the flipped image
                x1 = self.w - x1
                x2 = self.w - x2

                # Draw the bounding box
                color = (0, 255, 0)  # Green color for bounding box
                self.proc_frame = cv2.rectangle(self.proc_frame, (x1, y1), (x2, y2), color, 2)

                # Draw the label and confidence
                label = f"IMG ID: {data_dict[str(int(cls))]}: {conf:.2f}"

                # Adjust label position for the flipped image
                label_x = x1
                label_y = y1 - 10  # Place label slightly above the bounding box

                # Draw the label on the image
                self.proc_frame = cv2.putText(self.proc_frame, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Draw center point
        # self.proc_frame = cv2.circle(self.proc_frame, (self.mid_w, self.mid_h), 1, (255, 0, 255), 3)

    def extract_classes_and_positions(self):
        """Extract the classes and their positions from the latest frame."""
        if self.cvmodel.results_tensor is None:
            return []

        classes_positions = []

        # Loop through each detection and extract the necessary information
        for box in self.cvmodel.results_tensor:
            # Unpack the bounding box and class information
            x_center, y_center, width, height, conf, cls = box

            # Scale to frame size
            x_center, y_center, width, height = x_center * self.w, y_center * self.h, width * self.w, height * self.h

            # Calculate bounding box corners
            x1, y1 = int(x_center - width / 2), int(y_center - height / 2)
            x2, y2 = int(x_center + width / 2), int(y_center + height / 2)

            # Extract the class and its position (bounding box)
            class_info = {
                "class": int(cls),
                "confidence": conf.item(),  # Convert to regular float
                "position": (x1, y1, x2, y2)  # Bounding box corners (top-left, bottom-right)
            }

            classes_positions.append(class_info)

        return classes_positions


confs = {
    #"yolo_model": "mdp-det-v0.pt",  # Or any other model you want to use
    "yolo_model": "best.pt",
    #"camera_port": "/dev/video0"
    "camera_port": 4
}

def main():
    cvmodel = CVModel(confs["yolo_model"])
    cvmodel.set_model()

    cvvisualizer = CvVisualizer(camera_port=confs["camera_port"])
    cvvisualizer.read_stream_active = 1

    objectTracker = ObjectTracker()
    objectTracker.set_cvmodel(cvmodel)
    objectTracker.set_cvvisualizer(cvvisualizer)

    objectTracker.run()

if __name__ == "__main__":
    main()
