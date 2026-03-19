import datetime
import json
from functools import wraps

import pandas as pd


def save_df_return(filename='report.md'):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            res = func(*args, **kwargs)
            with open(f'{func.__name__} - {filename}', 'w', encoding='utf-8') as file:
                file.write(res.to_string())
            return res

        return inner

    return wrapper


def get_dy_date_range(transactions: pd.DataFrame, date: datetime.datetime) -> pd.DataFrame:
    date = date.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

    df = transactions.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S')

    df = df[(df['Дата операции'] < date) & (df['Дата операции'] >= date - pd.DateOffset(months=3))]

    return df


@save_df_return()
def category_spents(transactions: pd.DataFrame, category_name: str, date: str | None = None) -> pd.DataFrame:
    date = datetime.datetime.now() if not date else datetime.datetime.strptime(date, '%d.%m.%Y')

    df = get_dy_date_range(transactions, date)
    df = df[df['Категория'] == category_name]

    return df
