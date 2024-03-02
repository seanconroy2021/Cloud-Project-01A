import datetime
import logging

current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def setup_logger(name, log_file=f"logs/{current_time}.log", level=logging.INFO):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
