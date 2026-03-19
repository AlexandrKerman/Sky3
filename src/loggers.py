import logging

LOG_DIR = "../logs"


def create_logger(name: str, path: str = LOG_DIR) -> logging.Logger:
    logger = logging.getLogger(name)

    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")

    handler = logging.FileHandler(f"{path}/{logger.name}.log")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


views_logger = create_logger("view_logger")
services_logger = create_logger("services_logger")
reports_logger = create_logger("reports_logger")
