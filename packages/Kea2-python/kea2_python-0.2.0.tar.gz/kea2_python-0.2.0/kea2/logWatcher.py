import re
import os
import threading
import time
from .utils import getLogger


logger = getLogger(__name__)


PATTERN_EXCEPTION = re.compile(r"\[Fastbot\].+Internal\serror\n([\s\S]*)")
PATTERN_STATISTIC = re.compile(r".+Monkey\sis\sover!\n([\s\S]+)")


def thread_excepthook(args):
    print(args.exc_value, flush=True)
    os._exit(1)



class LogWatcher:

    def watcher(self, poll_interval=0.5):
        self.buffer = ""
        self.last_pos = 0

        while not self.end_flag:
            self.read_log()
            time.sleep(poll_interval)
        
        time.sleep(0.2)
        self.read_log()
        
    def read_log(self):
        with open(self.log_file, 'r', encoding='utf-8') as f:
            f.seek(self.last_pos)
            new_data = f.read()
            self.last_pos = f.tell()

            if new_data:
                self.buffer += new_data
            self.parse_log()

    def parse_log(self):
        buffer = self.buffer
        exception_match = PATTERN_EXCEPTION.search(buffer)
        if exception_match:
            exception_body = exception_match.group(1).strip()
            if exception_body:
                raise RuntimeError(
                    "[Error] Execption while running fastbot:\n" + 
                    exception_body + 
                    "\nSee fastbot.log for details."
                )
        if self.end_flag:
            statistic_match = PATTERN_STATISTIC.search(buffer)
            if statistic_match:
                statistic_body = statistic_match.group(1).strip()
                if statistic_body:
                    print(
                        "[INFO] Fastbot exit:\n" + 
                        statistic_body
                    , flush=True)

    def __init__(self, log_file):
        logger.info(f"Watching log: {log_file}")
        self.log_file = log_file
        self.end_flag = False

        threading.excepthook = thread_excepthook
        self.t = threading.Thread(target=self.watcher, daemon=True)
        self.t.start()
    
    def close(self):
        logger.info("Close: LogWatcher")
        self.end_flag = True
        if self.t:
            self.t.join()


if __name__ == "__main__":
    LogWatcher("fastbot.log")