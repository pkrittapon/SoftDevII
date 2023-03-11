from data.function import Stock,Categories,News,Location
import unittest
from unittest.mock import MagicMock,call
import sqlite3
import requests


class TestCategories(unittest.TestCase):
    
    def test_get_all_stock(self):
        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('AOT',),('PTT',)] 

        result = Categories("SET").get_all_stock()
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

        result = Categories("SET").get_all_stock()
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

        result = Categories("SET").get_all_stock()
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

        result = Categories("SET").get_all_stock_in_sector("AGRI")
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

        aot = Stock("AOT","SET")
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

        aot = Stock("AOT","SET")
        result = aot.get_stock_price(interval = '1h')
        self.assertEqual(result, 40.5)
        sqlite3.connect.assert_called_once_with('stock.db', timeout=10)
        mock_cursor.execute.assert_called_once_with("SELECT close FROM stock_price_hour WHERE stock_id = 1 order by [datetime] desc limit 1")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    
    def test_table(self):
        Categories.get_all_stock = MagicMock(return_value = ["AOT","PTT","TRUE"])
        aot = Stock("AOT","SET")
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
        aot = Stock("AOT","SET")
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
        aot = Stock("AOT","SET")
        result = aot.insert_stock(data=data,interval = '1h')
        self.assertEqual(result,None)
        self.assertEqual(mock_cursor.execute.call_count,3)
        mock_cursor.execute.assert_has_calls([call("INSERT INTO stock_price_hour VALUES (null,1,'2022-11-17 10:00:00',74.5,74.75,74.5,74.5,5966428)"), 
                                              call("INSERT INTO stock_price_hour VALUES (null,1,'2022-11-17 11:00:00',74.75,74.75,74.0,74.0,12216704)"),
                                              call("INSERT INTO stock_price_hour VALUES (null,1,'2022-11-17 12:00:00',74.0,74.25,74.0,74.25,788348)")])


class TestNews(unittest.TestCase):

    def test_yahoo_get_all_tag_normal(self):
        html = '<li class="js-stream-content Pos(r)">xxxxx</li><li class="abc">zzzzz</li><li class="js-stream-content Pos(r)">yyyyy</li>'

        mock_response = MagicMock()
        requests.get = MagicMock(return_value=mock_response)
        mock_response.text = html
        mock_response.status_code = 200

        news = News("NASDAQ")
        result = news.nasdaq_get_all_tags("APPL")
        result = [str(i) for i in result]

        self.assertEqual(result,['<li class="js-stream-content Pos(r)">xxxxx</li>','<li class="js-stream-content Pos(r)">yyyyy</li>'])


    def test_yahoo_get_all_tag_wrong(self):
        html = '<li class="aaa">xxxxx</li><li class="abc">zzzzz</li><li class="ccc">yyyyy</li>'

        mock_response = MagicMock()
        requests.get = MagicMock(return_value=mock_response)
        mock_response.text = html
        mock_response.status_code = 200

        news = News("NASDAQ")
        result = news.nasdaq_get_all_tags("APPL")

        self.assertEqual(result,[])

    def test_yahoo_get_all_tag_null(self):
        html = ''

        mock_response = MagicMock()
        requests.get = MagicMock(return_value=mock_response)
        mock_response.text = html
        mock_response.status_code = 200

        news = News("NASDAQ")
        result = news.nasdaq_get_all_tags("APPL")

        self.assertEqual(result,[])

    def test_yahoo_title_and_link_normal(self):
        html = '<li class="js-stream-content Pos(r)"><a href = "https://finance.yahoo.com">yahoo</a></li><li class="js-stream-content Pos(r)"><a href = "https://google.com">google</a></li>'
        
        mock_response = MagicMock()
        requests.get = MagicMock(return_value=mock_response)
        mock_response.text = html
        mock_response.status_code = 200

        news = News("NASDAQ")
        data = news.nasdaq_get_all_tags("APPL")
        result = news.nasdaq_title_link(data)

        self.assertEqual(result,[{'title': 'yahoo', 'link': 'https://finance.yahoo.com'}, {'title': 'google', 'link': 'https://google.com'}])

    def test_yahoo_title_and_link_null(self):

        news = News("NASDAQ")
        result = news.nasdaq_title_link([])

        self.assertEqual(result,[])

    def test_yahoo_content_time_normal(self):
        html = '<time datetime = "2022-10-10"></time><li class="caas-body"><p>Test</p><p>Test2</p><p>Test3</p></li>'
        mock_response = MagicMock()
        requests.get = MagicMock(return_value=mock_response)
        mock_response.text = html
        mock_response.status_code = 200

        news = News("NASDAQ")
        result = news.nasdaq_content_time('https://finance.yahoo.com')

        self.assertEqual(result,{'content': 'Test\nTest2\nTest3\n', 'datetime': '2022-10-10'})

    def test_yahoo_content_time_null(self):
        html = ''
        mock_response = MagicMock()
        requests.get = MagicMock(return_value=mock_response)
        mock_response.text = html
        mock_response.status_code = 200

        news = News("NASDAQ")
        result = news.nasdaq_content_time('https://finance.yahoo.com')

        self.assertEqual(result,{'content': 'null', 'datetime': 'null'})


    def test_insert_news(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        news = News("NASDAQ")
        news.insert_news({'title':'yahoo','datetime':'2020-10-10','link':'https://finance.yahoo.com','content':'TestYahoo12345'})

        mock_cursor.execute.assert_called_once_with('INSERT INTO nasdaq_news VALUES (null,?,?,?,?)', ('yahoo', '2020-10-10', 'https://finance.yahoo.com', 'TestYahoo12345'))


class TestLocation(unittest.TestCase):
    def test_noun(self):
        string = "I lived in Bangkok for 10 years"
        result = Location('set').noun(string)
        self.assertEqual(result,['I','Bangkok','10 years'])

    def test_noun_one_word(self):
        string = "years"
        result = Location('set').noun(string)
        self.assertEqual(result,['years'])

    def test_noun_empty(self):
        string = ""
        result = Location('set').noun(string)
        self.assertEqual(result,[])

    def test_location_one_location(self):
        string = "I lived in Bangkok for 10 years"
        result = Location('set').location(string)
        self.assertEqual(result,['Bangkok'])

    def test_location_two_location(self):
        string = "I went to Bangkok after that I went to Paris"
        result = Location('set').location(string)
        
        self.assertEqual(set(result),set(['Paris','Bangkok']))

    def test_location_no_location(self):
        string = "I am talking"
        result = Location('set').location(string)
        self.assertEqual(result,[])

    def test_extract_lat_lon(self):
        mock_response = MagicMock()
        requests.get = MagicMock(return_value = mock_response)
        mock_response.json.return_value = [{'name':'Bangkok','lat':12.6,'lon':10.1},{'name':'Bang','lat':1,'lon':2},{'lat':3,'lon':1}]
        result = Location('set').extract_lat_lon("Bangkok")
        self.assertEqual(result,{'lat':12.6,'lon':10.1})
        requests.get.assert_called_once_with('https://nominatim.openstreetmap.org/search.php?q=Bangkok&format=jsonv2')

    def test_extract_lat_lon_none(self):
        mock_response = MagicMock()
        requests.get = MagicMock(return_value = mock_response)
        mock_response.json.return_value = []
        result = Location('set').extract_lat_lon("Nonthaburi")
        self.assertEqual(result,None)
        requests.get.assert_called_once_with('https://nominatim.openstreetmap.org/search.php?q=Nonthaburi&format=jsonv2')
