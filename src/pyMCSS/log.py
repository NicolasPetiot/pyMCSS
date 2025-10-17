from .params import LOG_LVL, SHOW_STREAM, LOG_FILENAME
import logging

log = logging.getLogger(__name__)

match LOG_LVL.upper():
    case "DEBUG":
        log.setLevel(logging.DEBUG)
    case "INFO":
        log.setLevel(logging.INFO)
    case "WARNING":
        log.setLevel(logging.WARNING)
    case "ERROR":
        log.setLevel(logging.ERROR)
    case "CRITICAL":
        log.setLevel(logging.CRITICAL)

formatter = logging.Formatter(
    fmt="[%(asctime)s %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if SHOW_STREAM:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)

if LOG_FILENAME is not None:
    file_handler = logging.FileHandler(LOG_FILENAME)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    
log.propagate = False
log.debug("Logger initialized!")
