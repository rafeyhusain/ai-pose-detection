from sdk.app.cmd_args import CmdArgs
from sdk.video.video_analysis_manager import VideoAnalysisManager

if __name__ == "__main__":
    args = CmdArgs().parse()
    analyzer = VideoAnalysisManager(args)
    analyzer.analyze()
    
