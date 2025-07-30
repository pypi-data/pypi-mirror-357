import os
import logging
from logging.handlers import RotatingFileHandler


MAGIC_CENTER_UTIL_LOG_DIR = os.getenv("MAGIC_CENTER_LOG_DIR")
if not os.path.exists(MAGIC_CENTER_UTIL_LOG_DIR):
    os.makedirs(MAGIC_CENTER_UTIL_LOG_DIR)
logger = logging.Logger("magic_center_util_logger")
log_handler = RotatingFileHandler(f"{MAGIC_CENTER_UTIL_LOG_DIR}/magic_center_util.log",
                                  maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
log_handler.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)


def get_spire_license(file_path: str):
    with open(file_path, 'r') as file:
        return file.read()


def get_host_end_point():
    environment = os.environ.get("ENVIRONMENT")
    logger.debug("environment --> " + environment)
    if environment == "prod":
        end_point = os.environ.get("HOST_END_POINT_PROD")
    else:
        end_point = os.environ.get("HOST_END_POINT_LOCAL")
    return end_point
