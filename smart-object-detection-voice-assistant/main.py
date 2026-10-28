# Importing OpenCV library for image and video processing
import cv2
# Importing time module for timing operations
import time
# Importing threading module for running tasks in parallel
import threading
# Importing urllib.request for handling URL operations
import urllib.request
# Importing numpy for array manipulations
import numpy as np
# Importing ObjectDetector class from object_detector module
from object_detector import ObjectDetector
# Importing generate_description function from description_nlp module
from description_nlp import generate_description
# Importing speak and listen functions for voice-based interaction
from voice_input import speak, listen  # voice-based interaction


def speak_in_thread(text):
    """
    Running speak() in a separate thread so it doesn't block the main loop.

    Args:
        text (str): Text to be spoken aloud.
    """
    # Starting a daemon thread to run the speak function asynchronously
    threading.Thread(target=speak, args=(text,), daemon=True).start()


def test_mobile_camera(url):
    """
    Testing if the mobile camera stream URL is accessible.

    Args:
        url (str): URL of the mobile camera stream.

    Returns:
        bool: True if the URL responds with status 200, False otherwise.
    """
    try:
        # Opening the URL with a timeout of 3 seconds
        response = urllib.request.urlopen(url, timeout=3)
        # Returning True if the HTTP status is 200 (OK)
        return response.status == 200
    except Exception:
        # Returning False if any error occurs during URL access
        return False


def main():
    """
    Running the main program loop for smart object detection using laptop or mobile camera.
    """
    # Speaking a welcome message and asking for camera choice
    speak("Welcome Boss. Would you like to use the laptop webcam or the mobile phone camera?")
    # Printing prompt message for user input
    print("Listening for camera choice...")
    # Listening for voice input to get user's camera choice
    response = listen()
    # Printing the recognized response
    print(f"You said: {response}")

    # Deciding the camera source based on the response
    if "mobile" in response:
        # Setting to use mobile camera
        use_mobile_camera = True
        # Informing user about selected mobile camera
        speak("You selected mobile phone camera.")
        print("Using mobile phone camera.")
    elif "laptop" in response or "webcam" in response:
        # Setting to use laptop webcam
        use_mobile_camera = False
        # Informing user about selected laptop webcam
        speak("You selected laptop webcam.")
        print("Using laptop webcam.")
    else:
        # Defaulting to laptop webcam if response is unclear
        speak("I couldn't understand your response. Defaulting to laptop webcam.")
        use_mobile_camera = False
        print("Defaulting to laptop webcam.")

    # Creating an instance of ObjectDetector
    detector = ObjectDetector()

    if use_mobile_camera:
        # Setting mobile camera IP webcam URL (update IP as needed)
        url = "http://YOUR_PHONE_IP:8080/shot.jpg"
        # Testing accessibility of the mobile camera URL
        if not test_mobile_camera(url):
            # Preparing error message for inaccessible mobile camera
            error_msg = "Mobile phone camera is not accessible. Please check IP webcam and try again."
            print(error_msg)
            speak(error_msg)
            # Exiting main due to camera access failure
            return
    else:
        # Opening the laptop webcam capture device
        cap = cv2.VideoCapture(0)
        # Checking if the webcam opened successfully
        if not cap.isOpened():
            # Preparing error message for failed webcam opening
            error_msg = "Error: Could not open laptop webcam."
            print(error_msg)
            speak(error_msg)
            # Exiting main due to webcam failure
            return

    # Initializing last speak timestamp to zero
    last_speak_time = 0
    # Setting interval (seconds) between speaking descriptions
    speak_interval = 5

    # Creating a resizable window (normal behavior)
    # This allows the window to be the usual size at startup and be maximized by the user.
    cv2.namedWindow("Smart Object Detection", cv2.WINDOW_NORMAL)
    # Optionally setting an initial window size (width x height). Remove or change if undesired.
    cv2.resizeWindow("Smart Object Detection", 960, 540)
    # NOTE: do NOT set WINDOW_FULLSCREEN here — that would force fullscreen immediately.
    # The user can now click the maximize button (or drag to resize) to expand the window.

    # Starting the main detection loop
    while True:
        # Capturing frame depending on camera choice
        if use_mobile_camera:
            try:
                # Reading image response from the mobile camera URL
                img_resp = urllib.request.urlopen(url)
                # Converting the response to numpy array of bytes
                img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
                # Decoding the numpy array to an OpenCV image frame
                frame = cv2.imdecode(img_np, -1)
            except Exception as e:
                # Printing and speaking error when reading mobile camera fails
                print("Error reading from mobile camera:", e)
                speak("Error accessing mobile camera. Please make sure the app is running.")
                # Breaking the loop on error
                break
        else:
            # Reading a frame from the laptop webcam
            ret, frame = cap.read()
            # Checking if frame reading was successful
            if not ret:
                # Printing and speaking error when webcam frame grab fails
                print("Failed to grab frame")
                speak("Failed to access laptop webcam.")
                # Breaking the loop on failure
                break

        # Running object detection on the captured frame
        detections = detector.detect_objects(frame)

        # Iterating over each detection
        for det in detections:
            # Extracting bounding box coordinates
            x1, y1, x2, y2 = det['bbox']
            # Extracting detected object label
            label = det['label']
            # Getting confidence score if available
            conf = det.get('confidence', None)

            # Drawing a rectangle around the detected object
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Preparing text label for the detected object
            text = f"{label}"
            if conf is not None:
                # Adding confidence score to label text
                text += f": {conf:.2f}"
            # Putting the label text on the frame image
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Generating a natural language description from detected objects
        description = generate_description(detections)
        # Printing the generated description
        print(description)

        # Getting the current time in seconds
        current_time = time.time()
        # Checking if enough time passed since last speaking and description is not empty
        if current_time - last_speak_time > speak_interval and description.strip():
            # Speaking the description in a separate thread
            speak_in_thread(description)
            # Updating last speak time
            last_speak_time = current_time

        # Displaying the current video frame in a window
        cv2.imshow("Smart Object Detection", frame)

        # Checking if 'q' key was pressed to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Breaking the main loop to exit
            break

    # Releasing webcam resource if using laptop webcam
    if not use_mobile_camera:
        cap.release()
    # Destroying all OpenCV windows to clean up
    cv2.destroyAllWindows()


# Checking if this script is run as the main program
if __name__ == "__main__":
    # Running the main function to start the program
    main()