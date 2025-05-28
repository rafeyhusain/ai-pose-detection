from sdk.app.cmd_args import CmdArgs
from sdk.video.video_analysis_manager import VideoAnalysisManager
from sdk.video.video_analysis_request import VideoAnalysisRequest

if __name__ == "__main__":
    args = CmdArgs().parse()
    request = VideoAnalysisRequest.sample()
    analyzer = VideoAnalysisManager(request)
    analyzer.analyze()
    
