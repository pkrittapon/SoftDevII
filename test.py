from data.function import Stock,Categories

import unittest
from unittest.mock import MagicMock,patch
import pandas as pd
import sqlite3

def get_stock_and_crypto_data(name):
    import yfinance as yf
    data = yf.download(tickers=name) #get data
    data = data.loc[data["Volume"] != 0 ].drop(["Adj Close"],axis = 1)# ไม่เอาค่า volume = 0
    data["Date"] = data.index.strftime('%Y-%m-%d %X') # convert pandas timestamp to string 
    return data.values.tolist() #return value in type list

def convert_interval(data,period):
    if period not in ["MS","QS"]:
         raise Exception("Interval ofset is not support. The support interval ofset are 'MS' and 'QS'")
    # Use the resample function to get the open price on the first day of the month
    new_open = data['open'].resample(period).first()

    # Use the resample function to get the close price on the last day of the month
    new_close = data['close'].resample(period).last()

    # Use the resample function to get the maximum and minimum values for each month
    new_high = data['high'].resample(period).max()
    new_low = data['low'].resample(period).min()

    # Use the resample function to get the total volume for each month
    new_volume = data['volume'].resample(period).sum()
    # Create a new DataFrame with the monthly stock prices
    new_prices = pd.DataFrame({'open': new_open,
                                    'high': new_high,
                                    'low': new_low,
                                    'close': new_close,                                
                                    'volume': new_volume
                                    })

    new_prices = new_prices.reset_index()
    return new_prices

def get_close_date(data,frequency):
    if frequency not in ["1d","1h"]:
         raise Exception("This frequency is not support. The support frequency are '1d' and '1h'")
    # grab first and last observations from df.date and make a continuous date range from that
    dt_all = pd.date_range(start=data['x'].iloc[0],end=data['x'].iloc[-1], freq = frequency)

    # check which dates from your source that also accur in the continuous date range
    dt_obs = [d.strftime("%Y-%m-%d %H:%M:%S") for d in data['x']]

    # isolate missing timestamps
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d %H:%M:%S").tolist() if not d in dt_obs]
    dt_breaks = pd.to_datetime(dt_breaks)
    return dt_breaks

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
        Datetime = [pd.to_datetime('2022-12-25 09:30:00'),
                                        pd.to_datetime('2022-12-26 10:30:00'),
                                        pd.to_datetime('2022-12-27 15:30:00')]
        data_date = pd.DataFrame(data, index=Datetime)

        yfinance_mock.download.return_value = data_date
        with unittest.mock.patch('yfinance.download',yfinance_mock.download):
            result = get_stock_and_crypto_data("TESTTEST")
            assert result == []


class test_convert_price_data(unittest.TestCase):
    def test_convert1(self):
        #               x              open high  low  close volume
        data = [('2022-12-01 10:00:00',50.0,50.25,48.0,49.75,100),
                ('2022-12-15 10:00:00',52.0,52.0,49.0,52.0,20),
                ('2022-12-30 10:00:00',48.0,49.0,47.0,48.5,3)]
        data_df = pd.DataFrame(data)# Convert to dataframe
        data_df = data_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})# Change column name
        data_df['x'] = pd.to_datetime(data_df['x'])# Convert type to pandas timestamp
        data_df.set_index('x', inplace=True)# Set the Date column as the index of the DataFrame

        result = convert_interval(data_df,"MS")
        assert result.equals(pd.DataFrame({'x':[pd.to_datetime('2022-12-01')],
                                            'open' : [50.0],
                                            'high' : [52.0],
                                            'low' : [47.0],
                                            'close' : [48.5],
                                            'volume' : [123]}))

    def test_convert2(self):
        #               x              open high  low  close volume
        data = [('2022-12-01 10:00:00',50.0,50.25,48.0,49.75,100),
                ('2022-12-15 10:00:00',52.0,52.0,49.0,52.0,20),
                ('2022-12-30 10:00:00',48.0,49.0,47.0,48.5,3),
                ('2023-01-03 10:00:00',12.0,52.0,12.0,45.0,30),
                ('2023-01-15 10:00:00',50.0,55.0,49.0,50.0,400),
                ('2023-01-28 10:00:00',44.0,50.0,20.0,25.0,5000)]
        data_df = pd.DataFrame(data)# Convert to dataframe
        data_df = data_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})# Change column name
        data_df['x'] = pd.to_datetime(data_df['x'])# Convert type to pandas timestamp
        data_df.set_index('x', inplace=True)# Set the Date column as the index of the DataFrame

        result = convert_interval(data_df,"MS")
        assert result.equals(pd.DataFrame({'x':[pd.to_datetime('2022-12-01'),pd.to_datetime('2023-01-01')],
                                            'open' : [50.0,12.0],
                                            'high' : [52.0,55.0],
                                            'low' : [47.0,12.0],
                                            'close' : [48.5,25.0],
                                            'volume' : [123,5430]}))

    def test_convert3(self):
        #               x              open high  low  close volume
        data = [('2022-12-01 10:00:00',50.0,50.25,48.0,49.75,100),
                ('2022-12-15 10:00:00',52.0,52.0,49.0,52.0,20),
                ('2022-12-30 10:00:00',48.0,49.0,47.0,48.5,3),
                ('2023-01-03 10:00:00',12.0,52.0,12.0,45.0,30),
                ('2023-01-15 10:00:00',50.0,55.0,49.0,50.0,400),
                ('2023-01-28 10:00:00',44.0,50.0,20.0,25.0,5000)]
        data_df = pd.DataFrame(data)# Convert to dataframe
        data_df = data_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})# Change column name
        data_df['x'] = pd.to_datetime(data_df['x'])# Convert type to pandas timestamp
        data_df.set_index('x', inplace=True)# Set the Date column as the index of the DataFrame

        result = convert_interval(data_df,"QS")
        assert result.equals(pd.DataFrame({'x':[pd.to_datetime('2022-10-01'),pd.to_datetime('2023-01-01')],
                                            'open' : [50.0,12.0],
                                            'high' : [52.0,55.0],
                                            'low' : [47.0,12.0],
                                            'close' : [48.5,25.0],
                                            'volume' : [123,5430]}))

    def test_convert4(self):
        data = [('2022-12-01 10:00:00',50.0,50.25,48.0,49.75,100),
                ('2022-12-15 10:00:00',52.0,52.0,49.0,52.0,20),
                ('2023-01-15 10:00:00',50.0,55.0,49.0,50.0,400),
                ('2023-01-28 10:00:00',44.0,50.0,20.0,25.0,5000)]
        data_df = pd.DataFrame(data)# Convert to dataframe
        data_df = data_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})# Change column name
        data_df['x'] = pd.to_datetime(data_df['x'])# Convert type to pandas timestamp
        data_df.set_index('x', inplace=True)# Set the Date column as the index of the DataFrame

        with self.assertRaises(Exception) as context :
            convert_interval(data_df,'test')
        self.assertEqual("Interval ofset is not support. The support interval ofset are 'MS' and 'QS'", str(context.exception))
            

class test_get_close_day(unittest.TestCase):
    def test_close_day1(self):
        #               x              open high low close volume
        data = [('2022-12-01 00:00:00',0,0,0,0,0),
                ('2022-12-05 00:00:00',0,0,0,0,0),
                ('2022-12-07 00:00:00',0,0,0,0,0)]
        data_df = pd.DataFrame(data)# Convert to dataframe
        data_df = data_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})# Change column name
        data_df['x'] = pd.to_datetime(data_df['x'])

        result = get_close_date(data_df,"1d")
        assert result.equals(pd.to_datetime(["2022-12-02","2022-12-03","2022-12-04","2022-12-06"]))

    def test_close_day2(self):
        #               x              open high low close volume
        data = [('2023-12-01 10:00:00',0,0,0,0,0),
                ('2023-12-01 11:00:00',0,0,0,0,0),
                ('2023-12-01 12:00:00',0,0,0,0,0),
                ('2023-12-01 14:00:00',0,0,0,0,0),
                ('2023-12-01 15:00:00',0,0,0,0,0),
                ('2023-12-01 16:00:00',0,0,0,0,0),
                ('2023-12-02 10:00:00',0,0,0,0,0)]
        data_df = pd.DataFrame(data)# Convert to dataframe
        data_df = data_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})# Change column name
        data_df['x'] = pd.to_datetime(data_df['x'])

        result = get_close_date(data_df,"1h")
        assert result.equals(pd.to_datetime(['2023-12-01 13:00:00','2023-12-01 17:00:00',
                                            '2023-12-01 18:00:00','2023-12-01 19:00:00',
                                            '2023-12-01 20:00:00','2023-12-01 21:00:00',
                                            '2023-12-01 22:00:00','2023-12-01 23:00:00',
                                            '2023-12-02 00:00:00','2023-12-02 01:00:00',
                                            '2023-12-02 02:00:00','2023-12-02 03:00:00',
                                            '2023-12-02 04:00:00','2023-12-02 05:00:00',
                                            '2023-12-02 06:00:00','2023-12-02 07:00:00',
                                            '2023-12-02 08:00:00','2023-12-02 09:00:00']))
    

    def test_close_day3(self):
        #               x              open high low close volume
        data = [('2022-12-01 00:00:00',0,0,0,0,0),
                ('2022-12-05 00:00:00',0,0,0,0,0),
                ('2022-12-07 00:00:00',0,0,0,0,0)]
        data_df = pd.DataFrame(data)# Convert to dataframe
        data_df = data_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})# Change column name
        data_df['x'] = pd.to_datetime(data_df['x'])

        with self.assertRaises(Exception) as context :
            get_close_date(data_df,"test")
        self.assertEqual("This frequency is not support. The support frequency are '1d' and '1h'", str(context.exception))


class TestCategories(unittest.TestCase):
    
    def test_get_all_stock(self):
        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('AOT',),('PTT',)] 

        result = Categories().get_all_stock()
        self.assertEqual(result, ['AOT','PTT'])
        mock_connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT symbol FROM stock")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_get_all_stock_empty(self):
        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [] 

        result = Categories().get_all_stock()
        self.assertEqual(result, [])
        mock_connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT symbol FROM stock")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_get_all_stock_OneStock(self):
        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('AOT',)] 

        result = Categories().get_all_stock()
        self.assertEqual(result, ['AOT'])
        mock_connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT symbol FROM stock")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_get_all_stock_in_sector(self):
        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('AOT',),('PTT',)] 

        result = Categories().get_all_stock_in_sector("AGRI")
        self.assertEqual(result, ['AOT','PTT'])
        mock_connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT symbol FROM stock WHERE sector = 'AGRI'")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()


class TestStock(unittest.TestCase):

    def test_get_stock_id(self):
        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)] 

        aot = Stock("AOT")
        result = aot.get_stock_id()
        self.assertEqual(result, 1)
        mock_connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT stock_id FROM stock WHERE symbol = 'AOT'")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_get_stock_price(self):
        Stock.get_stock_id = MagicMock(return_value=1)
        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(40.5,)] 

        aot = Stock("AOT")
        result = aot.get_stock_price()
        self.assertEqual(result, 40.5)
        mock_connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT close FROM price WHERE stockdata = 1 order by [datetime] desc limit 1")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()


class test_get_financial(unittest.TestCase):
    def test_financial1(self):
        data = {}
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
            assert result



if __name__ == 'main':
    unittest.main()