from sdk.app.cmd_args import CmdArgs
from sdk.detection.core.analyzer import Analyzer

if __name__ == "__main__":
    args = CmdArgs().parse()
    analyzer = Analyzer(args)
    analyzer.analyze()
    
