from flask import Flask, Response
from threading import Lock
import cv2
from cv_deps import CVModel, CvVisualizer, ObjectTracker, confs  # Import from base code
import signal
import sys

# Create Flask app
app = Flask(__name__)

# Instantiate ObjectTracker from base code
objectTracker = ObjectTracker()

# Initialize and configure the CVModel and CvVisualizer
cvmodel = CVModel(confs["yolo_model"])
cvmodel.set_model()
cvvisualizer = CvVisualizer(camera_port=confs["camera_port"])

# Set objects in ObjectTracker
objectTracker.set_cvmodel(cvmodel)
objectTracker.set_cvvisualizer(cvvisualizer)

# Create a lock for camera access
camera_lock = Lock()

# Function to generate frames
def generate_frames():
    while True:
        with camera_lock:  # Ensure only one thread accesses the camera at a time
            objectTracker.cvvisualizer.readStream()
            objectTracker.cvmodel.predict(objectTracker.cvvisualizer.cap_frame)
            objectTracker.cvmodel.inference_locations()
            objectTracker.process_frame()

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', objectTracker.proc_frame)
        if not ret:
            continue

        # Convert the frame to bytes and yield
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Graceful shutdown
def close_resources(signal, frame):
    print("Releasing resources...")
    objectTracker.closeStream()  # Close camera stream
    sys.exit(0)

signal.signal(signal.SIGINT, close_resources)
signal.signal(signal.SIGTERM, close_resources)

if __name__ == '__main__':
    # Start Flask server without debug mode to avoid multi-threading issues
    app.run(debug=False, host='0.0.0.0', port=5000)
