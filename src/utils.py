import pandas as pd


def get_from_xlsx(path: str, convert_nan: bool = True) -> list[dict] | None:
    """
    :param path: path to excel-file. Must be str.
    :param convert_nan: bool. Flag to convert nan-type into None. Default = True
    :return: list[dict] of operations in path
    """
    if not path.endswith((".xlsx", ".xls")):
        return None
    df = pd.read_excel(path)

    if convert_nan:
        return [{k: v if pd.notna(v) else None for k, v in i.items()} for i in df.to_dict("records")]

    return df.to_dict("records")
