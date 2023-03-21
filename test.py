from data.function import Stock,Categories,News,Location
import unittest
from unittest.mock import MagicMock,call,patch
import sqlite3
import requests
from googletrans import Translator
import spacy
import pandas as pd


class TestGetIndexID(unittest.TestCase):
    def setUp(self):
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE [index] (
                index_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        cursor.execute("INSERT INTO [index] (symbol) VALUES ('DOWN JONES')")
        cursor.execute("INSERT INTO [index] (symbol) VALUES ('NASDAQ')")
        cursor.execute("INSERT INTO [index] (symbol) VALUES ('SET')")
        self.conn.commit()

        self.original_connect = sqlite3.connect

        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = self.conn

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        sqlite3.connect = self.original_connect

    def test_valid_symbol(self):
        """Test get_index_id with a valid symbol"""
        index = Categories("NASDAQ")
        result = index.get_index_id()
        self.assertEqual(result, 2)

    def test_invalid_symbol(self):
        """Test get_index_id with a symbol that has no index_id"""
        index = Categories("S&P500")
        result = index.get_index_id()
        self.assertEqual(result, 'null')

    def test_case_insensitivity(self):
        index = Categories("set")
        result = index.get_index_id()
        self.assertEqual(result, 3)    

class TestGetIndustryID(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE industry (
                industry_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        cursor.execute("INSERT INTO industry (symbol) VALUES ('AGRO')")
        cursor.execute("INSERT INTO industry (symbol) VALUES ('CONSUMP')")
        cursor.execute("INSERT INTO industry (symbol) VALUES ('FINCIAL')")
        self.conn.commit()

        self.original_connect = sqlite3.connect

        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = self.conn

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        sqlite3.connect = self.original_connect

    def test_existing_symbol(self):
        industry = Categories("SET")
        result = industry.get_industry_id('AGRO')
        self.assertEqual(result, 1)

    def test_nonexistent_symbol(self):
        industry = Categories("SET")
        result = industry.get_industry_id('TECH')
        self.assertEqual(result, 'null')

class TestGetSectorID(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE sector (
                sector_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        cursor.execute("INSERT INTO sector (symbol) VALUES ('AGRI')")
        cursor.execute("INSERT INTO sector (symbol) VALUES ('FOOD')")
        cursor.execute("INSERT INTO sector (symbol) VALUES ('HOME')")
        self.conn.commit()

        self.original_connect = sqlite3.connect

        mock_connect = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = self.conn

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        sqlite3.connect = self.original_connect

    def test_existing_symbol(self):
        sector = Categories("SET")
        result = sector.get_sector_id('AGRI')
        self.assertEqual(result, 1)

    def test_nonexistent_symbol(self):
        sector = Categories("SET")
        result = sector.get_sector_id('STEEL')
        self.assertEqual(result, 'null')

class TestInsertStock(unittest.TestCase):
    def setUp(self):
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT,
                index_id INTEGER,
                industry_id INTEGER,
                sector_id INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE [crypto] (
                crypto_id	INTEGER PRIMARY KEY,
                symbol	TEXT
        )""")
        self.conn.commit()
        self.original_connect = sqlite3.connect
        self.original_get_index_id = Categories.get_index_id
        self.original_get_industry_id = Categories.get_industry_id
        self.original_get_sector_id = Categories.get_sector_id

        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

        Categories.get_index_id = MagicMock(return_value = 1)
        Categories.get_industry_id = MagicMock(return_value = 2)
        Categories.get_sector_id = MagicMock(return_value = 3)

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        sqlite3.connect = self.original_connect
        Categories.get_index_id = self.original_get_index_id
        Categories.get_sector_id = self.original_get_sector_id
        Categories.get_industry_id = self.original_get_industry_id

    def test_insert_stock(self):
        obj = Categories('SET')
        obj.insert_stock('PTT', industry='AGRO', sector='AGRI')

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM stock")
        row = cursor.fetchone()

        self.assertEqual(row[0], 1) # stock_id
        self.assertEqual(row[1], 'PTT')
        self.assertEqual(row[2], 1)  # index_id 
        self.assertEqual(row[3], 2)  # industry_id 
        self.assertEqual(row[4], 3)  # sector_id 

    def test_insert_crypto(self):
        obj = Categories('CRYPTO')
        obj.insert_stock('BTC')

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM crypto")
        row = cursor.fetchone()

        self.assertEqual(row[0], 1) # crypto_id
        self.assertEqual(row[1], 'BTC')

class TestGetAllStock(unittest.TestCase):
    def setUp(self):
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        sqlite3.connect = self.original_connect

    def test_have_stocks(self):
        expected_result = ['PTT', 'AOT', 'SCB']
        mock_data = [(symbol,) for symbol in expected_result] 
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_stock()
        self.assertEqual(result,expected_result)

    def test_have_one_stock(self):
        expected_result = ['PTT']
        mock_data = [(symbol,) for symbol in expected_result] 
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_stock()
        self.assertEqual(result,expected_result)

    def test_have_none_stock(self):
        expected_result = []
        mock_data = [(symbol,) for symbol in expected_result] 
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_stock()
        self.assertEqual(result,expected_result)

class TestTopStock(unittest.TestCase):
    def setUp(self):
        """Create a new in-memory SQLite database and insert some data"""
        self.stock = ['PTT', 'AOT', 'SCB', 'TOA', 'OR']
        mock_stock_data = [(symbol,) for symbol in self.stock] 
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE [set100] (
                stock_id INTEGER
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", mock_stock_data)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        sqlite3.connect = self.original_connect

    def test_have_top_stock(self):
        top_stock = ['SCB','PTT']
        mock_top_stock_data = [(self.stock.index(symbol)+1,) for symbol in top_stock] 
        self.cursor.executemany("INSERT INTO set100 VALUES (?)", mock_top_stock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_top_stock()
        self.assertEqual(result,top_stock)

    def test_have_one_top_stock(self):
        top_stock = ['SCB']
        mock_top_stock_data = [(self.stock.index(symbol)+1,) for symbol in top_stock] 
        self.cursor.executemany("INSERT INTO set100 VALUES (?)", mock_top_stock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_top_stock()
        self.assertEqual(result,top_stock)

    def test_have_none_top_stock(self):
        top_stock = []
        mock_top_stock_data = [(self.stock.index(symbol)+1,) for symbol in top_stock] 
        self.cursor.executemany("INSERT INTO set100 VALUES (?)", mock_top_stock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_top_stock()
        self.assertEqual(result,top_stock)

class TestGetAllIndex(unittest.TestCase):
    def setUp(self):
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [index] (
                index_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        sqlite3.connect = self.original_connect

    def test_have_index(self):
        index = ['SET','NASDAQ']
        mock_index = [(symbol,) for symbol in index] 
        self.cursor.executemany("INSERT INTO [index] (symbol) VALUES (?)", mock_index)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_index()
        self.assertEqual(result,index)

    def test_have_one_index(self):
        index = ['SET']
        mock_index = [(symbol,) for symbol in index] 
        self.cursor.executemany("INSERT INTO [index] (symbol) VALUES (?)", mock_index)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_index()
        self.assertEqual(result,index)

    def test_have_none_index(self):
        index = []
        mock_index = [(symbol,) for symbol in index] 
        self.cursor.executemany("INSERT INTO [index] (symbol) VALUES (?)", mock_index)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_index()
        self.assertEqual(result,index)

class TestGetAllIndustry(unittest.TestCase):
    def setUp(self):
        self.industry = ['RESOURC','SERVICE','FINCIAL','TECH']
        mock_data = [(symbol,) for symbol in self.industry]
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT,
                industry_id INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE [industry] (
                industry_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.executemany("INSERT INTO industry (symbol) VALUES (?)", mock_data)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.industry = None
        sqlite3.connect = self.original_connect

    def test_have_stock_in_industry(self):
        stock = [('PTT','RESOURC'), ('AOT','SERVICE'), ('SCB','FINCIAL'), ('TOA','RESOURC'), ('DELTA','TECH')]
        mock_data = [(symbol[0],self.industry.index(symbol[1])+1) for symbol in stock] 
        self.cursor.executemany("INSERT INTO stock (symbol,industry_id) VALUES (?,?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_industry()
        self.assertEqual(result,self.industry)
    
    def test_have_one_stock_in_industry(self):
        stock = [('DELTA','TECH')]
        mock_data = [(symbol[0],self.industry.index(symbol[1])+1) for symbol in stock] 
        self.cursor.executemany("INSERT INTO stock (symbol,industry_id) VALUES (?,?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_industry()
        self.assertEqual(result,['TECH'])

    def test_have_none_stock_in_industry(self):
        stock = []
        mock_data = [(symbol,) for symbol in stock] 
        self.cursor.executemany("INSERT INTO stock (symbol,industry_id) VALUES (?,?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_industry()
        self.assertEqual(result,stock)

class TestGetAllSector(unittest.TestCase):
    def setUp(self):
        self.sector = ['RESOURC','SERVICE','FINCIAL','TECH']
        mock_data = [(symbol,) for symbol in self.sector]
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT,
                sector_id INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE [sector] (
                sector_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.executemany("INSERT INTO sector (symbol) VALUES (?)", mock_data)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.sector = None
        sqlite3.connect = self.original_connect

    def test_have_stock_in_sector(self):
        stock = [('PTT','RESOURC'), ('AOT','SERVICE'), ('SCB','FINCIAL'), ('TOA','RESOURC'), ('DELTA','TECH')]
        mock_data = [(symbol[0],self.sector.index(symbol[1])+1) for symbol in stock] 
        self.cursor.executemany("INSERT INTO stock (symbol,sector_id) VALUES (?,?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_sector()
        self.assertEqual(result,self.sector)
    
    def test_have_one_stock_in_industry(self):
        stock = [('DELTA','TECH')]
        mock_data = [(symbol[0],self.sector.index(symbol[1])+1) for symbol in stock] 
        self.cursor.executemany("INSERT INTO stock (symbol,sector_id) VALUES (?,?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_sector()
        self.assertEqual(result,['TECH'])

    def test_have_none_stock_in_industry(self):
        stock = []
        mock_data = [(symbol,) for symbol in stock] 
        self.cursor.executemany("INSERT INTO stock (symbol,sector_id) VALUES (?,?)", mock_data)
        self.conn.commit()
        obj = Categories('SET')
        result = obj.get_all_sector()
        self.assertEqual(result,stock)

class TestGetAllSectorInIndustry(unittest.TestCase):
    def setUp(self):
        self.industry = ['AGRO','SERVICE']
        self.sector = [('AGRI','AGRO'), ('FOOD','AGRO'), ('COMM','SERVICE'), ('HELTH','SERVICE'), ('TRANS','SERVICE')]
        mock_industry = [(symbol,) for symbol in self.industry]
        mock_sector = [(symbol[0],self.industry.index(symbol[1])+1) for symbol in self.sector]
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [industry] (
                industry_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE [sector] (
                sector_id INTEGER PRIMARY KEY,
                symbol TEXT,
                industry_id INTEGER
            )
        """)
        self.cursor.executemany("INSERT INTO industry (symbol) VALUES (?)", mock_industry)
        self.cursor.executemany("INSERT INTO sector (symbol,industry_id) VALUES (?,?)", mock_sector)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.industry = None
        self.sector = None
        sqlite3.connect = self.original_connect

    def test_valid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_sector_in_industrial('AGRO')
        self.assertEqual(result,['AGRI','FOOD'])
    
    def test_invalid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_sector_in_industrial('INDUS')
        self.assertEqual(result,[])

class TestGetAllStockInIndustry(unittest.TestCase):
    def setUp(self):
        self.industry = ['AGRO','SERVICE']
        self.stock = [('EE','AGRO'), ('GFPT','AGRO'), ('COM7','SERVICE'), ('CPALL','SERVICE'), ('HMPRO','SERVICE')]
        mock_industry = [(symbol,) for symbol in self.industry]
        mock_stock = [(symbol[0],self.industry.index(symbol[1])+1) for symbol in self.stock]
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [industry] (
                industry_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT,
                industry_id INTEGER
            )
        """)
        self.cursor.executemany("INSERT INTO industry (symbol) VALUES (?)", mock_industry)
        self.cursor.executemany("INSERT INTO stock (symbol,industry_id) VALUES (?,?)", mock_stock)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        self.industry = None
        sqlite3.connect = self.original_connect

    def test_valid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_industrial('AGRO')
        self.assertEqual(result,['EE','GFPT'])
    
    def test_invalid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_industrial('INDUS')
        self.assertEqual(result,[])

class TestGetAllStockInSector(unittest.TestCase):
    def setUp(self):
        self.sector = ['AGRI','COMM']
        self.stock = [('EE','AGRI'), ('GFPT','AGRI'), ('COM7','COMM'), ('CPALL','COMM'), ('HMPRO','COMM')]
        mock_sector = [(symbol,) for symbol in self.sector]
        mock_stock = [(symbol[0],self.sector.index(symbol[1])+1) for symbol in self.stock]
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [sector] (
                sector_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT,
                sector_id INTEGER
            )
        """)
        self.cursor.executemany("INSERT INTO sector (symbol) VALUES (?)", mock_sector)
        self.cursor.executemany("INSERT INTO stock (symbol,sector_id) VALUES (?,?)", mock_stock)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.sector = None
        self.stock = None
        sqlite3.connect = self.original_connect

    def test_valid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_sector('AGRI')
        self.assertEqual(result,['EE','GFPT'])
    
    def test_invalid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_sector('FOOD')
        self.assertEqual(result,[])

class TestInsertNewStock(unittest.TestCase):
    def setUp(self):
        self.original_get_all_stock = Categories.get_all_stock
        self.original_get_stock_and_crypto_data = Categories.get_stock_and_crypto_data
        self.original_insert_stock = Categories.insert_stock
    
    def tearDown(self):
        Categories.get_all_stock = self.original_get_all_stock
        Categories.get_stock_and_crypto_data = self.original_get_stock_and_crypto_data
        Categories.insert_stock = self.original_insert_stock

    def test_have_stock_in_db(self):
        Categories.get_all_stock = MagicMock(return_value = ['PTT','AOT'])
        Categories.get_stock_and_crypto_data = MagicMock()
        Categories.insert_stock = MagicMock()
        result = Categories('SET').insert_new_stock('PTT')
        self.assertEqual(result,'have')
        Categories.get_all_stock.assert_called_once()
        Categories.get_stock_and_crypto_data.assert_not_called()
        Categories.insert_stock.assert_not_called()

    def test_do_not_have_stock_in_db_and_no_stock_in_market(self):
        Categories.get_all_stock = MagicMock(return_value = ['PTT','AOT'])
        Categories.get_stock_and_crypto_data = MagicMock(return_value = None)
        Categories.insert_stock = MagicMock()
        result = Categories('SET').insert_new_stock('ABCD')
        self.assertEqual(result,'fail')
        Categories.get_all_stock.assert_called_once()
        Categories.get_stock_and_crypto_data.assert_called_once()
        Categories.insert_stock.assert_not_called()

    def test_new_stock(self):
        Categories.get_all_stock = MagicMock(return_value = ['PTT','AOT'])
        Categories.get_stock_and_crypto_data = MagicMock(return_value = [20,20,20,20])
        Categories.insert_stock = MagicMock()
        result = Categories('SET').insert_new_stock('SCG')
        self.assertEqual(result,'pass')
        Categories.get_all_stock.assert_called_once()
        Categories.get_stock_and_crypto_data.assert_called_once()
        Categories.insert_stock.assert_called_once()




class TestGetStockID(unittest.TestCase):
    def setUp(self):
        self.stock = ['EE','GFPT','COM7','CPALL','HMPRO']
        mock_stock = [(symbol,) for symbol in self.stock]
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", mock_stock)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        sqlite3.connect = self.original_connect
        

    def test_valid_data(self):
        stock = Stock('COM7','SET')
        result = stock.get_stock_id()
        self.assertEqual(result,3)

    def test_invalid_data(self):
        stock = Stock('PTT','SET')
        result = stock.get_stock_id()
        self.assertEqual(result,[])
       
class TestGetStockName(unittest.TestCase):
    def setUp(self):
        self.stock = [('EE','ETERNAL ENERGY PUBLIC COMPANY LIMITED'), ('COM7','COM7 PUBLIC COMPANY LIMITED'), ('HMPRO','HOME PRODUCT CENTER PUBLIC COMPANY LIMITED')]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT,
                about TEXT
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol,about) VALUES (?,?)", self.stock)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.stock = None
        self.conn = None
        self.cursor = None
        sqlite3.connect = self.original_connect

    def test_valid_data(self):
        stock = Stock('HMPRO','SET')
        result = stock.get_stock_name()
        self.assertEqual(result,'HOME PRODUCT CENTER PUBLIC COMPANY LIMITED')

    def test_invalid_data(self):
        stock = Stock('PTT','SET')
        result = stock.get_stock_name()
        self.assertEqual(result,[])

class TestDelete(unittest.TestCase):
    def setUp(self):
        self.stock = ['EE','GFPT','COM7','CPALL','HMPRO']
        mock_stock = [(symbol,) for symbol in self.stock]
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", mock_stock)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.stock = None
        self.conn = None
        self.cursor = None
        sqlite3.connect = self.original_connect

    def test_valid_data(self):
        stock = Stock('COM7','SET')
        stock.delete()
        self.cursor.execute("SELECT symbol FROM stock")
        result = self.cursor.fetchall()
        result = [i[0] for i in result]
        self.assertEqual(result,['EE','GFPT','CPALL','HMPRO'])

    def test_invalid_data(self):
        stock = Stock('PTT','SET')
        stock.delete()
        self.cursor.execute("SELECT symbol FROM stock")
        result = self.cursor.fetchall()
        result = [i[0] for i in result]
        self.assertEqual(result, ['EE','GFPT','COM7','CPALL','HMPRO'])
       
class TestTable(unittest.TestCase):
    def test_table(self):
        stock = Stock("AOT","SET")
        with self.assertRaises(ValueError) as error:
            stock.table("30m")
        self.assertEqual(str(error.exception),"The interval 30m is not available. The available interval are 1h,1d")
        self.assertEqual(stock.table("1d"),'stock_price_day')
        self.assertEqual(stock.table("1h"),'stock_price_hour')

class TestGetNasdaqCryptoAmount(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_get_amount(self):
        self.mock_cursor.fetchone.return_value = (10000,)
        stock = Stock('AAPL','NASDAQ')
        result = stock.get_nasdaq_crypto_amount()
        self.assertEqual(result,10000)
        self.mock_cursor.execute.assert_called_once_with("SELECT amount FROM stock_nasdaq WHERE symbol = 'AAPL'")

    def test_none(self):
        stock = Stock('PTT','SET')
        result = stock.get_nasdaq_crypto_amount()
        self.assertEqual(result,None)

class TestGetStockPrice(unittest.TestCase):
    def setUp(self):
        self.stock = [('EE',)]
        self.price_day = [(1,'2022-10-2 00:00:00',10.5), (1,'2022-10-3 00:00:00',12.8), (1,'2022-10-4 00:00:00',13.7)]
        self.price_hour = [(1,'2022-10-4 10:00:00',10.5), (1,'2022-10-4 11:00:00',12.8), (1,'2022-10-4 12:00:00',20.2)]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_day (
                stock_id INTEGER,
                [datetime] TEXT,
                close REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_hour (
                stock_id INTEGER,
                [datetime] TEXT,
                close REAL
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", self.stock)
        self.cursor.executemany("INSERT INTO stock_price_day VALUES (?,?,?)", self.price_day)
        self.cursor.executemany("INSERT INTO stock_price_hour VALUES (?,?,?)", self.price_hour)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        self.price_day = None
        self.price_hour = None
        sqlite3.connect = self.original_connect
        
    def test_data_price_day(self):
        stock = Stock('EE','SET')
        result = stock.get_stock_price(interval = '1d')
        self.assertEqual(result,13.7)

    def test_data_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.get_stock_price(interval = '1h')
        self.assertEqual(result,20.2)

    def test_no_data(self):
        stock = Stock('PTT','SET')
        result = stock.get_stock_price(interval = '1h')
        self.assertEqual(result,[])

class TestGetPercentChange(unittest.TestCase):
    def setUp(self):
        self.stock = [('EE',)]
        self.price_day = [(1,'2022-10-2 00:00:00',10.5), (1,'2022-10-3 00:00:00',24), (1,'2022-10-4 00:00:00',12)]
        self.price_hour = [(1,'2022-10-4 10:00:00',10.5), (1,'2022-10-4 11:00:00',12), (1,'2022-10-4 12:00:00',24)]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_day (
                stock_id INTEGER,
                [datetime] TEXT,
                close REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_hour (
                stock_id INTEGER,
                [datetime] TEXT,
                close REAL
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", self.stock)
        self.cursor.executemany("INSERT INTO stock_price_day VALUES (?,?,?)", self.price_day)
        self.cursor.executemany("INSERT INTO stock_price_hour VALUES (?,?,?)", self.price_hour)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        self.price_day = None
        self.price_hour = None
        sqlite3.connect = self.original_connect
        
    def test_data_price_day(self):
        stock = Stock('EE','SET')
        result = stock.get_percent_change(interval = '1d')
        self.assertEqual(result,-50)

    def test_data_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.get_percent_change(interval = '1h')
        self.assertEqual(result,100)

    def test_no_data(self):
        stock = Stock('PTT','SET')
        result = stock.get_percent_change(interval = '1h')
        self.assertEqual(result,[])

class TestGetLatestAndOldestUpdateTime(unittest.TestCase):
    def setUp(self):
        self.stock = [('EE',)]
        self.price_day = [(1,'2022-10-2 00:00:00',10.5), (1,'2022-10-3 00:00:00',24), (1,'2022-10-4 00:00:00',12)]
        self.price_hour = [(1,'2022-10-4 10:00:00',10.5), (1,'2022-10-4 11:00:00',12), (1,'2022-10-4 12:00:00',24)]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_day (
                stock_id INTEGER,
                [datetime] TEXT,
                close REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_hour (
                stock_id INTEGER,
                [datetime] TEXT,
                close REAL
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", self.stock)
        self.cursor.executemany("INSERT INTO stock_price_day VALUES (?,?,?)", self.price_day)
        self.cursor.executemany("INSERT INTO stock_price_hour VALUES (?,?,?)", self.price_hour)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        self.price_day = None
        self.price_hour = None
        sqlite3.connect = self.original_connect
        
    def test_latest_price_day(self):
        stock = Stock('EE','SET')
        result = stock.latest_update_time(interval = '1d')
        self.assertEqual(result,'2022-10-4 00:00:00')

    def test_latest_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.latest_update_time(interval = '1h')
        self.assertEqual(result,'2022-10-4 12:00:00')

    def test_oldest_price_day(self):
        stock = Stock('EE','SET')
        result = stock.oldest_update_time(interval = '1d')
        self.assertEqual(result,'2022-10-2 00:00:00')

    def test_oldest_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.oldest_update_time(interval = '1h')
        self.assertEqual(result,'2022-10-4 10:00:00')

    def test_no_data(self):
        stock = Stock('PTT','SET')
        result = stock.oldest_update_time(interval = '1h')
        self.assertEqual(result,[])

class TestGetAllDatetime(unittest.TestCase):
    def setUp(self):
        self.stock = [('EE',)]
        self.price_day = [(1,'2022-10-2 00:00:00',10.5), (1,'2022-10-3 00:00:00',24), (1,'2022-10-4 00:00:00',12)]
        self.price_hour = [(1,'2022-10-4 10:00:00',10.5), (1,'2022-10-4 11:00:00',12), (1,'2022-10-4 12:00:00',24)]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_day (
                stock_id INTEGER,
                [datetime] TEXT,
                close REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_hour (
                stock_id INTEGER,
                [datetime] TEXT,
                close REAL
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", self.stock)
        self.cursor.executemany("INSERT INTO stock_price_day VALUES (?,?,?)", self.price_day)
        self.cursor.executemany("INSERT INTO stock_price_hour VALUES (?,?,?)", self.price_hour)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        self.price_day = None
        self.price_hour = None
        sqlite3.connect = self.original_connect
        
    def test_price_day(self):
        stock = Stock('EE','SET')
        result = stock.get_all_datetime(interval = '1d')
        self.assertEqual(result,['2022-10-2 00:00:00','2022-10-3 00:00:00','2022-10-4 00:00:00'])

    def test_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.get_all_datetime(interval = '1h')
        self.assertEqual(result,['2022-10-4 10:00:00','2022-10-4 11:00:00','2022-10-4 12:00:00'])
    
    def test_no_data(self):
        stock = Stock('PTT','SET')
        result = stock.get_all_datetime(interval = '1h')
        self.assertEqual(result,[])

class TestGetAllStockPrice(unittest.TestCase):
    def setUp(self):
        self.stock = [('EE',)]
        self.price_day = [(1,'2022-10-2 00:00:00',10,11,12,13,1000), (1,'2022-10-3 00:00:00',10,11,12,13,2000), (1,'2022-10-4 00:00:00',10,11,12,13,3000)]
        self.price_hour = [(1,'2022-10-4 10:00:00',5,6,7,8,100), (1,'2022-10-4 11:00:00',5,6,7,8,200), (1,'2022-10-4 12:00:00',5,6,7,8,300)]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_day (
                stock_id INTEGER,
                [datetime] TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_hour (
                stock_id INTEGER,
                [datetime] TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INT
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", self.stock)
        self.cursor.executemany("INSERT INTO stock_price_day VALUES (?,?,?,?,?,?,?)", self.price_day)
        self.cursor.executemany("INSERT INTO stock_price_hour VALUES (?,?,?,?,?,?,?)", self.price_hour)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        self.price_day = None
        self.price_hour = None
        sqlite3.connect = self.original_connect
        
    def test_data_price_day(self):
        stock = Stock('EE','SET')
        result = stock.get_all_stock_price(interval = '1d')
        self.assertEqual(result,[('2022-10-2 00:00:00',10,11,12,13,1000), ('2022-10-3 00:00:00',10,11,12,13,2000), ('2022-10-4 00:00:00',10,11,12,13,3000)])

    def test_data_price_day_with_start(self):
        stock = Stock('EE','SET')
        result = stock.get_all_stock_price(interval = '1d',start = '2022-10-3 00:00:00')
        self.assertEqual(result,[('2022-10-3 00:00:00',10,11,12,13,2000), ('2022-10-4 00:00:00',10,11,12,13,3000)])

    def test_data_price_day_with_end(self):
        stock = Stock('EE','SET')
        result = stock.get_all_stock_price(interval = '1d',end = '2022-10-3 00:00:00')
        self.assertEqual(result,[('2022-10-2 00:00:00',10,11,12,13,1000), ('2022-10-3 00:00:00',10,11,12,13,2000)])

    def test_data_price_day_with_start_and_end(self):
        stock = Stock('EE','SET')
        result = stock.get_all_stock_price(interval = '1d',start = '2022-10-3 00:00:00',end = '2022-10-3 00:00:00')
        self.assertEqual(result,[('2022-10-3 00:00:00',10,11,12,13,2000)])

    def test_data_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.get_all_stock_price(interval = '1h')
        self.assertEqual(result,[('2022-10-4 10:00:00',5,6,7,8,100), ('2022-10-4 11:00:00',5,6,7,8,200), ('2022-10-4 12:00:00',5,6,7,8,300)])

    def test_no_data(self):
        stock = Stock('PTT','SET')
        result = stock.get_all_stock_price(interval = '1h')
        self.assertEqual(result,[])

class TestSectorAndIndustry(unittest.TestCase):
    def setUp(self):
        self.industry = ['AGRO','SERVICE']
        self.sector = ['AGRI','COMM']
        self.stock = [('EE','AGRO','AGRI'), ('GFPT','AGRO','AGRI'), ('COM7','SERVICE','COMM'), ('CPALL','SERVICE','COMM'), ('HMPRO','SERVICE','COMM')]
        mock_industry = [(symbol,) for symbol in self.industry]
        mock_sector = [(symbol,) for symbol in self.sector]
        mock_stock = [(symbol[0],self.industry.index(symbol[1])+1,self.sector.index(symbol[2])+1) for symbol in self.stock]
        """Create a new in-memory SQLite database and insert some data"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [industry] (
                industry_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE [sector] (
                sector_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT,
                industry_id INTEGER,
                sector_id INTEGER
            )
        """)
        self.cursor.executemany("INSERT INTO industry (symbol) VALUES (?)", mock_industry)
        self.cursor.executemany("INSERT INTO sector (symbol) VALUES (?)", mock_sector)
        self.cursor.executemany("INSERT INTO stock (symbol,industry_id,sector_id) VALUES (?,?,?)", mock_stock)
        self.conn.commit()

        self.original_connect = sqlite3.connect
        
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.industry = None
        self.sector = None
        self.stock = None
        sqlite3.connect = self.original_connect

    def test_industry_valid_symbol(self):
        stock = Stock('COM7','SET')
        result = stock.industry()
        self.assertEqual(result,'SERVICE')
    
    def test_industry_invalid_symbol(self):
        stock = Stock('PTT','SET')
        result = stock.industry()
        self.assertEqual(result,[])

    def test_sector_valid_symbol(self):
        stock = Stock('EE','SET')
        result = stock.sector()
        self.assertEqual(result,'AGRI')
    
    def test_sector_invalid_symbol(self):
        stock = Stock('PTT','SET')
        result = stock.sector()
        self.assertEqual(result,[])

class TestInsertFin(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE "set_financial_statement" (
                "financial_id"	INTEGER PRIMARY KEY,
                "stock_id"	INTEGER,
                "quarter"	TEXT,
                "total_asset"	REAL,
                "liabilities"	REAL,
                "equity"	REAL,
                "paid_up_capital"	REAL,
                "revenue"	REAL,
                "net_profit"	REAL,
                "EPS"	REAL,
                "ROA"	REAL,
                "ROE"	REAL,
                "net_profit_margin"	REAL,
                "market_capitalization"	REAL,
                "P/E"	REAL,
                "P/BV"	REAL,
                "dividend_yield"	REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE "nasdaq_financial_statement" (
                "financial_id"	INTEGER PRIMARY KEY,
                "stock_id"	INTEGER,
                "quarter"	TEXT,
                "total_asset"	REAL,
                "liabilities"	REAL,
                "equity"	REAL,
                "paid_up_capital"	REAL,
                "revenue"	REAL,
                "net_profit"	REAL
            )
        """)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        sqlite3.connect = self.original_connect
        
    def test_insert_set(self):
        stock = Stock('EE','SET')
        stock.insert_set_fin(1,['2556Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02,12.64,2.61,5.8,6.12,931153.68,8.9,1.54,3.99])
        self.cursor.execute("SELECT * FROM set_financial_statement")
        result = self.cursor.fetchone()
        self.assertEqual(result,(1,1,'2556Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02,12.64,2.61,5.8,6.12,931153.68,8.9,1.54,3.99))

    def test_insert_nasdaq(self):
        stock = Stock('AAPL','NASDAQ')
        stock.insert_nasdaq_fin(1,['2556Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02])
        self.cursor.execute("SELECT * FROM nasdaq_financial_statement")
        result = self.cursor.fetchone()
        self.assertEqual(result,(1,1,'2556Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02))
  
class TestGetQuarterFin(unittest.TestCase):
    def setUp(self):
        self.quarter = ['2560Q1','2560Q2','2560Q3','2560Q4']
        mock_quarter = [(1,symbol) for symbol in self.quarter]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE "stock" (
                "stock_id"	INTEGER PRIMARY KEY,
                "symbol"	TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE "set_financial_statement" (
                "financial_id"	INTEGER PRIMARY KEY,
                "stock_id"	INTEGER,
                "quarter"	TEXT
            )
        """)
        self.cursor.execute("INSERT INTO stock (symbol) VALUES ('EE')")
        self.cursor.executemany("INSERT INTO set_financial_statement (stock_id,quarter) VALUES (?,?)", mock_quarter)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.quarter = None
        sqlite3.connect = self.original_connect
        
    def test_get_quarter(self):
        stock = Stock('EE','SET')
        result = stock.get_quarter_fin()
        self.assertEqual(result,self.quarter)

    def test_no_data(self):
        stock = Stock('PTT','SET')
        result = stock.get_quarter_fin()
        self.assertEqual(result,[])

class TestFetchFinancial(unittest.TestCase):
    def setUp(self):
        self.original_get_stock_id = Stock.get_stock_id
        self.original_fetch_set_fin = Stock.fetch_set_fin
        self.original_insert_set_fin = Stock.insert_set_fin
        self.original_get_quarter_fin = Stock.get_quarter_fin

        Stock.get_stock_id = MagicMock(return_value = 1)
        Stock.fetch_set_fin = MagicMock(return_value = [['2556Q1'],['2556Q2'],['2560Q1']])
        Stock.insert_set_fin = MagicMock()

    def tearDown(self):
        Stock.get_stock_id = self.original_get_stock_id
        Stock.fetch_set_fin = self.original_fetch_set_fin
        Stock.insert_set_fin = self.original_insert_set_fin
        Stock.get_quarter_fin = self.original_get_quarter_fin

    def test_check_dup(self):
        Stock.get_quarter_fin = MagicMock(return_value = ['2556Q1','2556Q2'])
        stock = Stock('EE','SET')
        stock.fetch_financial()
        Stock.insert_set_fin.assert_called_once_with(1,['2560Q1'])

    def test_check_no_dup(self):
        Stock.get_quarter_fin = MagicMock(return_value = ['2555Q1','2555Q2'])
        stock = Stock('EE','SET')
        stock.fetch_financial()
        Stock.insert_set_fin.assert_has_calls([call(1,['2556Q1']),call(1,['2556Q2']),call(1,['2560Q1'])])

    def test_check_all_dup(self):
        Stock.get_quarter_fin = MagicMock(return_value = ['2556Q1','2556Q2','2560Q1'])
        stock = Stock('EE','SET')
        stock.fetch_financial()
        self.assertEqual(Stock.insert_set_fin.call_count,0)

class TestFinancialStatement(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE "set_financial_statement" (
                "financial_id"	INTEGER PRIMARY KEY,
                "stock_id"	INTEGER,
                "quarter"	TEXT,
                "total_asset"	REAL,
                "liabilities"	REAL,
                "equity"	REAL,
                "paid_up_capital"	REAL,
                "revenue"	REAL,
                "net_profit"	REAL,
                "EPS"	REAL,
                "ROA"	REAL,
                "ROE"	REAL,
                "net_profit_margin"	REAL,
                "market_capitalization"	REAL,
                "P/E"	REAL,
                "P/BV"	REAL,
                "dividend_yield"	REAL
            )
        """)
        self.cursor.execute("INSERT INTO stock (symbol) VALUES (?)", ('EE',))
        self.cursor.execute("INSERT INTO set_financial_statement VALUES (null,1,'2555Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02,12.64,2.61,5.8,6.12,931153.68,8.9,1.54,3.99)")
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        sqlite3.connect = self.original_connect
        
    def test_get_fin(self):
        stock = Stock('EE','SET')
        result = stock.financial_statement()
        self.assertEqual(result,[(1,1,'2555Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02,12.64,2.61,5.8,6.12,931153.68,8.9,1.54,3.99)])

    def test_no_data(self):
        stock = Stock('PTT','SET')
        result = stock.financial_statement()
        self.assertEqual(result,[])

class TestGetStockAndCryptoData(unittest.TestCase):
    def test_pull(self):
        yfinance_mock = MagicMock()
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
        with patch('yfinance.download',yfinance_mock.download):
            result = Stock('PTT','SET').get_stock_and_crypto_data("TESTTEST",'2022-02-02 00:00:00','1h')
            assert result == [[50.0,50.25,48.0,49.75,24543,'2022-12-25 09:30:00'],[52.0, 52.0, 49.0, 52.0, 67854, '2022-12-26 10:30:00'],[48.0, 49.0, 47.0, 48.5, 16875,'2022-12-27 15:30:00']]

    def test_pull_none(self):
        yfinance_mock = MagicMock()
        data = {}
        data_date = pd.DataFrame(data)
        yfinance_mock.download.return_value = data_date
        with patch('yfinance.download',yfinance_mock.download):
            result = Stock('PTT','SET').get_stock_and_crypto_data("TESTTEST",'2022-02-02 00:00:00','1h')
            assert result == None

class TestInsertStockPrice(unittest.TestCase):
    def setUp(self):
        self.stock = [('EE',)]
        self.price_day = [(1,'2022-10-2 00:00:00',10,11,12,13,1000), (1,'2022-10-3 00:00:00',10,11,12,13,2000), (1,'2022-10-4 00:00:00',10,11,12,13,3000)]
        self.price_hour = [(1,'2022-10-4 10:00:00',5,6,7,8,100), (1,'2022-10-4 11:00:00',5,6,7,8,200), (1,'2022-10-4 12:00:00',5,6,7,8,300)]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_day (
                price_id INTEGER PRIMARY KEY,
                stock_id INTEGER,
                [datetime] TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE stock_price_hour (
                price_id INTEGER PRIMARY KEY,
                stock_id INTEGER,
                [datetime] TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INT
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", self.stock)
        self.cursor.executemany("INSERT INTO stock_price_day VALUES (null,?,?,?,?,?,?,?)", self.price_day)
        self.cursor.executemany("INSERT INTO stock_price_hour VALUES (null,?,?,?,?,?,?,?)", self.price_hour)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.price_day = None
        self.price_hour = None
        self.stock = None
        sqlite3.connect = self.original_connect
        
    def test_dup(self):
        value = [(10,11,12,13,1000,'2022-10-2 00:00:00'), (10,11,12,13,2000,'2022-10-5 00:00:00'), (10,11,12,13,3000,'2022-10-6 00:00:00')]
        stock = Stock('EE','SET')
        stock.insert_stock_price(value,'1d')

        self.cursor.execute("SELECT * FROM stock_price_day")
        result = self.cursor.fetchall()
        self.assertEqual(result,[(1,1,'2022-10-2 00:00:00',10,11,12,13,1000), 
                                 (2,1,'2022-10-3 00:00:00',10,11,12,13,2000), 
                                 (3,1,'2022-10-4 00:00:00',10,11,12,13,3000),
                                 (4,1,'2022-10-5 00:00:00',10,11,12,13,2000),
                                 (5,1,'2022-10-6 00:00:00',10,11,12,13,3000)])
        
    def test_no_dup(self):
        value = [(10,11,12,13,1000,'2022-10-5 00:00:00'), (10,11,12,13,2000,'2022-10-6 00:00:00'), (10,11,12,13,3000,'2022-10-7 00:00:00')]
        stock = Stock('EE','SET')
        stock.insert_stock_price(value,'1d')

        self.cursor.execute("SELECT * FROM stock_price_day")
        result = self.cursor.fetchall()
        self.assertEqual(result,[(1,1,'2022-10-2 00:00:00',10,11,12,13,1000), 
                                 (2,1,'2022-10-3 00:00:00',10,11,12,13,2000), 
                                 (3,1,'2022-10-4 00:00:00',10,11,12,13,3000),
                                 (4,1,'2022-10-5 00:00:00',10,11,12,13,1000),
                                 (5,1,'2022-10-6 00:00:00',10,11,12,13,2000),
                                 (6,1,'2022-10-7 00:00:00',10,11,12,13,3000)])

    def test_all_dup(self):
        value = [(10,11,12,13,1000,'2022-10-2 00:00:00'), (10,11,12,13,2000,'2022-10-3 00:00:00'), (10,11,12,13,3000,'2022-10-4 00:00:00')]
        stock = Stock('EE','SET')
        stock.insert_stock_price(value,'1d')

        self.cursor.execute("SELECT * FROM stock_price_day")
        result = self.cursor.fetchall()
        self.assertEqual(result,[(1,1,'2022-10-2 00:00:00',10,11,12,13,1000), 
                                 (2,1,'2022-10-3 00:00:00',10,11,12,13,2000), 
                                 (3,1,'2022-10-4 00:00:00',10,11,12,13,3000)])    

class TestFetchStockPrice(unittest.TestCase):
    def setUp(self):
        self.original_latest_update_time = Stock.latest_update_time
        self.original_insert_stock_price = Stock.insert_stock_price
        self.original_get_stock_and_crypto_data = Stock.get_stock_and_crypto_data

        Stock.latest_update_time = MagicMock(return_value = '2022-02-02')
        Stock.insert_stock_price = MagicMock()
        Stock.get_stock_and_crypto_data = MagicMock()
    
    def tearDown(self):
        Stock.latest_update_time = self.original_latest_update_time
        Stock.insert_stock_price = self.original_insert_stock_price
        Stock.get_stock_and_crypto_data = self.original_get_stock_and_crypto_data

    def test_fetch(self):
        stock = Stock('EE','SET')
        stock.fetch_stock_price('1h')

        Stock.latest_update_time.assert_called_once_with(interval='1h')
        Stock.get_stock_and_crypto_data.assert_called_once_with('EE.bk','2022-02-02','1h')
        Stock.insert_stock_price.assert_called_once()

    def test_fetch_None_data(self):
        Stock.get_stock_and_crypto_data.return_value = None
        stock = Stock('EE','SET')
        result = stock.fetch_stock_price('1h')
        self.assertEqual(result,'fail')

        Stock.latest_update_time.assert_called_once_with(interval='1h')
        Stock.get_stock_and_crypto_data.assert_called_once_with('EE.bk','2022-02-02','1h')
        Stock.insert_stock_price.assert_not_called()

    def test_fetch_error(self):
        stock = Stock('EE','SET')
        with self.assertRaises(ValueError) as error:
            stock.fetch_stock_price('1m')
        self.assertEqual(str(error.exception),"The interval 1m is not available. The available interval are 1h,1d")

class TestGetAllNews(unittest.TestCase):
    def setUp(self):
        self.stock = [('EE',)]
        self.news = [(1,'test news','2022-10-3 00:00:00','www.test.com','many news'), (2,'test news1','2022-10-2 00:00:00','www.test1.com','many news')]
        self.many = [(1,1),(2,1)]
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE [stock] (
                stock_id INTEGER PRIMARY KEY,
                symbol TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE "set_news" (
                "news_id"	INTEGER PRIMARY KEY,
                "title"	TEXT,
                "datetime"	TEXT,
                "link"	TEXT,
                "content"	TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE "many_set_news" (
                "news_id"	INTEGER,
                "stock_id"	INTEGER
            )
        """)
        self.cursor.executemany("INSERT INTO stock (symbol) VALUES (?)", self.stock)
        self.cursor.executemany("INSERT INTO set_news VALUES (?,?,?,?,?)", self.news)
        self.cursor.executemany("INSERT INTO many_set_news VALUES (?,?)", self.many)
        self.conn.commit()
        self.original_connect = sqlite3.connect
        mock_connect = MagicMock()
        mock_conn = MagicMock()
        sqlite3.connect = mock_connect
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = self.conn.cursor()
        mock_conn.commit.return_value = self.conn.commit()

    def tearDown(self):
        """Close the database connection"""
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.stock = None
        self.news = None
        self.many = None
        sqlite3.connect = self.original_connect
        
    def test_get_news(self):
        stock = Stock('EE','SET')
        result = stock.get_all_news()
        self.assertEqual(result,self.news)

    def test_no_data(self):
        stock = Stock('PTT','SET')
        result = stock.get_all_news()
        self.assertEqual(result,[])

class TestGetStockLocation(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        self.original_get_stock_id = Stock.get_stock_id
        Stock.get_stock_id = MagicMock(return_value = 1)
        self.mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=self.mock_conn)
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        Stock.get_stock_id = self.original_get_stock_id
        self.mock_conn = None
        self.mock_cursor = None

    def test_get_location(self):
        self.mock_cursor.fetchall.return_value = [("2022-02-03","Thailand",10,10),("2022-02-02","Bangkok",8,8)]
        stock = Stock('EE','SET')
        result = stock.get_stock_location()
        self.assertEqual(result,[("2022-02-03","Thailand",10,10),("2022-02-02","Bangkok",8,8)])
        self.mock_cursor.execute.assert_called_once_with("SELECT c.[datetime],a.location_name, a.lat, a.lon FROM location AS a INNER JOIN set_location AS b ON a.location_id = b.location_id INNER JOIN set_news AS c ON b.news_id = c.news_id WHERE b.stock_id = 1 AND c.[datetime] >= '' ORDER BY c.[datetime] DESC")

    def test_get_no_location(self):
        self.mock_cursor.fetchall.return_value = []
        stock = Stock('AAPL','NASDAQ')
        result = stock.get_stock_location()
        self.assertEqual(result,[])
        self.mock_cursor.execute.assert_called_once_with("SELECT c.[datetime],a.location_name, a.lat, a.lon FROM location AS a INNER JOIN nasdaq_location AS b ON a.location_id = b.location_id INNER JOIN nasdaq_news AS c ON b.news_id = c.news_id WHERE b.stock_id = 1 AND c.[datetime] >= '' ORDER BY c.[datetime] DESC")





class TestGetAllTag(unittest.TestCase):
    def setUp(self):
        self.original_requests = requests.get
        self.mock_response = MagicMock()
        requests.get = MagicMock(return_value=self.mock_response)
        
    def tearDown(self):
        requests.get = self.original_requests
        self.mock_response = None

    def test_yahoo_get_all_tag_normal(self):
        html = '<li class="js-stream-content Pos(r)">xxxxx</li><li class="abc">zzzzz</li><li class="js-stream-content Pos(r)">yyyyy</li>'
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("NASDAQ")
        result = news.nasdaq_get_all_tags("APPL")
        result = [str(i) for i in result]
        self.assertEqual(result,['<li class="js-stream-content Pos(r)">xxxxx</li>','<li class="js-stream-content Pos(r)">yyyyy</li>'])

    def test_yahoo_get_all_tag_wrong(self):
        html = '<li class="aaa">xxxxx</li><li class="abc">zzzzz</li><li class="ccc">yyyyy</li>'
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("NASDAQ")
        result = news.nasdaq_get_all_tags("APPL")
        self.assertEqual(result,[])

    def test_yahoo_get_all_tag_null(self):
        html = ''
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("NASDAQ")
        result = news.nasdaq_get_all_tags("APPL")
        self.assertEqual(result,[])

    def test_yahoo_get_all_tag_bad_request(self):
        html = ''
        self.mock_response.text = html
        self.mock_response.status_code = 400
        news = News("NASDAQ")
        result = news.nasdaq_get_all_tags("APPL")
        self.assertEqual(result,[])

    def test_set_get_all_tag_normal(self):
        html = '<main><h class="info">xxxx</h><h class="info">yyyy</h></main><other>none</other>'
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("SET")
        result = news.set_get_all_tags('PTT',1)
        result = [str(i) for i in result]
        self.assertEqual(result,['<h class="info">xxxx</h>','<h class="info">yyyy</h>'])

    def test_set_get_all_tag_wrong(self):
        html = '<main><h class="aaa">xxxx</h><h class="abc">yyyy</h></main><other>none</other>'
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("SET")
        result = news.set_get_all_tags('PTT',1)
        self.assertEqual(result,[])

    def test_set_get_all_tag_null(self):
        html = ''
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("SET")
        result = news.set_get_all_tags('PTT',1)
        self.assertEqual(result,[])

    def test_set_get_all_tag_bad_request(self):
        html = ''
        self.mock_response.text = html
        self.mock_response.status_code = 400
        news = News("SET")
        result = news.set_get_all_tags('PTT',1)
        self.assertEqual(result,[])

class TestGetTitleLink(unittest.TestCase):
    def setUp(self):
        self.original_requests = requests.get
        self.mock_response = MagicMock()
        requests.get = MagicMock(return_value=self.mock_response)
        
    def tearDown(self):
        requests.get = self.original_requests
        self.mock_response = None

    def test_yahoo_title_and_link_normal(self):
        html = '<li class="js-stream-content Pos(r)"><a href = "https://finance.yahoo.com">yahoo</a></li><li class="js-stream-content Pos(r)"><a href = "https://google.com">google</a></li>'
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("NASDAQ")
        tag = news.nasdaq_get_all_tags("APPL")
        result = news.nasdaq_title_link(tag)
        self.assertEqual(result,[{'title': 'yahoo', 'link': 'https://finance.yahoo.com'}, {'title': 'google', 'link': 'https://google.com'}])

    def test_yahoo_title_and_link_null(self):
        news = News("NASDAQ")
        result = news.nasdaq_title_link([])
        self.assertEqual(result,[])

    def test_set_title_and_link_normal(self):
        html = '<main><h class="info"><l class = "entry-title"><a href="https://finance.yahoo.com">yahoo</a></l><time class="updated" datetime="2022-02-02 10:00:00">2022</time></h><h class="info"><l class = "entry-title"><a href = "https://google.com">google</a></l><time class="updated" datetime = "2022-02-02 11:00:00">2022</time></h></main><other>none</other>'
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("SET")
        tag = news.set_get_all_tags('PTT',1)
        result = news.set_title_link_time(tag)
        self.assertEqual(result,[{'title': 'yahoo', 'link': 'https://finance.yahoo.com', 'datetime':'2022-02-02 10:00:00'}, {'title': 'google', 'link': 'https://google.com', 'datetime':'2022-02-02 11:00:00'}])

    def test_set_title_and_link_null(self):
        news = News("SET")
        result = news.set_title_link_time([])
        self.assertEqual(result,[])

class TestContent(unittest.TestCase):
    def setUp(self):
        self.original_requests = requests.get
        self.mock_response = MagicMock()
        requests.get = MagicMock(return_value=self.mock_response)
        
    def tearDown(self):
        requests.get = self.original_requests
        self.mock_response = None

    def test_yahoo_content_time_normal(self):
        html = '<time datetime = "2022-10-10"></time><li class="caas-body"><p>Test</p><p>Test2</p><p>Test3</p></li>'
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("NASDAQ")
        result = news.nasdaq_content_time('https://finance.yahoo.com')
        self.assertEqual(result,{'content': 'Test\nTest2\nTest3\n', 'datetime': '2022-10-10'})

    def test_yahoo_content_time_null(self):
        html = ''
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("NASDAQ")
        result = news.nasdaq_content_time('https://finance.yahoo.com')
        self.assertEqual(result,{'content': 'null', 'datetime': 'null'})
    
    def test_set_content_time_normal(self):
        html = '<li class="entry-content"><p>Test</p><p>Test2</p><p>Test3</p></li>'
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("SET")
        result = news.set_content('https://finance.yahoo.com')
        self.assertEqual(result,'Test\nTest2\nTest3\n')

    def test_set_content_time_null(self):
        html = ''
        self.mock_response.text = html
        self.mock_response.status_code = 200
        news = News("SET")
        result = news.set_content('https://finance.yahoo.com')
        self.assertEqual(result,'null')

class TestNewDict(unittest.TestCase):
    def setUp(self):
        self.original_nasdaq_content_time = News.nasdaq_content_time
        self.original_set_content = News.set_content
        News.nasdaq_content_time = MagicMock(return_value = {'content':'test','datetime':'2022-02-02 00:00:00'})
        News.set_content = MagicMock(return_value = 'test')
        
    def tearDown(self):
        News.nasdaq_content_time = self.original_nasdaq_content_time
        News.set_content = self.original_set_content

    def test_yahoo_new_dict(self):
        news = News('NASDAQ')
        result = news.nasdaq_news_dict([{'link':'www.yahoo.com','title':'yahoo'}],'AAPL')
        self.assertEqual(result,[{'content':'test','datetime':'2022-02-02 00:00:00','stock':'AAPL','link':'www.yahoo.com','title':'yahoo'}])

    def test_set_new_dict(self):
        news = News('SET')
        result = news.set_news_dict([{'link':'www.set.com','title':'set','datetime':'2022-02-02 00:00:00'}],'PTT')
        self.assertEqual(result,[{'content':'test','datetime':'2022-02-02 00:00:00','stock':'PTT','link':'www.set.com','title':'set'}])
      
class TestInsertNews(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_insert_news(self):
        news = News("NASDAQ")
        news.insert_news({'title':'yahoo','datetime':'2020-10-10','link':'https://finance.yahoo.com','content':'TestYahoo12345'})
        self.mock_cursor.execute.assert_called_once_with('INSERT INTO nasdaq_news VALUES (null,?,?,?,?)', ('yahoo', '2020-10-10', 'https://finance.yahoo.com', 'TestYahoo12345'))

class TestGetNewsID(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_get_news_id(self):
        self.mock_cursor.fetchall.return_value = [(1,)]
        news = News("NASDAQ")
        result = news.get_news_id('aaaa')
        self.assertEqual(result,1)
        self.mock_cursor.execute.assert_called_once_with("SELECT news_id FROM nasdaq_news WHERE title = ?",('aaaa',))

    def test_get_news_id_none(self):
        self.mock_cursor.fetchall.return_value = []
        news = News("NASDAQ")
        result = news.get_news_id('aaaa')
        self.assertEqual(result,None)
        self.mock_cursor.execute.assert_called_once_with("SELECT news_id FROM nasdaq_news WHERE title = ?",('aaaa',))

class TestCheckRelation(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_check_relation_have_relation(self):
        self.mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]
        news = News("NASDAQ")
        result = news.check_relation(1,2)
        self.assertEqual(result,True)
        self.mock_cursor.execute.assert_called_once_with("SELECT news_id FROM many_nasdaq_news WHERE stock_id = 1")

    def test_check_relation_have_no_relation(self):
        self.mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]
        news = News("NASDAQ")
        result = news.check_relation(1,4)
        self.assertEqual(result,False)
        self.mock_cursor.execute.assert_called_once_with("SELECT news_id FROM many_nasdaq_news WHERE stock_id = 1")

class TestGetAllTitle(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_get_all_title(self):
        expect_result = ["news1","news2","news3"]
        mock_news = [(symbol,) for symbol in expect_result]
        self.mock_cursor.fetchall.return_value = mock_news
        news = News("NASDAQ")
        result = news.get_all_title()
        self.assertEqual(result,expect_result)
        self.mock_cursor.execute.assert_called_once_with("SELECT title FROM nasdaq_news")

    def test_get_all_title_none(self):
        self.mock_cursor.fetchall.return_value = []
        news = News("NASDAQ")
        result = news.get_all_title()
        self.assertEqual(result,[])
        self.mock_cursor.execute.assert_called_once_with("SELECT title FROM nasdaq_news")

class TestGetTitleContent(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_get_title_content(self):
        expect_result = [("news1","ssss")]
        self.mock_cursor.fetchall.return_value = expect_result
        news = News("NASDAQ")
        result = news.get_title_content(1)
        self.assertEqual(result,("news1","ssss"))
        self.mock_cursor.execute.assert_called_once_with("SELECT title,content FROM nasdaq_news WHERE news_id = 1")

    def test_get_title_content_none(self):
        self.mock_cursor.fetchall.return_value = []
        news = News("NASDAQ")
        result = news.get_title_content(1)
        self.assertEqual(result,[])
        self.mock_cursor.execute.assert_called_once_with("SELECT title,content FROM nasdaq_news WHERE news_id = 1")

class TestInsertManyNews(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_insert_many_news(self):
        news = News("NASDAQ")
        news.insert_many_news(1,2)
        self.mock_cursor.execute.assert_called_once_with("INSERT INTO many_nasdaq_news VALUES (1,2)")

class TestInsertCheckData(unittest.TestCase):
    def setUp(self):
        self.original_get_all_title = News.get_all_title
        self.original_get_stock_id = News.get_stock_id
        self.original_get_news_id = News.get_news_id
        self.original_check_relation = News.check_relation
        self.original_insert_many_news = News.insert_many_news
        self.original_insert_news= News.insert_news

        News.get_all_title = MagicMock(return_value = ['yahoo','set'])
        News.get_stock_id = MagicMock(return_value = 1)
        News.get_news_id = MagicMock(return_value = 1)
        News.insert_many_news = MagicMock()
        News.insert_news = MagicMock()

    def tearDown(self):
        News.get_all_title = self.original_get_all_title
        News.get_stock_id = self.original_get_stock_id
        News.get_news_id = self.original_get_news_id 
        News.check_relation = self.original_check_relation
        News.insert_many_news = self.original_insert_many_news 
        News.insert_news = self.original_insert_news

    def test_insert_check_data_have_news_but_no_relation(self):
        News.check_relation = MagicMock(return_value = False)
        news = News("NASDAQ")
        news.insert_check_data({'title':'yahoo','stock':'a','link':'www.yahoo.com','content':'aaaaaa'})
        News.insert_many_news.assert_called_once()
        News.insert_news.assert_not_called()

    def test_insert_check_data_have_news_and_relation(self):
        News.check_relation = MagicMock(return_value = True)
        news = News("NASDAQ")
        news.insert_check_data({'title':'yahoo','stock':'a','link':'www.yahoo.com','content':'aaaaaa'})
        News.insert_many_news.assert_not_called()
        News.insert_news.assert_not_called()

    def test_insert_check_data_new_news(self):
        News.check_relation = MagicMock(return_value = False)
        news = News("NASDAQ")
        news.insert_check_data({'title':'news','stock':'a','link':'www.yahoo.com','content':'aaaaaa'})
        News.insert_many_news.assert_called_once()
        News.insert_news.assert_called_once()
 
class TestFetchSpecificNews(unittest.TestCase):
    def setUp(self):
        self.original_nasdaq_get_all_tags = News.nasdaq_get_all_tags
        self.original_nasdaq_title_link = News.nasdaq_title_link
        self.original_nasdaq_news_dict = News.nasdaq_news_dict
        self.original_insert_check_data  = News.insert_check_data
        self.original_set_get_all_tags = News.set_get_all_tags
        self.original_set_title_link = News.set_title_link_time
        self.original_set_news_dict = News.set_news_dict
         
        News.nasdaq_title_link = MagicMock()
        News.insert_check_data = MagicMock()
        News.nasdaq_news_dict = MagicMock(return_value = [{},{},{},{}])
        News.set_get_all_tags = MagicMock() 
        News.set_title_link_time = MagicMock() 
        News.set_news_dict = MagicMock(return_value = [{},{},{},{}])

    def tearDown(self):
        News.nasdaq_get_all_tags = self.original_nasdaq_get_all_tags
        News.nasdaq_title_link = self.original_nasdaq_title_link
        News.nasdaq_news_dict = self.original_nasdaq_news_dict
        News.insert_check_data = self.original_insert_check_data
        News.set_get_all_tags = self.original_set_get_all_tags  
        News.set_title_link_time = self.original_set_title_link  
        News.set_news_dict = self.original_set_news_dict  

    def test_fetch_yahoo_news_have_tag(self):
        News.nasdaq_get_all_tags = MagicMock(return_value = ['<li class="js-stream-content Pos(r)">xxxxx</li>','<li class="js-stream-content Pos(r)">yyyyy</li>'])
        news = News('NASDAQ')
        news.fetch_nasdaq_news('AAPL')
        News.nasdaq_get_all_tags.assert_called_once()
        News.nasdaq_title_link.assert_called_once()
        News.nasdaq_news_dict.assert_called_once()
        self.assertEqual(News.insert_check_data.call_count,4)

    def test_fetch_yahoo_news_no_tag(self):
        News.nasdaq_get_all_tags = MagicMock(return_value = [])
        news = News('NASDAQ')
        result = news.fetch_nasdaq_news('AAPL')
        News.nasdaq_get_all_tags.assert_called_once()
        News.nasdaq_title_link.assert_not_called()
        News.nasdaq_news_dict.assert_not_called()
        self.assertEqual(result,None)

    def test_fetch_set_news_have_tag(self):
        News.set_get_all_tags = MagicMock(return_value = ['<li class="js-stream-content Pos(r)">xxxxx</li>','<li class="js-stream-content Pos(r)">yyyyy</li>'])
        news = News('SET')
        news.fetch_set_news('PTT')
        News.set_get_all_tags.assert_called_once()
        News.set_title_link_time.assert_called_once()
        News.set_news_dict.assert_called_once()
        self.assertEqual(News.insert_check_data.call_count,4)

    def test_fetch_set_news_no_tag(self):
        News.set_get_all_tags = MagicMock(return_value = [])
        news = News('SET')
        result = news.fetch_set_news('PTT')
        News.set_get_all_tags.assert_called_once()
        News.set_title_link_time.assert_not_called()
        News.set_news_dict.assert_not_called()
        self.assertEqual(result,None)

class TestFetchNews(unittest.TestCase):
    def setUp(self):
        self.original_fetch_nasdaq_news = News.fetch_nasdaq_news
        self.original_fetch_set_news = News.fetch_set_news
        News.fetch_nasdaq_news = MagicMock()
        News.fetch_set_news = MagicMock()
    
    def tearDown(self):
        News.fetch_nasdaq_news = self.original_fetch_nasdaq_news
        News.fetch_set_news = self.original_fetch_set_news

    def test_fetch_news_nasdaq(self):
        news = News('NASDAQ')
        news.fetch_news('AAPL')
        News.fetch_nasdaq_news.assert_called_once_with('AAPL')
        News.fetch_set_news.assert_not_called()

    def test_fetch_news_set(self):
        news = News('SET')
        news.fetch_news('PTT')
        News.fetch_set_news.assert_called_once_with('PTT')
        News.fetch_nasdaq_news.assert_not_called()
        
    def test_fetch_news_crypto(self):
        news = News('CRYPTO')
        news.fetch_news('BTC')
        News.fetch_nasdaq_news.assert_called_once_with('BTC')
        News.fetch_set_news.assert_not_called()

class TestDetect(unittest.TestCase):
    def setUp(self):
        self.original_translator = Translator.detect
        self.mock_obj = MagicMock()
        Translator.detect = MagicMock(return_value = self.mock_obj)

    def tearDown(self):
        Translator.detect =self.original_translator
        self.mock_obj = None

    def test_detect_true(self):
        self.mock_obj.lang = 'en'
        news = News('NASDAQ')
        result = news.detect('Hello world')
        self.assertEqual(result,True)

    def test_detect_false(self):
        self.mock_obj.lang = 'th'
        news = News('NASDAQ')
        result = news.detect('Hello world')
        self.assertEqual(result,False)

class TestTranslateText(unittest.TestCase):
    def setUp(self):
        self.original_detect = News.detect
        self.original_translator = Translator.detect
        self.mock_obj = MagicMock()
        Translator.translate = MagicMock(return_value = self.mock_obj)

    def tearDown(self):
        Translator.translate = self.original_translator
        News.detect = self.original_detect
        self.mock_obj = None

    def test_translate_text_thai(self):
        News.detect = MagicMock(return_value = False)
        self.mock_obj.text = 'Hello world'
        news = News('NASDAQ')
        result = news.translate_text('สวัสดีโลก')
        self.assertEqual(result,'Hello world')

    def test_translate_text_eng(self):
        News.detect = MagicMock(return_value = True)
        news = News('NASDAQ')
        result = news.translate_text('Hello world')
        self.assertEqual(result,'Hello world')
        Translator.translate.assert_not_called()

    def test_translate_no_text(self):
        News.detect = MagicMock(return_value = True)
        news = News('NASDAQ')
        result = news.translate_text('')
        self.assertEqual(result,'')
        Translator.translate.assert_not_called()

class TestTranslateParagraph(unittest.TestCase):
    def setUp(self):
        self.original_detect = News.detect
        self.original_translate_text = News.translate_text
        
    def tearDown(self):
        News.detect = self.original_detect
        News.translate_text = self.original_translate_text

    def test_translate_paragraph_thai(self):
        News.detect = MagicMock(return_value = False)
        News.translate_text = MagicMock(return_value = 'translate')
        news = News('NASDAQ')
        result = news.translate_paragraph('ฟหกดฟหกดหฟกา่ด้ฟหา่้ดา\nกหด้เ่กด้เ่ห้กาด่เ้หสาก่ด้\nฟ่้เกด่้เ่หก้ดเส้หสกา่้')
        self.assertEqual(result,'translate translate translate ')

    def test_translate_paragraph_eng(self):
        News.detect = MagicMock(return_value = True)
        News.translate_text = MagicMock()
        news = News('NASDAQ')
        result = news.translate_paragraph('abc\nabc\nabc')
        self.assertEqual(result,'abc\nabc\nabc')
        News.translate_text.assert_not_called()

    def test_translate_paragraph_none(self):
        News.detect = MagicMock(return_value = True)
        News.translate_text = MagicMock()
        news = News('NASDAQ')
        result = news.translate_paragraph('')
        self.assertEqual(result,'')
        News.translate_text.assert_not_called()

class TestCombineTranslate(unittest.TestCase):
    def setUp(self):
        self.original_get_title_content = News.get_title_content
        self.original_translate_text = News.translate_text
        self.original_translate_paragraph = News.translate_paragraph

        News.get_title_content = MagicMock()
        
    def tearDown(self):
        News.get_title_content = self.original_get_title_content
        News.translate_text = self.original_translate_text
        News.translate_paragraph = self.original_translate_paragraph

    def test_combine_translate(self):
        News.translate_text = MagicMock(return_value = 'translate')
        News.translate_paragraph = MagicMock(return_value = 'abcdefg')
        news = News('NASDAQ')
        result = news.combine_translate(1)
        self.assertEqual(result,'translate abcdefg')
        News.get_title_content.assert_called_once_with(1)

    def test_combine_translate_only_title(self):
        News.translate_text = MagicMock(return_value = 'translate')
        News.translate_paragraph = MagicMock(return_value = '')
        news = News('NASDAQ')
        result = news.combine_translate(1)
        self.assertEqual(result,'translate ')
        News.get_title_content.assert_called_once_with(1)

    def test_combine_translate_only_content(self):
        News.translate_text = MagicMock(return_value = '')
        News.translate_paragraph = MagicMock(return_value = 'abcdefg')
        news = News('NASDAQ')
        result = news.combine_translate(1)
        self.assertEqual(result,' abcdefg')
        News.get_title_content.assert_called_once_with(1)

    def test_combine_translate_none(self):
        News.translate_text = MagicMock(return_value = '')
        News.translate_paragraph = MagicMock(return_value = '')
        news = News('NASDAQ')
        result = news.combine_translate(1)
        self.assertEqual(result,' ')
        News.get_title_content.assert_called_once_with(1)






class TestGetLocationID(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_get_location_id(self):
        self.mock_cursor.fetchall.return_value = [(1,)]
        location = Location('NASDAQ')
        result = location.get_location_id('Thailand')
        self.assertEqual(result,1)
        self.mock_cursor.execute.assert_called_once_with("SELECT location_id FROM location WHERE location_name = ?",('Thailand',))

class TestGetLocationLatestDatetime(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor

    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_get_lo_latest_datetime(self):
        self.mock_cursor.fetchall.return_value = [("2022-02-02 00:00:00",)]
        location = Location('NASDAQ')
        result = location.get_lo_latest_datetime(1)
        self.assertEqual(result,"2022-02-02 00:00:00")
        self.mock_cursor.execute.assert_called_once_with("SELECT DISTINCT a.[datetime] FROM nasdaq_news AS a INNER JOIN nasdaq_location AS b ON a.news_id = b.news_id WHERE b.stock_id = 1 ORDER BY a.[datetime] DESC LIMIT 1")

    def test_get_lo_latest_datetime_none(self):
        self.mock_cursor.fetchall.return_value = []
        location = Location('NASDAQ')
        result = location.get_lo_latest_datetime(1)
        self.assertEqual(result,None)
        self.mock_cursor.execute.assert_called_once_with("SELECT DISTINCT a.[datetime] FROM nasdaq_news AS a INNER JOIN nasdaq_location AS b ON a.news_id = b.news_id WHERE b.stock_id = 1 ORDER BY a.[datetime] DESC LIMIT 1")

class TestGetDatetime(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_get_datetime(self):
        self.mock_cursor.fetchall.return_value = [('2022-02-02 00:00:00',)]
        obj = Location('NASDAQ')
        result = obj.get_news_datetime(1)
        self.assertEqual(result,'2022-02-02 00:00:00')
        self.mock_cursor.execute.assert_called_once_with("SELECT DISTINCT [datetime] FROM nasdaq_news WHERE news_id = 1")

    def test_get_datetime_none(self):
        self.mock_cursor.fetchall.return_value = []
        obj = Location('NASDAQ')
        result = obj.get_news_datetime(1)
        self.assertEqual(result,None)
        self.mock_cursor.execute.assert_called_once_with("SELECT DISTINCT [datetime] FROM nasdaq_news WHERE news_id = 1")

class TestGetAllLocationName(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_get_all_location_name(self):
        self.mock_cursor.fetchall.return_value = [("Thailand",),("Bangkok",)]
        location = Location('NASDAQ')
        result = location.get_all_location_name()
        self.assertEqual(result,["Thailand","Bangkok"])
        self.mock_cursor.execute.assert_called_once_with("SELECT location_name FROM location")

    def test_get_all_location_name_none(self):
        self.mock_cursor.fetchall.return_value = []
        location = Location('NASDAQ')
        result = location.get_all_location_name()
        self.assertEqual(result,[])
        self.mock_cursor.execute.assert_called_once_with("SELECT location_name FROM location")

class TestCheckLocateRelation(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_check_locate_relation_have_relation(self):
        self.mock_cursor.fetchall.return_value = [(1,),(2,)]
        location = Location('NASDAQ')
        result = location.check_locate_relation(1,2,3)
        self.assertEqual(result,True)
        self.mock_cursor.execute.assert_called_once_with("SELECT location_id FROM nasdaq_location WHERE news_id = 2 and stock_id = 3")

    def test_check_locate_relation_no_relation(self):
        self.mock_cursor.fetchall.return_value = [(2,),(3,)]
        location = Location('NASDAQ')
        result = location.check_locate_relation(1,2,3)
        self.assertEqual(result,False)
        self.mock_cursor.execute.assert_called_once_with("SELECT location_id FROM nasdaq_location WHERE news_id = 2 and stock_id = 3")

class TestInsertLocation(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_insert_location(self):
        location = Location('NASDAQ')
        location.insert_location('Bangkok',{'lat':10,'lon':11})
        self.mock_cursor.execute.assert_called_once_with('INSERT INTO location VALUES (null,"Bangkok",10,11)')

class TestInsertManyLocation(unittest.TestCase):
    def setUp(self):
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        self.mock_cursor = None

    def test_insert_many_location(self):
        location = Location('NASDAQ')
        location.insert_many_location(1,2,3)
        self.mock_cursor.execute.assert_called_once_with('INSERT INTO nasdaq_location VALUES (1,2,3)')

class TestGetAllStockNewsID(unittest.TestCase):
    def setUp(self):
        self.original_get_lo_latest_datetime = Location.get_lo_latest_datetime
        self.original_get_stock_id = Location.get_stock_id
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        self.mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]
        Location.get_stock_id = MagicMock(return_value=1)

    def tearDown(self):
        sqlite3.connect = self.original_connect
        Location.get_stock_id = self.original_get_stock_id
        Location.get_lo_latest_datetime = self.original_get_lo_latest_datetime
        self.mock_cursor = None

    def test_get_all_stock_news_id_has_old_location(self):
        Location.get_lo_latest_datetime = MagicMock(return_value="2022-02-02")
        location = Location('NASDAQ')
        result = location.get_all_stock_news_id('AAPL')
        self.assertEqual(result,[1,2,3])
        self.mock_cursor.execute.assert_called_once_with("SELECT DISTINCT a.news_id FROM many_nasdaq_news AS a INNER JOIN nasdaq_news AS b ON a.news_id = b.news_id WHERE a.stock_id = 1 AND b.[datetime] > '2022-02-02' ORDER BY b.[datetime] ASC")

    def test_get_all_stock_news_id_no_old_location(self):
        Location.get_lo_latest_datetime = MagicMock(return_value=None)
        location = Location('NASDAQ')
        result = location.get_all_stock_news_id('AAPL')
        self.assertEqual(result,[1,2,3])
        self.mock_cursor.execute.assert_called_once_with("SELECT DISTINCT news_id FROM many_nasdaq_news WHERE stock_id = 1")

class TestGetAllProcessNewsID(unittest.TestCase):
    def setUp(self):
        self.original_get_stock_id = Location.get_stock_id
        self.original_connect = sqlite3.connect
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        self.mock_cursor = MagicMock()
        mock_conn.cursor.return_value = self.mock_cursor
        
    def tearDown(self):
        sqlite3.connect = self.original_connect
        Location.get_stock_id = self.original_get_stock_id
        self.mock_cursor = None

    def test_get_all_process_news_id(self):
        self.mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]
        Location.get_stock_id = MagicMock(return_value=1)
        location = Location('NASDAQ')
        result = location.get_all_process_news_id('AAPL')
        self.assertEqual(result,[1,2,3])
        self.mock_cursor.execute.assert_called_once_with("SELECT DISTINCT news_id FROM nasdaq_location WHERE stock_id = 1")

    def test_get_all_process_news_id_none(self):
        self.mock_cursor.fetchall.return_value = []
        Location.get_stock_id = MagicMock(return_value=1)
        location = Location('NASDAQ')
        result = location.get_all_process_news_id('AAPL')
        self.assertEqual(result,[])
        self.mock_cursor.execute.assert_called_once_with("SELECT DISTINCT news_id FROM nasdaq_location WHERE stock_id = 1")

class TestNoun(unittest.TestCase):
    def setUp(self):
        self.original_load = spacy.load
        mock_nlp = MagicMock()
        spacy.load = MagicMock(return_value = mock_nlp)
        self.chunks = MagicMock()
        self.obj1 = MagicMock()
        self.obj2 = MagicMock()
        self.obj3 = MagicMock()
        mock_nlp.return_value = self.chunks

    def tearDown(self):
        spacy.load = self.original_load
        self.chunks = None
        self.obj1 = None
        self.obj2 = None
        self.obj3 = None
        
    def test_noun(self):
        self.chunks.noun_chunks = [self.obj1,self.obj2,self.obj3]
        self.obj1.text = 'I'; self.obj2.text = 'Bangkok'; self.obj3.text = '10 years'
        string = "I lived in Bangkok for 10 years"
        result = Location('set').noun(string)
        self.assertEqual(result,['I','Bangkok','10 years'])
    
    def test_noun_one_word(self):
        self.chunks.noun_chunks = [self.obj1]
        self.obj1.text = 'years'
        string = "years"
        result = Location('set').noun(string)
        self.assertEqual(result,['years'])

    def test_noun_empty(self):
        self.chunks.noun_chunks = []
        string = ""
        result = Location('set').noun(string)
        self.assertEqual(result,[])

class TestLocation(unittest.TestCase):
    def setUp(self):
        self.original_load = spacy.load
        self.original_noun = Location.noun
        self.original_get_all_stock = Categories.get_all_stock
        mock_nlp = MagicMock()
        spacy.load = MagicMock(return_value = mock_nlp)
        chunks1 = MagicMock()
        chunks2 = MagicMock()
        chunks3 = MagicMock()
        self.obj1 = MagicMock()
        self.obj2 = MagicMock()
        self.obj3 = MagicMock()
        chunks1.ents = [self.obj1]
        chunks2.ents = [self.obj2]
        chunks3.ents = [self.obj3]
        mock_nlp.side_effect = [chunks1,chunks2,chunks3]

    def tearDown(self):
        spacy.load = self.original_load
        Location.noun = self.original_noun
        Categories.get_all_stock = self.original_get_all_stock
        self.obj1 = None
        self.obj2 = None
        self.obj3 = None

    def test_location_one_location(self):
        Categories.get_all_stock = MagicMock(return_value = [])
        Location.noun = MagicMock(return_value = ["I",'Bangkok','years'])
        self.obj1.label_ = 'PERSON'
        self.obj2.label_ = 'GPE'
        self.obj3.label_ = 'TIME'
        string = "I'm living in Bangkok for 10 years"
        result = Location('set').location(string)
        self.assertEqual(result,['Bangkok'])

    def test_location_two_location(self):
        Categories.get_all_stock = MagicMock(return_value = [])
        Location.noun = MagicMock(return_value = ['I','Paris','Bangkok'])
        self.obj1.label_ = 'PERSON'
        self.obj2.label_ = 'GPE'
        self.obj3.label_ = 'GPE'
        string = "I went to Bangkok after that I went to Paris"
        result = Location('set').location(string)
        self.assertEqual(set(result),set(['Paris','Bangkok']))

    def test_location_dup_location(self):
        Categories.get_all_stock = MagicMock(return_value = [])
        Location.noun = MagicMock(return_value = ['I','Bangkok','Bangkok'])
        self.obj1.label_ = 'PERSON'
        self.obj2.label_ = 'GPE'
        self.obj3.label_ = 'GPE'
        string = "I went to Bangkok after that I sleep in Bangkok"
        result = Location('set').location(string)
        self.assertEqual(result,['Bangkok'])

    def test_location_no_location(self):
        Categories.get_all_stock = MagicMock(return_value = [])
        Location.noun = MagicMock(return_value = ["I"])
        self.obj1.label_ = 'PERSON'
        string = "I am talking"
        result = Location('set').location(string)
        self.assertEqual(result,[])

class TestExtractLatLon(unittest.TestCase):
    def setUp(self):
        self.original_requests = requests.get
        self.mock_response = MagicMock()
        requests.get = MagicMock(return_value=self.mock_response)
        
    def tearDown(self):
        requests.get = self.original_requests
        self.mock_response = None

    def test_extract_lat_lon(self):
        self.mock_response.json.return_value = [{'name':'Bangkok','lat':12.6,'lon':10.1},{'name':'Bang','lat':1,'lon':2},{'lat':3,'lon':1}]
        result = Location('set').extract_lat_lon("Bangkok")
        self.assertEqual(result,{'lat':12.6,'lon':10.1})
        requests.get.assert_called_once_with('https://nominatim.openstreetmap.org/search.php?q=Bangkok&format=jsonv2')

    def test_extract_lat_lon_none(self):
        self.mock_response.json.return_value = []
        result = Location('set').extract_lat_lon("Nonthaburi")
        self.assertEqual(result,None)
        requests.get.assert_called_once_with('https://nominatim.openstreetmap.org/search.php?q=Nonthaburi&format=jsonv2')

class TestFetchLocation(unittest.TestCase):
    def setUp(self):
        self.original_get_stock_id = Location.get_stock_id
        self.original_get_all_stock_news_id = Location.get_all_stock_news_id
        self.original_get_all_process_news_id = Location.get_all_process_news_id
        self.original_get_news_datetime = Location.get_news_datetime
        self.original_combine_translate = News.combine_translate
        self.original_location = Location.location
        self.original_get_all_location_name = Location.get_all_location_name
        self.original_get_location_id = Location.get_location_id
        self.original_check_locate_relation = Location.check_locate_relation
        self.original_extract_lat_lon = Location.extract_lat_lon
        self.original_insert_many_location = Location.insert_many_location
        self.original_insert_location = Location.insert_location

        Location.get_stock_id = MagicMock(return_value = 1)
        Location.get_all_stock_news_id = MagicMock(return_value = [1,2,3])
        Location.get_news_datetime = MagicMock(return_value = '2022-02-02')
        News.combine_translate = MagicMock(return_value = "I live in Bangkok")
        Location.location = MagicMock(return_value = ['Bangkok'])
        Location.get_location_id = MagicMock(return_value = 1)
        Location.extract_lat_lon = MagicMock(return_value = {'lat':30,'lon':20})
        Location.insert_many_location = MagicMock()
        Location.insert_location = MagicMock()

    def tearDown(self):
        Location.get_stock_id = self.original_get_stock_id
        Location.get_all_stock_news_id = self.original_get_all_stock_news_id
        Location.get_all_process_news_id = self.original_get_all_process_news_id
        Location.get_news_datetime = self.original_get_news_datetime
        News.combine_translate = self.original_combine_translate
        Location.location = self.original_location
        Location.get_all_location_name = self.original_get_all_location_name
        Location.get_location_id = self.original_get_location_id
        Location.check_locate_relation = self.original_check_locate_relation
        Location.extract_lat_lon = self.original_extract_lat_lon
        Location.insert_many_location = self.original_insert_many_location
        Location.insert_location = self.original_insert_location

    def test_fetch_location_never_has_location(self):
        Location.get_all_process_news_id = MagicMock(return_value = [1,2])
        Location.check_locate_relation = MagicMock(return_value = False)
        Location.get_all_location_name = MagicMock(return_value = ['Thailand'])

        location = Location('NASDAQ')
        location.fetch_location('AAPL')
        Location.extract_lat_lon.assert_called_once_with('Bangkok')
        Location.insert_location.assert_called_once_with('Bangkok',{'lat':30,'lon':20})
        Location.insert_many_location.assert_called_once_with(1,3,1)

    def test_fetch_location_has_location_no_relation(self):
        Location.get_all_process_news_id = MagicMock(return_value = [1,2])
        Location.get_all_location_name = MagicMock(return_value = ['Bangkok'])
        Location.check_locate_relation = MagicMock(return_value = False)

        location = Location('NASDAQ')
        location.fetch_location('AAPL')
        Location.extract_lat_lon.assert_not_called()
        Location.insert_location.assert_not_called()
        Location.insert_many_location.assert_called_once_with(1,3,1)

    def test_fetch_location_has_relation(self):
        Location.get_all_process_news_id = MagicMock(return_value = [1,2])
        Location.get_all_location_name = MagicMock(return_value = ['Bangkok'])
        Location.check_locate_relation = MagicMock(return_value = True)

        location = Location('NASDAQ')
        location.fetch_location('AAPL')
        Location.extract_lat_lon.assert_not_called()
        Location.insert_location.assert_not_called()
        Location.insert_many_location.assert_not_called()

    def test_fetch_location_processed_all_news(self):
        Location.get_all_process_news_id = MagicMock(return_value = [1,2,3])
        Location.get_all_location_name = MagicMock(return_value = ['Bangkok'])
        Location.check_locate_relation = MagicMock()

        location = Location('NASDAQ')
        location.fetch_location('AAPL')
        News.combine_translate.assert_not_called()
        Location.location.assert_not_called()
        Location.get_all_location_name.assert_not_called()
        Location.get_location_id.assert_not_called()
        Location.check_locate_relation.assert_not_called()
        Location.extract_lat_lon.assert_not_called()
        Location.insert_location.assert_not_called()
        Location.insert_many_location.assert_not_called()

if __name__ == '__main__':
    unittest.main()
