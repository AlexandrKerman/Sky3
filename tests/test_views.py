from unittest.mock import patch, Mock

import pandas as pd
import pytest
from src import views as v


@pytest.mark.parametrize(
    "hours, expected",
    (
        (6, "Доброе утро"),
        (7, "Доброе утро"),
        (10, "Доброе утро"),
        (12, "Добрый день"),
        (13, "Добрый день"),
        (15, "Добрый день"),
        (18, "Добрый вечер"),
        (19, "Добрый вечер"),
        (23, "Добрый вечер"),
        (0, "Доброй ночи"),
        (4, "Доброй ночи"),
    ),
)
def test_get_greeting(hours, expected):
    assert v.get_greeting.__wrapped__(hours) == expected


def test_get_cards_data(transactions_list):
    res = v.get_cards_data.__wrapped__(transactions_list)
    assert res == [
        {"Номер карты": "2222", "Сумма операции": -7500, "Кэшбэк": -75},
        {"Номер карты": "4444", "Сумма операции": -13400, "Кэшбэк": -134},
    ]


def test_get_top_transactions(transactions_list):
    res = v.get_top_transactions.__wrapped__(transactions_list)
    assert res == [
        {
            "Дата операции": "18.07.2025 10:15:00",
            "Сумма операции": -3400,
            "Категория": "Бытовая техника",
            "Описание": "DNS",
        },
        {
            "Дата операции": "14.02.2026 16:20:00",
            "Сумма операции": -3000,
            "Категория": "Переводы",
            "Описание": "Сергей В.",
        },
        {
            "Дата операции": "18.02.2026 13:45:00",
            "Сумма операции": -2500,
            "Категория": "Одежда и обувь",
            "Описание": "Zarina",
        },
        {
            "Дата операции": "22.08.2025 17:20:00",
            "Сумма операции": -2200,
            "Категория": "Супермаркеты",
            "Описание": "Перекрёсток",
        },
        {
            "Дата операции": "28.01.2026 18:45:00",
            "Сумма операции": -2000,
            "Категория": "Переводы",
            "Описание": "Анна П.",
        },
    ]


def test_get_rates():
    with patch("requests.request") as r_mock:
        r_mock.return_value.text = '{"rates": {"USD": 0.1, "EUR": 0.2}}'
        res = v.get_rates.__wrapped__()
        assert res == [{"currency": "USD", "rate": 10.0}, {"currency": "EUR", "rate": 5.0}]


def test_get_stock():
    with patch("src.views.sleep"):
        with patch("requests.get") as r_mock:
            r_mock.return_value.text = '{"Global Quote": {"01. symbol": "TEST", "05. price": 100}}'
            res = v.get_stock.__wrapped__()
            assert res == [
                {"stock": "TEST", "price": 100},
                {"stock": "TEST", "price": 100},
                {"stock": "TEST", "price": 100},
                {"stock": "TEST", "price": 100},
                {"stock": "TEST", "price": 100},
            ]

            r_mock.return_value.text = '{"data": [{"symbol": "TEST", "close": 100}]}'
            res = v.get_stock.__wrapped__()
            assert res == [{"stock": "TEST", "price": 100}]


def test_main_view(transactions_list):
    # mock_greeting = Mock(return_value='Добрый вечер')
    # mock_cards = Mock(return_value={'card': 2222})
    # mock_top = Mock(return_value=['top1', 'top2'])
    mock_rates = Mock(
        return_value=[
            {"currency": "USD", "rate": 80},
        ]
    )
    mock_stock = Mock(return_value=[{"stock": "TEST", "price": 100}, {"stock": "TEST1", "price": 200}])
    v.get_rates = mock_rates
    v.get_stock = mock_stock
    res = v.main_view(date="2025-12-01 22:00:00", data=transactions_list[:2])
    assert (
        res == '{"greeting": "Добрый вечер", "cards": [{"Номер карты": "4444", "Сумма операции": -2500, '
        '"Кэшбэк": -25}], "top_transactions": [{"Дата операции": "25.01.2026 09:15:00", '
        '"Сумма операции": -1500, "Категория": "Супермаркеты", "Описание": "Пятёрочка"}, '
        '{"Дата операции": "22.01.2026 14:30:00", "Сумма операции": -1000, "Категория": "Переводы", '
        '"Описание": "Иван Б."}], "currency_rates": [{"currency": "USD", "rate": 80}], '
        '"stock_prices": [{"stock": "TEST", "price": 100}, {"stock": "TEST1", "price": 200}]}'
    )


def test_get_expenses_data(transactions_list):
    data = pd.DataFrame(transactions_list[:3])
    res = v.get_expenses_data.__wrapped__(data)
    assert res == {
        "total_amount": 4500,
        "main": [{"category": "Супермаркеты", "amount": 1500}],
        "transfers_and_cash": [{"category": "Переводы", "amount": 3000}],
    }


def test_get_income_data(transactions_list):
    data = pd.DataFrame(transactions_list[:5])
    res = v.get_income_data.__wrapped__(data)
    assert res == {"total_amount": 5000, "main": [{"category": "Пополнения", "amount": 5000}]}
