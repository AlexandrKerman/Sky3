from unittest.mock import patch

import pandas as pd

from src import utils as u


def test_get_from_xlsx(transactions_list):
    with patch('pandas.read_excel') as pd_mock:
        pd_mock.return_value = pd.DataFrame(transactions_list)
        res = u.get_from_xlsx('test.xlsx')
        assert res == transactions_list
