import logging
import os

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = logging.DEBUG if os.getenv("FLASK_DEBUG") == "1" else logging.INFO
    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
