import logging
import time
import traceback

class Logger:
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)

    def started(self, message, start_time=None):
        self.info(f"🚀 {message}", start_time)

    def finished(self, message, start_time=None):
        self.info(f"✅ {message}", start_time)

    def info(self, message, start_time=None):
        if start_time:
            time_spent = time.time() - start_time
            print(f"[INFO]:[{self.name}]: Time spent: [{time_spent:.2f}s] - {message}")
        else:
            print(f"[INFO]:[{self.name}]: {message}")

    def error(self, message, e=None):
        if e:
            print(f"❌ [ERROR]:[{self.name}]: {message}: {e}\n{traceback.format_exc()}")
        else:
            print(f"❌ [ERROR]:[{self.name}]: {message}")