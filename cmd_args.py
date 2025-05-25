import argparse
import os

class CmdArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Online meeting Behavior Analyzer - Analyze MP4 Online meetings or live webcam feed"
        )

        subparsers = self.parser.add_subparsers(dest="mode", help="Choose mode: file or live", required=True)

        # Subparser for file mode (single or batch)
        file_parser = subparsers.add_parser("file", help="Analyze MP4 video file(s)")
        file_parser.add_argument(
            "--input", "-i", type=str, required=True,
            help="Path to input video file or folder of .mp4 files"
        )
        file_parser.add_argument(
            "--output", "-o", type=str, default="output.json",
            help="Path to save output JSON summary"
        )
        file_parser.add_argument(
            "--frame-skip", type=int, default=5,
            help="Process every Nth frame (default: 5)"
        )
        file_parser.add_argument(
            "--look-away-threshold", type=float, default=0.3,
            help="Threshold for eye center deviation to detect look-away (default: 0.3)"
        )

        # Subparser for live webcam analysis
        live_parser = subparsers.add_parser("live", help="Start live video stream analysis")
        live_parser.add_argument(
            "--look-away-threshold", type=float, default=0.3,
            help="Threshold for eye center deviation to detect look-away (default: 0.3)"
        )

    def parse(self):
        return self.parser.parse_args()
