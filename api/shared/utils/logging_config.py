import logging
import sys

# Create a custom formatter
formatter = logging.Formatter(
    "%(levelname)-8s:%(name)-12s %(asctime)s %(filename)s:%(funcName)s  |   %(message)s"
)

# Create a StreamHandler that outputs to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

# Configure the root logger
logging.root.handlers = []  # Remove any existing handlers
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)

# Get your specific logger
logger = logging.getLogger("WORKER")
