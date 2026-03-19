import datetime
from functools import wraps

import pandas as pd

from src.loggers import func_logger, reports_logger


def save_df_return(filename: str = "report.txt"):
    """Сохраняет Dataframe в txt"""

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            res = func(*args, **kwargs)
            with open(f"{func.__name__} - {filename}", "w", encoding="utf-8") as file:
                file.write(res.to_string())
            return res

        return inner

    return wrapper


@func_logger(reports_logger)
def get_dy_date_range(transactions: pd.DataFrame, date: datetime.datetime) -> pd.DataFrame:
    """
    Формирует выборку транзакций за 3 месяца до date включительно
    """
    date = date.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    df = df[(df["Дата операции"] < date) & (df["Дата операции"] >= date - pd.DateOffset(months=3))]

    return df


@func_logger(reports_logger)
def get_expenses(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Формирует выборку из отрицательных транзакций - трат
    """
    transactions = transactions[transactions["Сумма операции"] < 0]
    transactions["Сумма операции"] = transactions["Сумма операции"].abs()
    return transactions


@func_logger(reports_logger)
@save_df_return()
def category_spents(transactions: pd.DataFrame, category_name: str, date: str | None = None) -> pd.DataFrame:
    """
    Формирует отчёт по затратам по категории
    """
    date = datetime.datetime.now() if not date else datetime.datetime.strptime(date, "%d.%m.%Y")

    df = get_dy_date_range(transactions, date)
    df = get_expenses(df)
    df = df[df["Категория"] == category_name]
    df["Сумма операции"] = df["Сумма операции"].round(2)

    return df


@func_logger(reports_logger)
@save_df_return()
def weekly_spents(transactions: pd.DataFrame, date: str | None = None) -> pd.DataFrame:
    """
    Формирует отчёт о тратах по дням недели
    """
    weekdays = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье",
    }

    date = datetime.datetime.now() if not date else datetime.datetime.strptime(date, "%d.%m.%Y")

    df = get_dy_date_range(transactions, date)
    df = get_expenses(df)

    df["День недели"] = df["Дата операции"].apply(lambda x: weekdays[x.weekday()])
    grouped_df = df.groupby("День недели").agg({"Сумма операции": "sum"})
    grouped_df.reset_index(inplace=True)
    grouped_df["Сумма операции"] = grouped_df["Сумма операции"].round(2)

    return grouped_df


@func_logger(reports_logger)
@save_df_return()
def average_spents(transactions: pd.DataFrame, date: str | None) -> pd.DataFrame:
    """
    Формирует отчёт о средних тратах в выходные и рабочие дни
    """
    date = datetime.datetime.now() if not date else datetime.datetime.strptime(date, "%d.%m.%Y")

    df = get_dy_date_range(transactions, date)
    df = get_expenses(df)

    df["weekday"] = df["Дата операции"].apply(lambda x: "Будний день" if x.weekday() <= 4 else "Выходной день")

    grouped_df = df.groupby("weekday").agg({"Сумма операции": "mean"})
    grouped_df.reset_index(inplace=True)
    grouped_df["Сумма операции"] = grouped_df["Сумма операции"].round(2)

    return grouped_df
