#mt_cv.py

import threading
import time
import cv2
from cv import CVModel, CvVisualizer

class MultiThreadedObjectTracker:
    def __init__(self, cvmodel: CVModel, cvvisualizer: CvVisualizer):
        self.cvmodel = cvmodel
        self.cvvisualizer = cvvisualizer

        # Flags for user-controlled operations
        self.read_stream_active = False
        self.inference_active = False
        self.show_raw_stream_active = False
        self.show_labeled_stream_active = False
        
        # Shared variables between operations
        self.proc_frame = None
        self.cap_frame = None
        self.lock = threading.Lock()

    def start(self):
        print("Starting CV operations in a single thread.")
        self.cv_thread_active = True
        self.cv_thread = threading.Thread(target=self.cv_operations, daemon=True)
        self.cv_thread.start()

    def stop(self):
        self.cv_thread_active = False
        if self.cv_thread is not None:
            self.cv_thread.join()

    def cv_operations(self):
        while self.cv_thread_active:
            if self.read_stream_active:
                self.read_stream()

            if self.inference_active:
                self.run_inference()

            if self.show_raw_stream_active:
                self.show_raw_stream()

            if self.show_labeled_stream_active:
                self.show_labeled_stream()

            time.sleep(0.02)  # Adjust the delay based on performance needs

    def set_flags(self, read_stream=False, inference=False, show_raw_stream=False, show_labeled_stream=False):
        """ Set the flags for the operations. """
        self.read_stream_active = read_stream
        self.inference_active = inference
        self.show_raw_stream_active = show_raw_stream
        self.show_labeled_stream_active = show_labeled_stream

    def read_stream(self):
        ret, frame = self.cvvisualizer.cap.read()
        if not ret:
            print("Failed to read frame")
            return
        with self.lock:
            self.cap_frame = frame

    def run_inference(self):
        with self.lock:
            if self.cap_frame is not None:
                self.cvmodel.predict(self.cap_frame)
                self.cvmodel.inference_locations()
                if self.cvmodel.results_tensor is None:
                    print("No results found")
                else:
                    for box in self.cvmodel.results_tensor:
                        # Unpack the bounding box information
                        x_center, y_center, width, height, conf, cls = box
                        print(f"Detected {len(self.cvmodel.results_tensor)} {cls}")

    def show_raw_stream(self):
        with self.lock:
            if self.cap_frame is not None:
                cv2.imshow("Raw Stream", self.cap_frame)

    def show_labeled_stream(self):
        with self.lock:
            if self.cap_frame is not None:
                self.process_frame_with_labels()
                cv2.imshow("Labeled Stream", self.proc_frame)

    def process_frame_with_labels(self):
        if self.cap_frame is None:
            return

        self.proc_frame = cv2.flip(self.cap_frame, 1)
        if self.cvmodel.results_tensor is not None:
            for box in self.cvmodel.results_tensor:
                x_center, y_center, width, height, conf, cls = box
                x_center, y_center, width, height = x_center * self.cvvisualizer.w, y_center * self.cvvisualizer.h, width * self.cvvisualizer.w, height * self.cvvisualizer.h
                x1, y1 = int(x_center - width / 2), int(y_center - height / 2)
                x2, y2 = int(x_center + width / 2), int(y_center + height / 2)
                x1 = self.cvvisualizer.w - x1
                x2 = self.cvvisualizer.w - x2
                color = (0, 255, 0)
                self.proc_frame = cv2.rectangle(self.proc_frame, (x1, y1), (x2, y2), color, 2)
                label = f"Class {int(cls)}: {conf:.2f}"
                label_x = x1
                label_y = y1 - 10
                self.proc_frame = cv2.putText(self.proc_frame, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
