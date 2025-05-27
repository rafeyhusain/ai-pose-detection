# Overview

This tool analyzes video recordings of online meetings or live webcam feeds to detect potential engagement issues. It uses computer vision to identify:

- Looking away from the screen
- Head turns
- Multiple people in frame

The analysis can be run in two modes:

1. **File Mode**: Analyze pre-recorded MP4 videos (single file or batch)
2. **Live Mode**: Real-time analysis of webcam feed

Results are saved as JSON reports containing metrics:

```json
{
  "multiple_people_detected": {
    "detected": bool,
    "confidence": float,
    "detected_timestamps": [
      {
        "confidence": float,
        "detected_people": int,
        "image": "base64 or path to frame image",
        "timestamp": float
      }
    ]
  },
  "eye_head_tracking": {
    "detected": bool,
    "confidence": float,
    "eye_tracking_flags": [
      {
        "confidence": float,
        "image": "base64 or path to frame image",
        "timestamp": float
      }
    ],
    "heapq_tracking_flags": [
      {
        "confidence": float,
        "image": "base64 or path to frame image",
        "timestamp": float
      }
    ]
  }
}
```

## Setup Guide

- Install Python 3.10, as MediaPipe supports Python 3.7–3.10
- Run `winget install ffmpeg`
- Create and activate a virtual environment using Python 3.10

```bash
py -3.10 -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
```

Now you can install your required packages inside this environment:

```bash
pip install mediapipe opencv-python numpy ultralytics pydantic
```

## Example Usage

### Analyze a single `.mp4` file

```bash
python main.py file --input data/video1.mp4 --output report.json --frame-skip 1 --look-away-threshold 0.1 --look-mode yaw
```

### Analyze a folder of `.mp4` files

```bash
python main.py file --input data/videos/ --output batch_report.json
```

### Start webcam stream

```bash
python main.py live
```
