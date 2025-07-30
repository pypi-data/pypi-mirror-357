# pylog
Python Logger library

An asynchronous trace event logger using Python's logging system. Outputs Chrome-compatible trace event JSON logs.


## Example

```python
from async_trace_logger import configure_logger, log_scope

logger, handler = configure_logger()

@log_scope
def my_function():
    logger.info("Running something...")

my_function()
handler.stop()