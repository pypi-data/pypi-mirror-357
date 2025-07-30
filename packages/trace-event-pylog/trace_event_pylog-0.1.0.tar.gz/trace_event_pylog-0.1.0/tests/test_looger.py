from trace_event_pylog.logger import configure_logger, log_scope

def test_logger_runs():
    logger, handler = configure_logger("test_trace.json")
    logger.info("test message")
    handler.stop()