from cmd_args import CmdArgs
from meeting_video_analyzer import MeetingVideoAnalyzer
from live_stream_analyzer import LiveStreamAnalyzer
import json
import os

def main():
    args = CmdArgs().parse()

    if args.mode == "file":
        analyzer = MeetingVideoAnalyzer(frame_skip=args.frame_skip, look_away_thresh=args.look_away_threshold)

        if os.path.isfile(args.input):
            result = analyzer.analyze_file(args.input)
            with open(args.output, "w") as f:
                json.dump(result, f, indent=4)
            print(f"✅ Report saved to {args.output}")

        elif os.path.isdir(args.input):
            results = analyzer.analyze_folder(args.input)
            with open(args.output, "w") as f:
                json.dump(results, f, indent=4)
            print(f"✅ Batch report saved to {args.output}")

        else:
            print("❌ Invalid input path")

    elif args.mode == "live":
        live_analyzer = LiveStreamAnalyzer(look_away_thresh=args.look_away_threshold)
        live_analyzer.start()

if __name__ == "__main__":
    main()
