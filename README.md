# Overview

This tool analyzes video recordings of online meetings or live webcam feeds to detect potential engagement issues. It uses computer vision to identify:

- Looking away from the screen
- Head turns
- Multiple people in frame

The analysis can be run in two modes:

1. **File Mode**: Analyze pre-recorded MP4 videos (single file or batch)
2. **Live Mode**: Real-time analysis of webcam feed

Results are saved as JSON reports containing metrics like:

- Number of look-away events
- Total duration of looking away
- Longest look-away duration
- Head turn detection
- Multiple people detection

## Setup Guide

- Install Python 3.10, as MediaPipe supports Python 3.7–3.10
- Create and activate a virtual environment using Python 3.10

```bash
py -3.10 -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
```

Now you can install your required packages inside this environment:

```bash
pip install mediapipe opencv-python numpy
```

or

```bash
py -m pip install mediapipe opencv-python numpy
```

## Example Usage

### Analyze a single `.mp4` file

```bash
python main.py file --input data/video1.mp4 --output report.json
```

### Analyze a folder of `.mp4` files

```bash
python main.py file --input data/videos/ --output batch_report.json
```

### Start webcam stream

```bash
python main.py live
```
