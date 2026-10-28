# Smart Object Detection with Voice Summary for the Visually Impaired

A Python computer-vision prototype that uses YOLOv8 and OpenCV to detect common objects in a camera feed, describe their approximate left/center/right positions, and provide spoken scene summaries.

## Features

- YOLOv8 Nano object detection with bounding boxes and confidence scores
- Scene summaries that count detected objects and describe approximate positions
- Text-to-speech feedback using `pyttsx3`
- Flask dashboard with a video stream and camera controls
- Laptop webcam support, with optional mobile/IP camera support (configure the stream URL in the source first)

## Requirements

- Python 3.10 or 3.11 is recommended for compatibility with the pinned dependencies
- Git
- A webcam for laptop-camera mode
- Microphone and speakers/headphones for voice interaction

Camera and audio features may behave differently across Windows, macOS, and Linux. `SpeechRecognition` uses Google's online speech-recognition service in the current implementation, so voice input requires internet access. The speech output currently uses local `pyttsx3`; this project does not currently use Hugging Face TTS.

## Setup (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the `py -3.11` command is unavailable, install Python 3.11 first or use another supported Python version after adjusting dependencies.

## Run the web dashboard

```powershell
python web_server.py
```

Then open <http://127.0.0.1:5000> in your browser. Allow camera and microphone access if prompted. The Flask server must run on the same computer that can access the webcam; a hosted server generally cannot directly access your personal computer's webcam or speakers.

## Run the command-line camera workflow

```powershell
python main.py
```

This workflow uses microphone input to choose a camera mode. If you prefer not to use voice input, the source code will need a small change to select the camera by configuration or keyboard input.

## Mobile/IP camera

The mobile camera stream URL is configured in `main.py` and `web_server.py`. Update the placeholder/current address to the URL provided by your IP-camera app. Ensure the phone and computer are on the same network and the stream is reachable. Do not publish a private camera URL or credentials in this public repository.

## Model weights

The repository includes `yolov8n.pt` (YOLOv8 Nano weights). Keep the file in the project root because `object_detector.py` loads it by filename.

## Reported performance

The project report describes approximately 85% detection accuracy, 0.12-second latency per frame, and 12–15 FPS on CPU. These are reported project figures and have not been independently reproduced as part of this repository preparation. For a rigorous evaluation, report the dataset, hardware, confidence threshold, precision/recall or mAP, and timing methodology.

## Limitations and safety

- Object detection can miss objects or misclassify scenes; do not rely on it as the sole navigation or obstacle-avoidance aid.
- The current description is based on detected object labels and rough horizontal positions; it does not estimate distance or guarantee safe paths.
- Real-time performance depends on CPU/GPU, camera resolution, and environment.
- Mobile camera mode requires the correct local stream URL.

## Project structure

```text
.
├── main.py
├── object_detector.py
├── description_nlp.py
├── voice_input.py
├── tts_speaker.py
├── web_server.py
├── templates/
│   └── index.html
├── yolov8n.pt
├── requirements.txt
├── .gitignore
└── README.md
```

## License

Add a license only after deciding how you want others to use and redistribute your code. Check the license terms for the included model weights and all dependencies before publishing.
