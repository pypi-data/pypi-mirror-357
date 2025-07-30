import logging #consider using loguru
from ujson import dumps, loads #faster than json
import threading
import queue
import time
from datetime import datetime


def log_scope(func):
    """A decorator to log function entry and exit."""
    def wrapper(*args, **kwargs):
        logger.info(f"B% {func.__name__}")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"E% {func.__name__}")
        return result
    return wrapper


class AsyncTraceEventHandler(logging.Handler):
    """
    Custom logging handler for async logging in trace event format.
    """
    def __init__(self, log_file:str, as_daemon:bool = True):
        super().__init__()
        self.log_file = log_file
        self.log_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._process_logs, daemon=True)
        self._thread.start()

    def emit(self, record):
        try:
            self.log_queue.put(record)
        except Exception as e:
            print(f"Error emitting log record: {e}")

    def format(self, record):
        """
        Formats the log record as a trace event JSON object.
        """
        arg_dict = {
                "level": record.levelname,
                "module": record.module,
                "filename": record.pathname,
                "lineno": record.lineno
            }
        match record.getMessage()[0:2].lower():
            case 'b%':
                phase='B'
                record.msg = record.getMessage()[2:].strip()
            case 'e%':
                phase='E'
                record.msg = record.getMessage()[2:].strip()
            case 'c%':
                phase = 'C'
                arg_dict = loads(record.getMessage()[2:])
                record.msg = "counter"
            case _:
                phase = 'I'
        trace_event = {
            "name": record.getMessage(),
            "cat": "logging",
            "ph": phase,
            "ts": int(time.time() * 1000000),  # Timestamp in microseconds
            "pid": record.process,
            "tid": record.thread,
            "args": arg_dict
        }
        return dumps(trace_event)

    def _process_logs(self):
        """
        Worker thread to process log queue and write to file. (note that the formatting is done here for speed)
        """
        event_count = 0
        with open(self.log_file, 'a') as f:
            f.write('[')
            while not self._stop_event.is_set() or not self.log_queue.empty():
                try:
                    log_entry = self.log_queue.get(timeout=0.1)
                    f.write(self.format(log_entry) + ',\n')
                    event_count += 1
                    if event_count > 100:
                        f.flush()
                        event_count=0
                except queue.Empty:
                    continue
            end_event =   {
                "name": "final",
                "cat": "logging",
                "ph": 'M',
                "ts": int(time.time() * 1000000)  # Timestamp in microseconds
            }
            f.write(dumps(end_event))
            f.write(']')
            f.flush()

    def stop(self):
        """
        Signals the thread to stop and waits for it to finish.
        """
        self._stop_event.set()
        self._thread.join()

# Configure the logger
def configure_logger(log_file="trace_events.json"):
    """
    Configure the logger, returns a handler which should be closed in the end (consider a try finally)
    """
    logger = logging.getLogger("trace_logger")
    logger.setLevel(logging.DEBUG)

    # Add the async trace event handler
    handler = AsyncTraceEventHandler(log_file)
    logger.addHandler(handler)
    
    return logger, handler

"""Testing stuff"""
import random
@log_scope
def random_pause(depth):
    if depth>0:
        random_pause(depth-1)
    logger.info(f'c% {{"cats":{random.randint(1,10)}, "dogs":{random.randint(1,10)}}}')
    time.sleep(random.random())
    logger.info(f'c% {{"cats":{random.randint(1,10)}, "dogs":{random.randint(1,10)}}}')


@log_scope
def count_to_5():
    for i in range(0,5):
        random_pause(random.randint(1,10))
        logger.info(f'c% {{"cats":{random.randint(1,10)}, "dogs":{random.randint(1,10)}}}')


if __name__ == "__main__":
    # Example usage
    logger, handler = configure_logger()

    try:
        logger.debug("This is a debug message.")
        logger.info("Info level message.")
        logger.warning("Warning with more details.")
        logger.error("Error occurred.")
        logger.critical("Critical issue!")
        time.sleep(1)  # Allow async processing
        
        count_to_5()
    finally:
        handler.stop()  # Ensure graceful shutdown


