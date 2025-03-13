import cv2
import torch
import os
import time
import numpy as np
from datetime import datetime
from ultralytics import YOLO

###################################################
# CONFIG / CONSTANTS
###################################################

data_dict = {
    '0': '11',
    '1': '12',
    '2': '13',
    '3': '14',
    '4': '15',
    '5': '16',
    '6': '17',
    '7': '18',
    '8': '19',
    '9': '20',
    '10': '21',
    '11': '22',
    '12': '23',
    '13': '24',
    '14': '25',
    '15': '26',
    '16': '27',
    '17': '28',
    '18': '29',
    '19': '30',
    '20': '31',
    '21': '33',
    '22': '34',
    '23': '35',
    '24': '36',
    '25': '40',
    '27': '36',
    '28': '37',
    '29': '39',  # left arrow
    '30': '38'   # right arrow
}

confs = {
    "yolo_model": "mdp-det-v0.pt",  # Change to your YOLO model path
    "camera_port": 0
}

# Whether to flip the camera feed horizontally (selfie style)
FLIP_IMAGE = False

# Screenshot capture settings
capture_screenshots = True       # Change to True if you want automatic capture
num_screenshots = 5               # How many screenshots total
screenshot_interval = 0.5         # Seconds between screenshots
screenshot_dir = "./screenshot"   # Folder to save screenshots

###################################################
# CVModel
###################################################

class CVModel:
    """
    Manages the YOLO model inference using ultralytics.
    """
    def __init__(self, yolo_model_name):
        self.yolo_model_name = yolo_model_name
        self.model = None
        self.results = None
        self.results_tensor = None

    def set_model(self):
        # Load the YOLO model
        self.model = YOLO(self.yolo_model_name)
        # Speed things up if you have a GPU
        torch.backends.cudnn.benchmark = True

    def predict(self, frame):
        """
        Runs inference on the given frame at conf=0.6, iou=0.5
        and stores the first result in self.results
        """
        # ultralytics >= 8.0 usage:
        #   self.model.predict(...)[0] returns a yolo result object
        self.results = self.model.predict(source=frame, 
                                          verbose=False, 
                                          conf=0.6, 
                                          iou=0.5)[0]

    def inference_locations(self):
        """
        Converts YOLO's result boxes into a single tensor: [x_center, y_center, w, h, conf, class_id]
        in normalized coords (0 to 1).
        """
        if self.results is None:
            self.results_tensor = None
            return
        
        boxes = self.results.boxes
        # Each shape is (N,) or (N, 4) for N detections
        xywhn = boxes.xywhn  # (N, 4) normalized coords
        conf = boxes.conf    # (N,) confidence
        cls = boxes.cls      # (N,) class labels

        if len(xywhn) == 0:
            # No detections found
            self.results_tensor = None
            return

        # Make them column vectors so we can concatenate
        conf = conf.reshape(-1, 1)
        cls = cls.reshape(-1, 1)
        self.results_tensor = torch.cat((xywhn, conf, cls), dim=1)

###################################################
# CvVisualizer
###################################################

class CvVisualizer:
    """
    Grabs frames from a camera and keeps track of frame sizes.
    """
    def __init__(self, camera_port):
        self.camera_port = camera_port
        self.cap = cv2.VideoCapture(self.camera_port)

        # Try setting some camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        self.cap_frame = None
        self.h = 0
        self.w = 0
        self.mid_h = 0
        self.mid_w = 0

    def readStream(self):
        """
        Reads a frame from the camera, updates self.cap_frame.
        """
        ret, self.cap_frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from the camera stream")

        if len(self.cap_frame.shape) != 3:
            raise RuntimeError(f"Invalid frame shape: {self.cap_frame.shape}. Expected 3 dims.")
    
    def get_frame_details(self):
        """
        Updates the .h, .w, mid_h, mid_w based on the last read frame.
        """
        if self.cap_frame is None:
            raise RuntimeError("Frame not read yet.")
        
        self.h, self.w, _ = self.cap_frame.shape
        self.mid_h = int(self.h / 2)
        self.mid_w = int(self.w / 2)

    def showStream(self, frame):
        cv2.imshow("frame", frame)
    
    def closeStream(self):
        cv2.destroyAllWindows()
        self.cap.release()

###################################################
# ObjectTracker + Screenshot Logic
###################################################

class ObjectTracker:
    """
    Reads frames in a loop, runs YOLO inference, draws bounding boxes/labels,
    and (optionally) captures screenshots every N seconds.
    """
    def __init__(self):
        self.cvmodel = None
        self.cvvisualizer = None

        # Updated after we read the first frame
        self.w = 0
        self.h = 0
        self.mid_w = 0
        self.mid_h = 0

        # A buffer for the processed frame with bounding boxes
        self.proc_frame = None

        # Screenshot / verification
        self.capture_screenshots = capture_screenshots
        self.screenshot_dir = screenshot_dir
        self.num_screenshots = num_screenshots
        self.screenshot_interval = screenshot_interval
        
        # Tracking how many we've taken
        self.screenshots_taken = 0
        self.last_screenshot_time = 0
        self.screenshot_results = []
        self.verification_done = False

        # Ensure screenshot dir exists
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def set_cvmodel(self, cvmodel: CVModel):
        self.cvmodel = cvmodel

    def set_cvvisualizer(self, cvvisualizer: CvVisualizer):
        self.cvvisualizer = cvvisualizer

    def openStream(self):
        """
        Grabs an initial frame to establish .w and .h
        """
        if not self.cvvisualizer:
            raise RuntimeError("No CvVisualizer set.")

        self.cvvisualizer.readStream()
        self.cvvisualizer.get_frame_details()

        # Update the known width/height
        self.w = self.cvvisualizer.w
        self.h = self.cvvisualizer.h
        self.mid_w = self.cvvisualizer.mid_w
        self.mid_h = self.cvvisualizer.mid_h

    def closeStream(self):
        if self.cvvisualizer:
            self.cvvisualizer.closeStream()

    def run(self):
        """
        Main loop:
          1) Read a frame
          2) Inference
          3) Draw bounding boxes
          4) Show frame
          5) Optionally capture screenshots
          6) Press 'q' to quit
        """
        self.openStream()

        while True:
            # 1) Read the camera stream
            self.cvvisualizer.readStream()

            # 2) Run inference
            self.cvmodel.predict(self.cvvisualizer.cap_frame)
            self.cvmodel.inference_locations()

            # 3) Draw bounding boxes
            self.process_frame()

            # 4) Show the result
            self.cvvisualizer.showStream(self.proc_frame)

            # 5) If screenshots are enabled, handle it
            if self.capture_screenshots and not self.verification_done:
                self.handle_screenshots()

            # 6) Listen for keyboard
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.closeStream()
                break

    def process_frame(self):
        """
        Creates self.proc_frame by optionally flipping the camera frame,
        then drawing bounding boxes + labels from self.cvmodel.results_tensor.
        """
        frame = self.cvvisualizer.cap_frame

        if FLIP_IMAGE:
            # Flip horizontally
            frame = cv2.flip(frame, 1)

        self.proc_frame = frame

        # If no detections
        if self.cvmodel.results_tensor is None:
            # You can print something here if you want:
            # print("No results found")
            return

        # Otherwise, draw bounding boxes
        for box in self.cvmodel.results_tensor:
            # Unpack the bounding box info
            x_center, y_center, width, height, conf, cls = box.tolist()

            # >>> PRINT DETECTED CLASS (added line) <<<
            cls_id = str(int(cls))
            cls_text = data_dict.get(cls_id, cls_id)
            print(f"Detected class: {cls_text} with confidence {conf:.2f}")

            # Scale to actual image size
            x_center *= self.w
            y_center *= self.h
            width *= self.w
            height *= self.h

            x1 = int(x_center - width / 2)
            y1 = int(y_center - height / 2)
            x2 = int(x_center + width / 2)
            y2 = int(y_center + height / 2)

            # If flipping is enabled, adjust x-coordinates
            if FLIP_IMAGE:
                flip_x1 = self.w - x2
                flip_x2 = self.w - x1
                x1, x2 = int(flip_x1), int(flip_x2)

            color = (0, 255, 0)  # Green bounding box
            cv2.rectangle(self.proc_frame, (x1, y1), (x2, y2), color, 2)

            label = f"IMG ID: {cls_text}: {conf:.2f}"
            label_x = x1
            label_y = y1 - 10
            cv2.putText(
                self.proc_frame,
                label,
                (label_x, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )


    ###################################################
    # Screenshot + Verification
    ###################################################

    def handle_screenshots(self):
        """
        If it's time to take a new screenshot, do it. After finishing the
        required number, run verification.
        """
        now = time.time()
        if (now - self.last_screenshot_time >= self.screenshot_interval 
                and self.screenshots_taken < self.num_screenshots):
            self.take_screenshot()
            self.last_screenshot_time = now

            if self.screenshots_taken >= self.num_screenshots:
                self.verify_screenshots()
                self.verification_done = True

    def take_screenshot(self):
        """
        Saves the current processed frame (with bounding boxes drawn) to disk
        and logs the detection results.
        """
        if self.proc_frame is None or self.cvmodel.results_tensor is None:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.screenshot_dir,
                                f"screenshot_{self.screenshots_taken+1}_{timestamp}.jpg")

        cv2.imwrite(filename, self.proc_frame)

        # Gather detection info
        detected_classes = []
        for box in self.cvmodel.results_tensor:
            *_, conf, cls = box.tolist()
            cls_id = str(int(cls))
            cls_text = data_dict.get(cls_id, cls_id)
            detected_classes.append((cls_text, conf))

        self.screenshot_results.append({
            'filename': filename,
            'detections': detected_classes
        })

        self.screenshots_taken += 1
        print(f"Captured screenshot {self.screenshots_taken}/{self.num_screenshots}: {filename}")
        print(f"Detected classes: {detected_classes}")

    def verify_screenshots(self):
        """
        Example verification: checks whether all screenshots had the same set of classes.
        Also prints confidence statistics if they match.
        """
        if not self.screenshot_results:
            print("No screenshots to verify.")
            return

        # Build a list of sets of classes from each screenshot
        screenshot_classes = []
        for result in self.screenshot_results:
            classes_here = set([det[0] for det in result['detections']])
            screenshot_classes.append(classes_here)

        # Check if all sets match
        all_match = all(s == screenshot_classes[0] for s in screenshot_classes)
        if all_match:
            print("VERIFICATION SUCCESSFUL: All screenshots contain the same image IDs.")
            print(f"Detected image IDs: {', '.join(screenshot_classes[0])}")
        else:
            print("VERIFICATION FAILED: Inconsistent detection across screenshots.")
            for i, classes in enumerate(screenshot_classes):
                print(f"Screenshot {i+1}: {', '.join(classes)}")

        # If they match, check confidence score stability
        if all_match and len(self.screenshot_results) > 0:
            confidence_analysis = {}
            # Use the first screenshot's set of detections for baseline
            first_detects = self.screenshot_results[0]['detections']

            for (cls_txt, _) in first_detects:
                # Gather all confidence scores for this class from each screenshot
                conf_scores = []
                for sr in self.screenshot_results:
                    # Look up the class
                    found_conf = None
                    for (c_txt, c_conf) in sr['detections']:
                        if c_txt == cls_txt:
                            found_conf = c_conf
                            break
                    if found_conf is not None:
                        conf_scores.append(found_conf)
                
                if conf_scores:
                    avg_conf = sum(conf_scores) / len(conf_scores)
                    std_dev = np.std(conf_scores)
                    confidence_analysis[cls_txt] = (avg_conf, std_dev, conf_scores)

            print("\nConfidence Score Analysis:")
            for cls_txt, (avg_c, std_c, all_c) in confidence_analysis.items():
                print(f"Image ID {cls_txt}:")
                print(f"  Average confidence: {avg_c:.4f}")
                print(f"  Standard deviation: {std_c:.4f}")
                print("  Scores: " + ", ".join([f"{x:.4f}" for x in all_c]))
            print("")

###################################################
# MAIN
###################################################

def main():
    # 1) Create and load the YOLO model
    cvmodel = CVModel(confs["yolo_model"])
    cvmodel.set_model()

    # 2) Create the visualizer (camera feed)
    cvvisualizer = CvVisualizer(camera_port=confs["camera_port"])

    # 3) Create the object tracker, set references
    obj_tracker = ObjectTracker()
    obj_tracker.set_cvmodel(cvmodel)
    obj_tracker.set_cvvisualizer(cvvisualizer)

    # 4) Run
    obj_tracker.run()

if __name__ == "__main__":
    main()
