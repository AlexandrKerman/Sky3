import datetime
import json
from os import getenv
from time import sleep

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
LAYER_KEY = getenv("LAYER_KEY")
SPRATES_KEY = getenv("SPRATES")
SPRATES_KEY_RESERVE = getenv("SPRATES_KEY_RESERVE")


def get_greeting(hour):
    day_time = {0: "Доброй ночи", 1: "Доброе утро", 2: "Добрый день", 3: "Добрый вечер"}
    return day_time[hour // 6]


def get_cards_data(data):
    df = pd.DataFrame(data, columns=["Номер карты", "Сумма операции", "Категория"])
    df = df[df["Сумма операции"] < 0]
    cards_info = df.groupby("Номер карты").agg({"Сумма операции": "sum"})
    cards_info["Кэшбэк"] = cards_info["Сумма операции"].apply(lambda amount: amount // 100)
    cards_info = cards_info.reset_index()
    cards_info["Номер карты"] = cards_info["Номер карты"].apply(lambda card_number: card_number[1:])
    return cards_info.to_dict("records")


def get_top_transactions(data):
    df = pd.DataFrame(data, columns=["Дата операции", "Сумма операции", "Категория", "Описание"])
    df = df[df["Сумма операции"] < 0]
    top_transactions = df.sort_values("Сумма операции").head(5)
    return top_transactions.to_dict("records")


def get_rates():
    base_url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": LAYER_KEY}
    payload = {
        "symbols": "USD,EUR",
        "base": "RUB",
    }
    try:
        response = requests.request("GET", base_url, headers=headers, params=payload)
    except requests.exceptions.RequestException as e:
        print(f"an error occurred: {e}")
    else:
        result = json.loads(response.text)
        for k, v in result["rates"].items():
            result["rates"][k] = round(1 / v, 2)
        return [{"currency": k, "rate": v} for k, v in result["rates"].items()]
    return None


def get_stock():

    stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    prices = []

    url = "https://www.alphavantage.co/query"
    for i in stocks:
        payload = {"function": "GLOBAL_QUOTE", "symbol": i, "apikey": SPRATES_KEY}
        response = requests.get(url, params=payload)
        response_json = json.loads(response.text)
        sleep(5)
        if "Global Quote" in response_json and response_json["Global Quote"]:
            prices.append(
                {
                    "stock": response_json["Global Quote"]["01. symbol"],
                    "price": response_json["Global Quote"]["05. price"],
                }
            )
        else:
            break
    else:
        return prices

    url = "http://api.marketstack.com/v1/eod"
    payload = {
        "access_key": SPRATES_KEY_RESERVE,
        "symbols": ",".join(stocks),
        "limit": len(stocks),
    }
    response = requests.get(url, params=payload)
    response_json = json.loads(response.text)
    print(response_json)
    prices = [{"stock": i["symbol"], "price": i["close"]} for i in response_json["data"]]
    return prices


def main_view(date, data):
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    json_data = {
        "greeting": get_greeting(date_obj.hour),
        "cards": get_cards_data(data),
        "top_transactions": get_top_transactions(data),
        "currency_rates": get_rates(),
        "stock_prices": get_stock(),
    }

    with open("txt.json", "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)
        file.close()


if __name__ == "__main__":
    from src import utils

    data = utils.get_from_xlsx("../data/operations.xlsx")
    main_view("2025-12-05 22:34:41", data)
