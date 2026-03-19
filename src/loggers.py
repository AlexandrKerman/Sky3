import logging
from functools import wraps

LOG_DIR = "../logs"


def func_logger(logger: logging.Logger):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            logger.info(f'{func.__name__} была вызвана.')
            res = func(*args, **kwargs)
            logger.info(f'{func.__name__} завершила работу')
            return res

        return inner

    return wrapper


def create_logger(name: str, path: str = LOG_DIR) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")

    handler = logging.FileHandler(f"{path}/{logger.name}.log", mode='w', encoding='utf-8')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


views_logger = create_logger("view_logger")
services_logger = create_logger("services_logger")
reports_logger = create_logger("reports_logger")
