import re
from datetime import datetime
from venv import logger

from src.loggers import create_logger, func_logger

services_logger = create_logger("services_logger")


@func_logger(services_logger)
def get_cashback_profit(data: list[dict], /, year: int, month: int) -> dict:
    """
    :param data: list[dict] positional only.
    :param year: int - year to filter
    :param month: int - moth to filter
    :return: list[dict] of cashback profit by period
    """
    data = [i for i in data if i["Кэшбэк"]]
    data = [
        i
        for i in data
        if (date := datetime.strptime(i["Дата операции"], "%d.%m.%Y %H:%M:%S")).year == year and date.month == month
    ]

    cashback_categories = {category for i in data if (category := i.get("Категория"))}
    cashback_amount = {i: [] for i in cashback_categories}

    for i in data:
        cashback_amount[i["Категория"]].append(i["Кэшбэк"])
    for k, v in cashback_amount.items():
        cashback_amount[k] = sum(v)

    return cashback_amount


@func_logger(services_logger)
def investment_bank(transactions: list[dict], /, month: str, limit: int, raise_zero=True) -> float:
    """
    :param transactions: list[dict] of operations with keys 'Дата операции' and 'Сумма платежа'
    :param month: str - month to slice
    :param limit: int - step to round
    :param raise_zero: bool - raise exception, if limit = 0. Optional, default = True, else return 0
    :return: float: sum of investment
    """
    if limit == 0:
        logger.warning("limit == 0")
        if raise_zero:
            logger.critical("Raised ValueError, because limit = 0 and raise_zero = True")
            raise ValueError("Expected non-zero value in limit")
        else:
            logger.warning("Returned 0, because limit = 0 and raise_zero = False")
            return 0
    month = datetime.strptime(month, "%Y-%m")
    total_amount = 0
    for i in [k for k in transactions if k["Сумма операции"] < 0]:
        if datetime.strptime(i["Дата операции"], "%d.%m.%Y %H:%M:%S") <= month:
            amount = abs(i["Сумма операции"])
            total_amount += ((amount + limit - 1) // limit) * limit - amount
    return round(total_amount, 2)


@func_logger(services_logger)
def simple_search(data: list, /, search: str) -> list:
    """
    Ищет совпадения str в data по ключам Описание и Категория
    :param data: list - data
    :param search: str - string for search in data
    :return: list - list with matches
    """
    pattern = re.compile(search, re.IGNORECASE)
    new_data = []
    for i in data:
        data_str = f"{str(i.get('Описание'))}\n{str(i.get('Категория'))}"
        if pattern.search(data_str):
            new_data.append(i)
    return new_data


@func_logger(services_logger)
def search_by_number(data: list, /) -> list:
    """
    Ищет все транзации с номерами телефона в описании
    :param data: list - data
    :return: list - new data with only telephone numbers
    """
    pattern = re.compile(r"(\+?7|8)((\s|-)?\d(\s|-)?){10}")
    new_data = []
    for i in data:
        if pattern.search(str(i.get("Описание"))):
            new_data.append(i)
    return new_data


@func_logger(services_logger)
def search_by_person(data: list, /) -> list:
    """
    Ищет все транзации с переводом физ. лицу
    :param data: list - data
    :return: list - new data with persons
    """
    pattern = re.compile(r"^\w+ \w\.?$", re.IGNORECASE)
    new_data = []
    for i in data:
        if i.get("Категория") == "Переводы":
            if pattern.search(str(i.get("Описание"))):
                new_data.append(i)
    return new_data
