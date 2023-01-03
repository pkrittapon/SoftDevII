from data.function import Stock,Categories

import unittest
from unittest.mock import MagicMock,patch
import pandas as pd

def get_stock_and_crypto_data(name):
    import yfinance as yf
    data = yf.download(tickers=name) #get data
    data = data.loc[data["Volume"] != 0 ].drop(["Adj Close"],axis = 1)# ไม่เอาค่า volume = 0
    data["Date"] = data.index.strftime('%Y-%m-%d %X') # convert pandas timestamp to string 
    return data.values.tolist() #return value in type list



class test_pull_data(unittest.TestCase):
    # Create a mock return value for the yfinance.download function
    def test_pull1(self):
        yfinance_mock = unittest.mock.MagicMock()
        data = {'Open': [50.0, 52.0, 48.0],
                'High': [50.25,52.0,49.0],
                'Low': [48.0,49.0,47.0],
                'Close': [49.75,52.0,48.5],
                'Adj Close':[49.75,51.75,48.5],
                'Volume':[24543,67854,16875]}

        data_date = pd.DataFrame(data, index=[pd.to_datetime('2022-12-25 09:30:00'),
                                        pd.to_datetime('2022-12-26 10:30:00'),
                                        pd.to_datetime('2022-12-27 15:30:00')])

        yfinance_mock.download.return_value = data_date
        with unittest.mock.patch('yfinance.download',yfinance_mock.download):
            result = get_stock_and_crypto_data("TESTTEST")
            assert result == [[50.0,50.25,48.0,49.75,24543,'2022-12-25 09:30:00'],[52.0, 52.0, 49.0, 52.0, 67854, '2022-12-26 10:30:00'],[48.0, 49.0, 47.0, 48.5, 16875,'2022-12-27 15:30:00']]

    def test_pull2(self):
        yfinance_mock = unittest.mock.MagicMock()
        data = {'Open': [50.0, 52.0, 48.0],
                'High': [50.25,52.0,49.0],
                'Low': [48.0,49.0,47.0],
                'Close': [49.75,52.0,48.5],
                'Adj Close':[49.75,51.75,48.5],
                'Volume':[0,67854,16875]}

        data_date = pd.DataFrame(data, index=[pd.to_datetime('2022-12-25 09:30:00'),
                                        pd.to_datetime('2022-12-26 10:30:00'),
                                        pd.to_datetime('2022-12-27 15:30:00')])

        yfinance_mock.download.return_value = data_date
        with unittest.mock.patch('yfinance.download',yfinance_mock.download):
            result = get_stock_and_crypto_data("TESTTEST")
            assert result == [[52.0, 52.0, 49.0, 52.0, 67854, '2022-12-26 10:30:00'],[48.0, 49.0, 47.0, 48.5, 16875,'2022-12-27 15:30:00']]

    def test_pull3(self):
        yfinance_mock = unittest.mock.MagicMock()
        data = {'Open': [50.0, 52.0, 48.0],
                'High': [50.25,52.0,49.0],
                'Low': [48.0,49.0,47.0],
                'Close': [49.75,52.0,48.5],
                'Adj Close':[49.75,51.75,48.5],
                'Volume':[0,0,0]}

        data_date = pd.DataFrame(data, index=[pd.to_datetime('2022-12-25 09:30:00'),
                                        pd.to_datetime('2022-12-26 10:30:00'),
                                        pd.to_datetime('2022-12-27 15:30:00')])

        yfinance_mock.download.return_value = data_date
        with unittest.mock.patch('yfinance.download',yfinance_mock.download):
            result = get_stock_and_crypto_data("TESTTEST")
            assert result == []
if __name__ == 'main':
    unittest.main()
