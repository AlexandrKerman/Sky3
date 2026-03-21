import pandas as pd

from src import reports as r


def test_get_expenses(transactions_list):
    data = pd.DataFrame(transactions_list[:3])
    res = r.get_expenses.__wrapped__(data)["Сумма операции"].to_dict()
    assert res == {0: 1000, 1: 1500, 2: 2000}


def test_weekly(transactions_list):
    data = pd.DataFrame(transactions_list[:3])
    res = r.weekly_spents.__wrapped__.__wrapped__(data, "20.03.2026")
    assert res.to_dict("records") == [
        {"День недели": "Воскресенье", "Сумма операции": 1500},
        {"День недели": "Среда", "Сумма операции": 2000},
        {"День недели": "Четверг", "Сумма операции": 1000},
    ]


def test_category(transactions_list):
    data = pd.DataFrame(transactions_list)
    res = r.category_spents.__wrapped__.__wrapped__(data, "Переводы", "20.03.2026")
    assert res["Сумма операции"].to_dict() == {0: 1000, 2: 2000, 6: 3000, 10: 800, 14: 1200}


def test_average(transactions_list):
    data = pd.DataFrame(transactions_list)
    res = r.average_spents.__wrapped__.__wrapped__(data, "20.03.2026")
    assert res.to_dict("records") == [
        {"weekday": "Будний день", "Сумма операции": 1200.0},
        {"weekday": "Выходной день", "Сумма операции": 1900.0},
    ]
