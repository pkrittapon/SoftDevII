from data.function import Stock,Categories
import unittest
from unittest.mock import MagicMock,call
import sqlite3


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
        Categories.get_sector_id = MagicMock(return_value=1)
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
        mock_cursor.execute.assert_called_once_with("SELECT symbol FROM stock WHERE sector_id = 1")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()


class TestStock(unittest.TestCase):

    def test_get_stock_id(self):
        Categories.get_all_stock = MagicMock(return_value = ["AOT","PTT","TRUE"])
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)] 

        aot = Stock("AOT")
        result = aot.get_stock_id()
        self.assertEqual(result, 1)
        sqlite3.connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT stock_id FROM stock WHERE symbol = 'AOT'")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_get_stock_price(self):
        Categories.get_all_stock = MagicMock(return_value = ["AOT","PTT","TRUE"])
        Stock.get_stock_id = MagicMock(return_value=1)
        Stock.table = MagicMock(return_value='stock_price_hour')
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(40.5,)] 

        aot = Stock("AOT")
        result = aot.get_stock_price(interval = '1h')
        self.assertEqual(result, 40.5)
        sqlite3.connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT close FROM stock_price_hour WHERE stock_id = 1 order by [datetime] desc limit 1")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_init(self):
        Categories.get_all_stock = MagicMock(return_value = ["AOT","PTT","TRUE"])
        with self.assertRaises(ValueError) as error:
            Stock("ABC")
        self.assertEqual(str(error.exception),"ABC is not available")
    
    def test_table(self):
        Categories.get_all_stock = MagicMock(return_value = ["AOT","PTT","TRUE"])
        aot = Stock("AOT")
        with self.assertRaises(ValueError) as error:
            aot.table("30m")
        self.assertEqual(str(error.exception),"The interval 30m is not available. The available interval are 1h,1d")
        self.assertEqual(aot.table("1d"),'stock_price_day')
        self.assertEqual(aot.table("1h"),'stock_price_hour')

    def test_get_all_datetime(self):
        Categories.get_all_stock = MagicMock(return_value = ["AOT","PTT","TRUE"])
        Stock.get_stock_id = MagicMock(return_value=1)
        Stock.table = MagicMock(return_value='stock_price_hour')
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("2022-11-16 10:00:00",),
                                             ("2022-11-16 11:00:00",),
                                             ("2022-11-16 12:00:00",),
                                             ("2022-11-16 14:00:00",),
                                             ("2022-11-16 15:00:00",),
                                             ("2022-11-16 16:00:00",)]
        aot = Stock("AOT")
        result = aot.get_all_datetime(interval = '1h')
        self.assertEqual(result, ["2022-11-16 10:00:00",
                                  "2022-11-16 11:00:00",
                                  "2022-11-16 12:00:00",
                                  "2022-11-16 14:00:00",
                                  "2022-11-16 15:00:00",
                                  "2022-11-16 16:00:00"])
        Stock.table.assert_called_once_with('1h')
        mock_cursor.execute.assert_called_once_with('SELECT [datetime] from stock_price_hour WHERE stock_id = 1')
    
    def test_insert_stock_price(self):
        Categories.get_all_stock = MagicMock(return_value = ["AOT","PTT","TRUE"])
        Stock.get_stock_id = MagicMock(return_value=1)
        Stock.get_all_datetime = MagicMock(return_value =  ["2022-11-16 10:00:00",
                                                            "2022-11-16 11:00:00",
                                                            "2022-11-16 12:00:00",
                                                            "2022-11-16 14:00:00",
                                                            "2022-11-16 15:00:00",
                                                            "2022-11-16 16:00:00"] )
        Stock.table = MagicMock(return_value='stock_price_hour')
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        data = [(75.25, 75.75, 75.25, 75.5, 2323369,'2022-11-16 10:00:00'),
                (75.25, 75.5, 75.0, 75.0, 3076771,'2022-11-16 11:00:00'),
                (75.0, 75.25, 75.0, 75.0, 253130,'2022-11-16 12:00:00'),
                (75.0, 75.25, 74.75, 74.75, 3464105,'2022-11-16 14:00:00'),
                (74.75, 75.0, 74.75, 74.75, 6457770,'2022-11-16 15:00:00'),
                (74.5, 74.75, 74.5, 74.5, 5966428,'2022-11-17 10:00:00'),
                (74.75, 74.75, 74.0, 74.0, 12216704,'2022-11-17 11:00:00'),
                (74.0, 74.25, 74.0, 74.25, 788348,'2022-11-17 12:00:00')]
        aot = Stock("AOT")
        result = aot.insert_stock(data=data,interval = '1h')
        self.assertEqual(result,None)
        self.assertEqual(mock_cursor.execute.call_count,3)
        mock_cursor.execute.assert_has_calls([call("INSERT INTO stock_price_hour VALUES (null,1,'2022-11-17 10:00:00',74.5,74.75,74.5,74.5,5966428)"), 
                                              call("INSERT INTO stock_price_hour VALUES (null,1,'2022-11-17 11:00:00',74.75,74.75,74.0,74.0,12216704)"),
                                              call("INSERT INTO stock_price_hour VALUES (null,1,'2022-11-17 12:00:00',74.0,74.25,74.0,74.25,788348)")])