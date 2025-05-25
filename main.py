from sdk.cmd_args import CmdArgs
from sdk.meeting_video_analyzer import MeetingVideoAnalyzer
from sdk.live_stream_analyzer import LiveStreamAnalyzer
from sdk.multiple_person_detector import MultiplePersonDetector
import json
import os

def main():
    args = CmdArgs().parse()
    args_dict = vars(args)  # Convert Namespace to dict

    if args.mode == "file":
        analyzer = MeetingVideoAnalyzer(
            frame_skip=args.frame_skip,
            look_away_thresh=args.look_away_threshold,
            look_mode=args.look_mode  
        )

        if os.path.isfile(args.input):
            result = analyzer.analyze_file(args.input)
            # Add args to the result dict
            result["args"] = args_dict
            with open(args.output, "w") as f:
                json.dump(result, f, indent=4)
            print(f"✅ Report saved to {args.output}")

        elif os.path.isdir(args.input):
            results = analyzer.analyze_folder(args.input)
            # Add args to the batch results as metadata
            output = {
                "args": args_dict,
                "results": results
            }
            with open(args.output, "w") as f:
                json.dump(output, f, indent=4)
            print(f"✅ Batch report saved to {args.output}")

        else:
            print("❌ Invalid input path")

    elif args.mode == "live":
        live_analyzer = LiveStreamAnalyzer(
            look_away_thresh=args.look_away_threshold,
            look_mode=args.look_mode  
        )
        live_analyzer.start()

if __name__ == "__main__":
    counter = MultiplePersonDetector(model_name="yolov8n.pt")  # you can use yolov8s.pt or yolov8m.pt
    result = counter.analyze_video("data/video3.mp4")

    with open("report_people.json", "w") as f:
        json.dump(result, f, indent=4)

    print("✅ Analysis complete")

    #main()
