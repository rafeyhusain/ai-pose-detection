from sdk.app.cmd_args import CmdArgs
from sdk.app.logger import Logger
from sdk.detection.head.head_file_analyzer import HeadFileAnalyzer
from sdk.detection.head.head_request import HeadRequest
from sdk.detection.person.person_file_analyzer import PersonFileAnalyzer
from sdk.detection.person.person_request import PersonRequest

class Analyzer:
    def __init__(self, args: CmdArgs):
        self.args = args
        self.logger = Logger(__name__)

    def analyze(self):
        self.logger.started(f"Started analyzing video")

        self.args.mode = "file"

        if self.args.mode == "file":
            self.analyze_people()
            #self.analyze_head()

        elif self.args.mode == "live":
            pass

        else:
            self.logger.error(f"invalid mode [{self.args.mode}]")

        self.logger.finished(f"Finished analyzing video")


    def analyze_people(self):
        request = PersonRequest.sample()
        analyzer = PersonFileAnalyzer(request)
        analyzer.analyze()  

    def analyze_head(self):
        request = HeadRequest.sample()
        analyzer = HeadFileAnalyzer(request)
        analyzer.analyze()
