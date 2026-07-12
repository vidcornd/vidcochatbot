import logging
import sys

def configure_logging(level: int = logging.INFO) -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(name)s: %(message)s"))

    root_logger.addHandler(handler)
    root_logger.setLevel(level)