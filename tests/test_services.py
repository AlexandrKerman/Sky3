import pytest

from src import services as s


def test_cashback_profit(transactions_list):
    cashback = s.get_cashback_profit.__wrapped__(transactions_list, year=2026, month=3)
    assert cashback == {"Развлечения": 9, "Аптеки": 7}


def test_investment_bank(transactions_list_Y_M_D):
    investment = s.investment_bank.__wrapped__(transactions_list_Y_M_D, month="2026-03", limit=50)
    assert investment == 70
    investment = s.investment_bank.__wrapped__(transactions_list_Y_M_D, month="2026-03", limit=0, raise_zero=False)
    assert investment == 0
    with pytest.raises(ValueError):
        s.investment_bank.__wrapped__(transactions_list_Y_M_D, month="2026-03", limit=0, raise_zero=True)


def test_simple_search(transactions_list):
    res = s.simple_search.__wrapped__(transactions_list, "Перекрёсток")
    assert res == [
        {
            "Дата операции": "22.08.2025 17:20:00",
            "Сумма операции": -2200,
            "Номер карты": "*4444",
            "Категория": "Супермаркеты",
            "Кэшбэк": 22,
            "Описание": "Перекрёсток",
        }
    ]


def test_search_by_number(transactions_list):
    res = s.search_by_number.__wrapped__(transactions_list)
    assert res == [
        {
            "Дата операции": "15.03.2026 11:25:00",
            "Сумма операции": -1200,
            "Номер карты": "*4444",
            "Категория": "Переводы",
            "Кэшбэк": 0,
            "Описание": "+7 912 345-67-89",
        }
    ]


def test_search_by_person(transactions_list):
    res = s.search_by_person.__wrapped__(transactions_list)
    assert res == [
        {
            "Дата операции": "22.01.2026 14:30:00",
            "Сумма операции": -1000,
            "Номер карты": "*4444",
            "Категория": "Переводы",
            "Кэшбэк": 0,
            "Описание": "Иван Б.",
        },
        {
            "Дата операции": "28.01.2026 18:45:00",
            "Сумма операции": -2000,
            "Номер карты": "*2222",
            "Категория": "Переводы",
            "Кэшбэк": 0,
            "Описание": "Анна П.",
        },
        {
            "Дата операции": "14.02.2026 16:20:00",
            "Сумма операции": -3000,
            "Номер карты": "*4444",
            "Категория": "Переводы",
            "Кэшбэк": 0,
            "Описание": "Сергей В.",
        },
        {
            "Дата операции": "05.03.2026 19:30:00",
            "Сумма операции": -800,
            "Номер карты": "*4444",
            "Категория": "Переводы",
            "Кэшбэк": 0,
            "Описание": "Ольга К.",
        },
    ]
