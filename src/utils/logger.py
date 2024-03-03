import logging
from datetime import datetime

import colorlog

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")


def setup_logger(name, log_file=f"logs/{current_time}.log", level=logging.INFO):
    color_formatter = colorlog.ColoredFormatter(
        "%(asctime)s - %(log_color)s%(name)s - %(levelname)s%(reset)s - %(message)s"
    )

    plain_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(plain_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(color_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
