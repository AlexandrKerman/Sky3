from datetime import datetime


def get_cashback_profit(data: list[dict], /, year: int, month: int):
    """
    :param data: list[dict] positional only.
    :param year: int - year to filter
    :param month: int - moth to filter
    :return: list[dict] of cashback profit by period
    """
    data = [i for i in data if i['Кэшбэк']]
    data = [i for i in data if
            (date := datetime.strptime(i['Дата операции'], '%d.%m.%Y %H:%M:%S')).year == year and date.month == month]

    cashback_categories = {category for i in data if (category := i.get('Категория'))}
    cashback_amount = {i: [] for i in cashback_categories}

    for i in data:
        cashback_amount[i['Категория']].append(i['Кэшбэк'])
    for k, v in cashback_amount.items():
        cashback_amount[k] = sum(v)

    return cashback_amount


def investment_bank(transactions: list[dict], /, month: str, limit: int, raise_zero=True) -> float:
    """
    :param transactions: list[dict] of operations with keys 'Дата операции' and 'Сумма платежа'
    :param month: str - month to slice
    :param limit: int - step to round
    :param raise_zero: bool - raise exception, if limit = 0. Optional, default = True, else return 0
    :return: float: sum of investment
    """
    if limit == 0:
        if raise_zero:
            raise ValueError('Expected non-zero value in limit')
        else:
            return 0
    month = datetime.strptime(month, '%Y-%m')
    total_amount = 0
    for i in transactions:
        if datetime.strptime(i['Дата операции'], '%Y-%m-%d') <= month:
            amount = i['Сумма операции']
            total_amount += ((amount + limit - 1) // limit) * limit - amount
    return total_amount



