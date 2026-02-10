from datetime import datetime


def get_cashback_profit(data: list[dict], /, year:int, month:int):
    """
    :param data: list[dict] positional only.
    :param year: int - year to filter
    :param month: int - moth to filter
    :return: list[dict] of cashback profit by period
    """
    data = [i for i in data if i['Кэшбэк']]
    data = [i for i in data if (date := datetime.strptime(i['Дата операции'], '%d.%m.%Y %H:%M:%S')).year == year and date.month == month]

    cashback_categories = {category for i in data if (category := i.get('Категория'))}
    cashback_amount = {i: [] for i in cashback_categories}

    for i in data:
        cashback_amount[i['Категория']].append(i['Кэшбэк'])
    for k, v in cashback_amount.items():
        cashback_amount[k] = sum(v)

    return cashback_amount