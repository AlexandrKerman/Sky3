import datetime
import json
from os import getenv
from time import sleep

import pandas as pd
import requests
from dotenv import load_dotenv

from src.loggers import func_logger, views_logger

load_dotenv()
LAYER_KEY = getenv("LAYER_KEY")
SPRATES_KEY = getenv("SPRATES")
SPRATES_KEY_RESERVE = getenv("SPRATES_KEY_RESERVE")


@func_logger(views_logger)
def get_greeting(hour: int) -> str:
    """
    Возвращает приветствие, соответствующее времени суток
    """
    day_time = {0: "Доброй ночи", 1: "Доброе утро", 2: "Добрый день", 3: "Добрый вечер"}
    return day_time[hour // 6]


@func_logger(views_logger)
def get_cards_data(data: list[dict]) -> list[dict]:
    """
    Возвращает информацию по картам.
    """
    df = pd.DataFrame(data, columns=["Номер карты", "Сумма операции", "Категория"])
    df = df[df["Сумма операции"] < 0]
    cards_info = df.groupby("Номер карты").agg({"Сумма операции": "sum"})
    cards_info["Кэшбэк"] = cards_info["Сумма операции"].apply(lambda amount: amount // 100)
    cards_info = cards_info.reset_index()
    cards_info["Номер карты"] = cards_info["Номер карты"].apply(lambda card_number: card_number[1:])
    return cards_info.to_dict("records")


@func_logger(views_logger)
def get_top_transactions(data: list[dict]) -> list[dict]:
    """
    Возвращает топ-5 транзакций по убыванию суммы
    """
    df = pd.DataFrame(data, columns=["Дата операции", "Сумма операции", "Категория", "Описание"])
    df = df[df["Сумма операции"] < 0]
    top_transactions = df.sort_values("Сумма операции").head(5)
    return top_transactions.to_dict("records")


@func_logger(views_logger)
def get_rates() -> list[dict] | None:
    """
    Возвращает актуальные курсы валют
    """
    base_url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": LAYER_KEY}
    payload = {
        "symbols": "USD,EUR",
        "base": "RUB",
    }
    try:
        views_logger.info('Попытка обратиться по API')
        response = requests.request("GET", base_url, headers=headers, params=payload)
    except requests.exceptions.RequestException as e:
        views_logger.error(f'При обращении была получена ошибка {e}')
        print(f"an error occurred: {e}")
    else:
        views_logger.info('Обращение по API прошло успешно.')
        result = json.loads(response.text)
        for k, v in result["rates"].items():
            result["rates"][k] = round(1 / v, 2)
            views_logger.info(f'Получено {k}: {round(1 / v, 2)}')
        views_logger.info('Курс валют будет возвращён')
        return [{"currency": k, "rate": v} for k, v in result["rates"].items()]
    views_logger.info('Возвращается None')
    return None


@func_logger(views_logger)
def get_stock() -> list[dict] | None:
    """
    Возвращает актуальные стоимости акций из S&P500
    """
    stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    prices = []

    url = "https://www.alphavantage.co/query"
    for i in stocks:
        payload = {"function": "GLOBAL_QUOTE", "symbol": i, "apikey": SPRATES_KEY}
        views_logger.info(f'Идёт запрос по основному API для получения {i}')
        response = requests.get(url, params=payload)
        response_json = json.loads(response.text)
        print(f"Идёт запрос по API для получения {i}\n")
        if "Global Quote" in response_json and response_json["Global Quote"]:
            prices.append(
                {
                    "stock": response_json["Global Quote"]["01. symbol"],
                    "price": response_json["Global Quote"]["05. price"],
                }
            )
            views_logger.info(f'{i} получен. {prices[-1]} было добавлено в prices')
        else:
            views_logger.warning('Произошла ошибка при запросе по основному запросу')
            print("При получении данных произошла ошибка. Подключение к резервному API")
            break
        views_logger.info('Ожидание до след. запроса 5с...')
        sleep(5)
        views_logger.info('Ожидание окончено')
    else:
        views_logger.info(f'Возвращается {prices}')
        return prices

    url = "http://api.marketstack.com/v1/eod"
    payload = {
        "access_key": SPRATES_KEY_RESERVE,
        "symbols": ",".join(stocks),
        "limit": len(stocks),
    }
    views_logger.info('Попытка запроса по резервному API')
    response = requests.get(url, params=payload)
    response_json = json.loads(response.text)
    if 'data' in response_json:
        views_logger.info(f'Данные успешно получены.')
        prices = [{"stock": i["symbol"], "price": i["close"]} for i in response_json["data"]]
        views_logger.info(f'{prices} будет возвращено')
        return prices
    else:
        print('Data not captured.')
        views_logger.warning(f'Ответ на запрос пришёл с результатом {response_json}. Будет возвращено None')
        return None


def main_view(date: str, data: list[dict]) -> json:
    """
    Окно Главная. Возвращает JSON с
    — приветствием,
    — информацией по картам,
    — Топ-5 транзакций,
    — Курс рубля к другим валютам,
    — Стомость акций из S&P500
    """
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    json_data = {
        "greeting": get_greeting(date_obj.hour),
        "cards": get_cards_data(data),
        "top_transactions": get_top_transactions(data),
        "currency_rates": get_rates(),
        "stock_prices": get_stock(),
    }

    return json.dumps(json_data, ensure_ascii=False)


@func_logger(views_logger)
def get_expenses_data(data: pd.DataFrame) -> dict:
    """
    Возвращает информацию о тратах по категориям
    """
    expenses_info = {}
    df_expenses = data[data["Сумма операции"] < 0].copy()

    df_expenses["Сумма операции"] = df_expenses["Сумма операции"].abs()
    df_expenses = (
        df_expenses.groupby("Категория").agg({"Сумма операции": "sum"}).sort_values("Сумма операции", ascending=False)
    )
    df_expenses = df_expenses.reset_index()
    df_expenses.rename(columns={"Категория": "category", "Сумма операции": "amount"}, inplace=True)
    df_expenses["amount"] = df_expenses["amount"].round(2)

    expenses_info["total_amount"] = df_expenses.sum()["amount"]

    first = df_expenses.loc[~df_expenses["category"].isin(["Переводы", "Наличные"])].head(7)
    other = df_expenses.loc[~df_expenses["category"].isin(["Переводы", "Наличные"])][7:].sum()

    expenses_info["main"] = first.to_dict("records")
    if other["amount"] != 0:
        other["amount"] = other["amount"].round(2)
        other["category"] = "Остальное"
        expenses_info["main"].append(other.to_dict())
    transfers = df_expenses.loc[df_expenses["category"].isin(["Переводы", "Наличные"])]

    expenses_info["transfers_and_cash"] = transfers.to_dict("records")

    return expenses_info


@func_logger(views_logger)
def get_income_data(data: pd.DataFrame) -> dict:
    """
    Возвращает информацию о пополнениях по категориям
    """
    income_info = {}
    df_income = data[data["Сумма операции"] > 0].copy()

    df_income = (
        df_income.groupby("Категория").agg({"Сумма операции": "sum"}).sort_values("Сумма операции", ascending=False)
    )
    df_income = df_income.reset_index()
    df_income.rename(columns={"Категория": "category", "Сумма операции": "amount"}, inplace=True)

    df_income["amount"] = df_income["amount"].round(2)
    # df_expenses['amount'] = df_expenses['amount'].round(2)
    # income_info['total_amount'] = df_income.sum().to_dict()
    income_info["total_amount"] = df_income.sum()["amount"].round(2)
    income_info["main"] = df_income.to_dict("records")
    return income_info


@func_logger(views_logger)
def events_view(date: str, data: list[dict], *, date_range: str = "M") -> json:
    """
    Окно События. Возвращает JSON с:
    — Информацией о расходах,
    — Информацией о пополнениях,
    — Курсом валют,
    — Стоимости акций
    """
    df = pd.DataFrame(data)
    # df['Дата операции'] = df['Дата операции'].apply(lambda x: datetime.datetime.strptime(x, "%d.%m.%Y %H:%M:%S"))
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    date = datetime.datetime.strptime(date, "%d.%m.%Y")
    match date_range:
        case "W":
            start_date = date - datetime.timedelta(days=date.weekday())
            end_date = start_date + datetime.timedelta(days=6)
            df = df.loc[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
        case "M":
            df = df.loc[(df["Дата операции"].dt.month == date.month) & (df["Дата операции"].dt.year == date.year)]
        case "Y":
            df = df.loc[df["Дата операции"].dt.year == date.year]
        case "ALL":
            df = df.loc[df["Дата операции"] < date + datetime.timedelta(days=1)]
        case _:
            raise ValueError(f"Not supported date_range. Expected W/M/Y/ALL, got {date_range}")

    json_data = {
        "expenses": get_expenses_data(df),
        "income": get_income_data(df),
        "currency_rates": get_rates(),
        "stock_prices": get_stock(),
    }

    return json.dumps(json_data, indent=2, ensure_ascii=False)
