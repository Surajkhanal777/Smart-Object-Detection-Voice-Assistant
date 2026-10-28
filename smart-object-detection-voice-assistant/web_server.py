
"""
Bridging Python object detection with a web frontend using Flask.
Running this file instead of main.py enables the web interface.
"""

# Importing Flask components for creating routes, rendering pages, and returning responses
from flask import Flask, render_template, Response, jsonify

# Importing CORS for enabling cross-origin requests
from flask_cors import CORS

# Importing OpenCV for capturing, processing, and annotating video frames
import cv2

# Importing NumPy for converting image data into arrays
import numpy as np

# Importing urllib.request for retrieving images from a mobile IP camera
import urllib.request

# Importing threading for running speech announcements without blocking detection
import threading

# Importing time for controlling delays and announcement intervals
import time

# Importing datetime for generating detection timestamps
from datetime import datetime

# Importing existing project modules for detecting objects, generating descriptions, and speaking
from object_detector import ObjectDetector
from description_nlp import generate_description
from voice_input import speak

# Initializing the Flask application
app = Flask(__name__)

# Enabling cross-origin resource sharing for frontend requests
CORS(app)

# Initializing the object detector and shared application settings
detector = ObjectDetector()
camera_active = False  # Tracking whether camera processing is active
current_camera = "laptop"  # Selecting the default camera ("laptop" or "mobile")
use_voice = True  # Enabling voice announcements by default
last_speak_time = 0  # Tracking the previous announcement time
speak_interval = 5  # Setting the minimum interval between announcements in seconds
mobile_url = "http://YOUR_PHONE_IP:8080/shot.jpg"  # Configuring the mobile camera snapshot URL

# Initializing shared detection data and statistical counters
current_detections = []  # Storing the latest detected objects
detection_stats = {
    "total_objects": 0,  # Tracking the number of objects in the latest frame
    "unique_types": set()  # Collecting distinct detected object labels
}


def speak_async(text):
    """Running speech announcements in a separate thread without blocking detection."""

    # Checking whether voice announcements are enabled
    if use_voice:
        # Starting a background thread for speaking the generated description
        threading.Thread(target=speak, args=(text,), daemon=True).start()


def get_frame():
    """Retrieving a frame from the currently selected camera."""

    # Accessing the shared camera selection
    global current_camera

    # Checking whether the mobile camera is selected
    if current_camera == "mobile":
        try:
            # Requesting a snapshot from the mobile IP camera with a two-second timeout
            img_resp = urllib.request.urlopen(mobile_url, timeout=2)

            # Converting the received image bytes into a NumPy array
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)

            # Decoding the image array into an OpenCV frame
            frame = cv2.imdecode(img_np, -1)

            # Returning the decoded mobile camera frame
            return frame

        except Exception as e:
            # Reporting mobile camera retrieval errors
            print(f"Mobile camera error: {e}")

            # Returning an empty result when retrieving the frame fails
            return None

    else:
        # Opening the default laptop camera
        cap = cv2.VideoCapture(0)

        # Capturing a frame and checking whether the operation succeeds
        ret, frame = cap.read()

        # Releasing the camera resource after capturing the frame
        cap.release()

        # Returning the captured frame or an empty result when capture fails
        return frame if ret else None


def generate_frames():
    """Generating annotated video frames for continuous frontend streaming."""

    # Accessing shared variables for camera processing, detections, announcements, and statistics
    global camera_active, current_detections, last_speak_time, detection_stats

    # Continuing frame generation while camera processing remains active
    while camera_active:

        # Retrieving a frame from the selected camera
        frame = get_frame()

        # Checking whether frame retrieval failed
        if frame is None:
            # Pausing briefly before attempting another capture
            time.sleep(0.1)
            continue

        # Detecting objects within the captured frame
        detections = detector.detect_objects(frame)

        # Updating the latest detection results
        current_detections = detections

        # Updating the number of objects detected in the current frame
        detection_stats["total_objects"] = len(detections)

        # Collecting the labels of detected object types
        for det in detections:
            detection_stats["unique_types"].add(det['label'])

        # Drawing bounding boxes and labels around detected objects
        for det in detections:

            # Extracting bounding-box coordinates, object labels, and confidence scores
            x1, y1, x2, y2 = det['bbox']
            label = det['label']
            conf = det['confidence']

            # Drawing a green rectangle around the detected object
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Formatting the object label and confidence score for display
            text = f"{label}: {conf:.2f}"

            # Displaying the formatted label above the bounding box
            cv2.putText(
                frame,
                text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        # Checking the elapsed time before generating another voice announcement
        current_time = time.time()

        # Generating and speaking a description when the interval has elapsed and objects are detected
        if current_time - last_speak_time > speak_interval and detections:

            # Converting the detected objects into a natural-language description
            description = generate_description(detections)

            # Announcing the description asynchronously
            speak_async(description)

            # Updating the previous announcement timestamp
            last_speak_time = current_time

        # Encoding the annotated frame into JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)

        # Skipping the frame when JPEG encoding fails
        if not ret:
            continue

        # Converting the encoded image buffer into bytes
        frame_bytes = buffer.tobytes()

        # Streaming the frame using the multipart HTTP response format
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

        # Pausing briefly to regulate the frame-generation loop
        time.sleep(0.03)  # Targeting approximately 30 iterations per second


# Registering the root route for serving the frontend page
@app.route('/')
def index():
    """Serving the main HTML page."""

    # Rendering the frontend template
    return render_template('index.html')


# Registering the video-streaming route
@app.route('/video_feed')
def video_feed():
    """Streaming annotated video frames to the frontend."""

    # Returning the generated frames as a multipart HTTP response
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# Registering the camera-starting endpoint for POST requests
@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    """Starting camera processing."""

    # Updating the shared camera state to active
    global camera_active
    camera_active = True

    # Returning a JSON confirmation of the camera-starting operation
    return jsonify({"status": "success", "message": "Camera started"})


# Registering the camera-stopping endpoint for POST requests
@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    """Stopping camera processing."""

    # Updating the shared camera state to inactive
    global camera_active
    camera_active = False

    # Returning a JSON confirmation of the camera-stopping operation
    return jsonify({"status": "success", "message": "Camera stopped"})


# Registering the camera-switching endpoint for POST requests
@app.route('/api/switch_camera', methods=['POST'])
def switch_camera():
    """Switching between laptop and mobile camera inputs."""

    # Accessing the shared camera-selection setting
    global current_camera

    # Importing request for reading the incoming JSON payload
    from flask import request

    # Extracting the submitted JSON data
    data = request.json

    # Reading the requested camera type while defaulting to the laptop camera
    camera_type = data.get('camera', 'laptop')

    # Validating and applying the requested camera selection
    if camera_type in ['laptop', 'mobile']:
        current_camera = camera_type

        # Returning the selected camera in a JSON response
        return jsonify({"status": "success", "camera": current_camera})

    # Rejecting unsupported camera types with an HTTP 400 response
    return jsonify({"status": "error", "message": "Invalid camera type"}), 400


# Registering the voice-toggle endpoint for POST requests
@app.route('/api/toggle_voice', methods=['POST'])
def toggle_voice():
    """Toggling voice announcements on and off."""

    # Accessing the shared voice setting
    global use_voice

    # Reversing the current voice-enabled state
    use_voice = not use_voice

    # Returning the updated voice state in a JSON response
    return jsonify({"status": "success", "voice_active": use_voice})


# Registering the detection-retrieval endpoint
@app.route('/api/detections')
def get_detections():
    """Retrieving current object detections and summary statistics."""

    # Initializing a list for preparing detection data
    detections_data = []

    # Formatting each detection for frontend consumption
    for det in current_detections:
        detections_data.append({
            "label": det['label'],  # Returning the detected object label
            "confidence": det['confidence'],  # Returning the detection confidence
            "position": det['position'],  # Returning the estimated object position
            "timestamp": datetime.now().strftime("%H:%M:%S")  # Adding the current timestamp
        })

    # Returning detection records and summary statistics as JSON
    return jsonify({
        "detections": detections_data,
        "total_objects": detection_stats["total_objects"],
        "unique_types": len(detection_stats["unique_types"])
    })


# Registering the system-status endpoint
@app.route('/api/status')
def get_status():
    """Retrieving the current camera and voice settings."""

    # Returning the current system state as JSON
    return jsonify({
        "camera_active": camera_active,
        "current_camera": current_camera,
        "voice_active": use_voice
    })


# Checking whether the file is being executed directly
if __name__ == '__main__':

    # Printing the startup banner
    print("\n" + "=" * 50)

    # Announcing the web-server startup
    print("🚀 Smart Object Detection Web Server Starting...")

    # Printing the banner separator
    print("=" * 50)

    # Displaying the local browser address
    print("\n📱 Open your browser and go to:")

    # Displaying the local access URL
    print("   👉 http://localhost:5000")

    # Presenting the usage instructions
    print("\n💡 Instructions:")

    # Listing the first step for opening the frontend
    print("   1. Open the link above in your browser")

    # Listing the second step for starting camera processing
    print("   2. Click 'Start Camera' button")

    # Listing the third step for selecting a camera input
    print("   3. Select Laptop or Mobile camera")

    # Listing the fourth step for viewing the detection output
    print("   4. Watch the magic happen! ✨")

    # Displaying the keyboard shortcut for stopping the server
    print("\n⚠️  Press Ctrl+C to stop the server")

    # Printing the closing banner
    print("=" * 50 + "\n")

    # Starting the Flask development server with threaded request handling
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
