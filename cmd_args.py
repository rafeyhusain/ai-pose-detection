import argparse

class CmdArgs:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Video Behavior Analysis")
        subparsers = parser.add_subparsers(dest="mode", required=True)

        # File mode
        file_parser = subparsers.add_parser("file")
        file_parser.add_argument("--input", required=True, help="Path to video file or folder")
        file_parser.add_argument("--output", required=True, help="Output JSON path")
        file_parser.add_argument("--look_mode", choices=["yaw", "yaw_pitch", "gaze"], default="yaw", help="Look-away detection mode")

        # Streaming mode (if you implement it)
        stream_parser = subparsers.add_parser("stream")
        stream_parser.add_argument("--camera", type=int, default=0, help="Camera index")
        stream_parser.add_argument("--look_mode", choices=["yaw", "yaw_pitch", "gaze"], default="yaw", help="Look-away detection mode")

        self.args = parser.parse_args()

    def get(self):
        return self.args
