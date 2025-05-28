import argparse
import sys

class CmdArgs:
    def parse(self):
        parser = argparse.ArgumentParser(
            description="Online meeting Behavior Analyzer - Analyze MP4 Online meetings or live webcam feed",
            add_help=False  # Disable default help
        )

        parser.add_argument("-h", "--help", action="store_true", help="Show full help message and exit")

        subparsers = parser.add_subparsers(dest="mode", required=False)

        # --- file mode ---
        file_parser = subparsers.add_parser("file", help="Analyze MP4 video file(s)")
        file_parser.add_argument("-i", "--input", required=True, help="Input MP4 file or folder path")
        file_parser.add_argument("-o", "--output", required=True, help="Path to save JSON output")
        file_parser.add_argument("--look-mode", default="yaw", choices=["yaw", "yaw_pitch", "gaze"])
        file_parser.add_argument("--frame-skip", type=int, default=1)
        file_parser.add_argument("--look-away-threshold", type=float, default=0.1)

        # --- live mode ---
        live_parser = subparsers.add_parser("live", help="Start live video stream analysis")
        live_parser.add_argument("--look-mode", default="yaw", choices=["yaw", "yaw_pitch", "gaze"])
        live_parser.add_argument("--look-away-threshold", type=float, default=0.1)

        args = parser.parse_args()
        
        # If just --help or -h is passed, print help for everything
        if args.help:
            parser.print_help()
            print("\nSubcommand 'file' options:")
            file_parser.print_help()
            print("\nSubcommand 'live' options:")
            live_parser.print_help()
            sys.exit(0)

        args.input = "data/videos/video5.mp4"
        
        if args.mode == "":
            args.mode = "file"
            
        return args
