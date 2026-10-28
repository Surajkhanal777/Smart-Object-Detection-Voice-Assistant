"""
Web Server to bridge Python detection with Web Frontend
Run this file instead of main.py to use the web interface
"""

from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import urllib.request
import threading
import time
from datetime import datetime

# Import your existing modules
from object_detector import ObjectDetector
from description_nlp import generate_description
from voice_input import speak

app = Flask(__name__)
CORS(app)

# Global variables
detector = ObjectDetector()
camera_active = False
current_camera = "laptop"  # "laptop" or "mobile"
use_voice = True
last_speak_time = 0
speak_interval = 5
mobile_url = "http://192.168.1.48:8080/shot.jpg"

# Store detection data
current_detections = []
detection_stats = {
    "total_objects": 0,
    "unique_types": set()
}


def speak_async(text):
    """Speak in a separate thread so it doesn't block"""
    if use_voice:
        threading.Thread(target=speak, args=(text,), daemon=True).start()


def get_frame():
    """Get frame from the active camera"""
    global current_camera

    if current_camera == "mobile":
        try:
            img_resp = urllib.request.urlopen(mobile_url, timeout=2)
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(img_np, -1)
            return frame
        except Exception as e:
            print(f"Mobile camera error: {e}")
            return None
    else:
        # Laptop camera
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None


def generate_frames():
    """Generate video frames with detections"""
    global camera_active, current_detections, last_speak_time, detection_stats

    while camera_active:
        frame = get_frame()

        if frame is None:
            time.sleep(0.1)
            continue

        # Detect objects
        detections = detector.detect_objects(frame)
        current_detections = detections

        # Update statistics
        detection_stats["total_objects"] = len(detections)
        for det in detections:
            detection_stats["unique_types"].add(det['label'])

        # Draw bounding boxes
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = det['label']
            conf = det['confidence']

            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            text = f"{label}: {conf:.2f}"
            cv2.putText(frame, text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Voice announcement
        current_time = time.time()
        if current_time - last_speak_time > speak_interval and detections:
            description = generate_description(detections)
            speak_async(description)
            last_speak_time = current_time

        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        # Yield frame in multipart format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.03)  # ~30 FPS


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    """Start the camera"""
    global camera_active
    camera_active = True
    return jsonify({"status": "success", "message": "Camera started"})


@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    """Stop the camera"""
    global camera_active
    camera_active = False
    return jsonify({"status": "success", "message": "Camera stopped"})


@app.route('/api/switch_camera', methods=['POST'])
def switch_camera():
    """Switch between laptop and mobile camera"""
    global current_camera
    from flask import request

    data = request.json
    camera_type = data.get('camera', 'laptop')

    if camera_type in ['laptop', 'mobile']:
        current_camera = camera_type
        return jsonify({"status": "success", "camera": current_camera})

    return jsonify({"status": "error", "message": "Invalid camera type"}), 400


@app.route('/api/toggle_voice', methods=['POST'])
def toggle_voice():
    """Toggle voice on/off"""
    global use_voice
    use_voice = not use_voice
    return jsonify({"status": "success", "voice_active": use_voice})


@app.route('/api/detections')
def get_detections():
    """Get current detections"""
    detections_data = []
    for det in current_detections:
        detections_data.append({
            "label": det['label'],
            "confidence": det['confidence'],
            "position": det['position'],
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

    return jsonify({
        "detections": detections_data,
        "total_objects": detection_stats["total_objects"],
        "unique_types": len(detection_stats["unique_types"])
    })


@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        "camera_active": camera_active,
        "current_camera": current_camera,
        "voice_active": use_voice
    })


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🚀 Smart Object Detection Web Server Starting...")
    print("=" * 50)
    print("\n📱 Open your browser and go to:")
    print("   👉 http://localhost:5000")
    print("\n💡 Instructions:")
    print("   1. Open the link above in your browser")
    print("   2. Click 'Start Camera' button")
    print("   3. Select Laptop or Mobile camera")
    print("   4. Watch the magic happen! ✨")
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("=" * 50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)