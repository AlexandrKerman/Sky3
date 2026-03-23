import pandas as pd

from src import reports, services, utils, views


# 31.12.2021 - крайняя дата в предоставленном operations.xlsx
def main():
    data = utils.get_from_xlsx("data/operations.xlsx")

    # views.py
    main_view = views.main_view("2021-12-31 22:00:00", data)
    events_view = views.events_view("31.12.2021", data)

    # services.py
    cashback = services.get_cashback_profit(data, year=2021, month=12)
    investment = services.investment_bank(data, month="2018-05", limit=50)
    simple = services.simple_search(data, search="Ж/Д")
    by_number = services.search_by_number(data)
    by_person = services.search_by_person(data)

    # reports.py
    df = pd.DataFrame(data)
    by_category = reports.category_spents(df, "Переводы", "31.12.2021")
    weekly = reports.weekly_spents(df, "31.12.2021")
    average = reports.average_spents(df, "31.12.2021")

    print(f'Окно Главное:\n{main_view}\n{"_"*30}\n')
    print(f'Окно События:\n{events_view}\n{"_"*30}\n')

    print(f'Кэшбэк:\n{cashback}\n{"_"*30}\n')
    print(f'Инвесткопилка:\n{investment}\n{"_"*30}\n')
    print(f'Простой поиск:\n{simple}\n{"_"*30}\n')
    print(f'Поиск по номеру:\n{by_number}\n{"_"*30}\n')
    print(f'Поиск по физ. лицу:\n{by_person}\n{"_"*30}\n')

    print(f'Отчёт по категории:\n{by_category}\n{"_"*30}\n')
    print(f'Отчёт за дни недели:\n{weekly}\n{"_" * 30}\n')
    print(f'Отчёт в среднем:\n{average}\n{"_" * 30}\n')


if __name__ == "__main__":
    main()
