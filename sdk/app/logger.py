import logging
import time
import traceback

class Logger:
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)

    def started(self, message, start_time=None):
        self.log(message, "STARTED", "🚀", start_time)

    def finished(self, message, start_time=None):
        self.log(message, "FINISHED", "✅", start_time)

    def success(self, message, start_time=None):
        self.log(message, "FAILED", "✨", start_time)

        self.info(f" {message}", start_time)

    def failed(self, message, start_time=None):
        self.log(message, "SUCCESS", "💥", start_time)

    def info(self, message, start_time=None):
        self.log(message, "INFO", "ℹ️", start_time)

    def log(self, message, type, icon, start_time=None):
        if start_time:
            time_spent = time.time() - start_time
            print(f"{icon} [{type}]:[{self.name}]: Time spent: [{time_spent:.2f}s] - {message}")
        else:
            print(f"{icon} [{type}]:[{self.name}]: {message}")

    def error(self, message, e=None, stack=True):
        if e:
            print(f"❌ [ERROR]:[{self.name}]: {message}: {e}" + (f"\n{traceback.format_exc()}" if stack else ""))
        else:
            print(f"❌ [ERROR]:[{self.name}]: {message}")