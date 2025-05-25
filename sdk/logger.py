import time
import traceback

class Logger:
    def finished(self, message, start_time=None):
        self.log(f"✅ {message}", start_time)

    def log(self, message, start_time=None):
        if start_time:
            time_spent = time.time() - start_time
            print(f"[INFO] Time spent: [{time_spent:.2f}s] - {message}")
        else:
            print(f"[INFO] {message}")

    def error(self, message, e=None):
        if e:
            print(f"❌ [ERROR] {message}: {e}\n{traceback.format_exc()}")
        else:
            print(f"❌ [ERROR] {message}")