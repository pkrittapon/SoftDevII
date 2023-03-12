from data.function import Stock,Categories,News,Location
import unittest
from unittest.mock import MagicMock,call
import sqlite3
import requests
from googletrans import Translator


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
        sqlite3.connect = self.original_connect

    def test_valid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_sector_in_industrial('AGRO')
        self.assertEqual(result,['AGRI','FOOD'])
    
    def test_invalid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_sector_in_industrial('INDUS')
        self.assertEqual(result,[])

    def test_case_sensitive(self):
        obj = Categories('SET')
        result = obj.get_all_sector_in_industrial('service')
        self.assertEqual(result,['COMM','HELTH','TRANS'])

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
        sqlite3.connect = self.original_connect

    def test_valid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_industrial('AGRO')
        self.assertEqual(result,['EE','GFPT'])
    
    def test_invalid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_industrial('INDUS')
        self.assertEqual(result,[])

    def test_case_sensitive(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_industrial('service')
        self.assertEqual(result,['COM7','CPALL','HMPRO'])

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
        sqlite3.connect = self.original_connect

    def test_valid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_sector('AGRI')
        self.assertEqual(result,['EE','GFPT'])
    
    def test_invalid_symbol(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_sector('FOOD')
        self.assertEqual(result,[])

    def test_case_sensitive(self):
        obj = Categories('SET')
        result = obj.get_all_stock_in_sector('comm')
        self.assertEqual(result,['COM7','CPALL','HMPRO'])





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
        sqlite3.connect = self.original_connect
        
    def test_data_price_day(self):
        stock = Stock('EE','SET')
        result = stock.get_stock_price(interval = '1d')
        self.assertEqual(result,13.7)

    def test_data_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.get_stock_price(interval = '1h')
        self.assertEqual(result,20.2)

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
        sqlite3.connect = self.original_connect
        
    def test_data_price_day(self):
        stock = Stock('EE','SET')
        result = stock.get_percent_change(interval = '1d')
        self.assertEqual(result,-50)

    def test_data_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.get_percent_change(interval = '1h')
        self.assertEqual(result,100)

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
        sqlite3.connect = self.original_connect
        
    def test_price_day(self):
        stock = Stock('EE','SET')
        result = stock.get_all_datetime(interval = '1d')
        self.assertEqual(result,['2022-10-2 00:00:00','2022-10-3 00:00:00','2022-10-4 00:00:00'])

    def test_price_hour(self):
        stock = Stock('EE','SET')
        result = stock.get_all_datetime(interval = '1h')
        self.assertEqual(result,['2022-10-4 10:00:00','2022-10-4 11:00:00','2022-10-4 12:00:00'])

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
        
    def test_insert(self):
        stock = Stock('EE','SET')
        stock.insert_set_fin(1,['2556Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02,12.64,2.61,5.8,6.12,931153.68,8.9,1.54,3.99])

        self.cursor.execute("SELECT * FROM set_financial_statement")
        result = self.cursor.fetchone()
        self.assertEqual(result,(1,1,'2556Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02,12.64,2.61,5.8,6.12,931153.68,8.9,1.54,3.99))
  
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
        sqlite3.connect = self.original_connect
        
    def test_get_quarter(self):
        stock = Stock('EE','SET')
        result = stock.get_quarter_fin()
        self.assertEqual(result,self.quarter)

class TestFetchFinancial(unittest.TestCase):
    def setUp(self):
        Stock.get_stock_id = MagicMock(return_value = 1)
        Stock.fetch_set_fin = MagicMock(return_value = [['2556Q1'],['2556Q2'],['2560Q1']])
        Stock.insert_set_fin = MagicMock()

    def tearDown(self):
        Stock.get_stock_id.reset_mock()
        Stock.fetch_set_fin.reset_mock()
        Stock.get_quarter_fin.reset_mock()
        Stock.insert_set_fin.reset_mock()

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
        self.cursor.execute("INSERT INTO set_financial_statement VALUES (null,1,'2555Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02,12.64,2.61,5.8,6.12,931153.68,8.9,1.54,3.99)")
        self.conn.commit()
        self.original_connect = sqlite3.connect
        Stock.get_stock_id = MagicMock(return_value = 1)
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
        Stock.get_stock_id.reset_mock()
        sqlite3.connect = self.original_connect
        
    def test_get_fin(self):
        stock = Stock('EE','SET')
        result = stock.financial_statement()
        self.assertEqual(result,[(1,1,'2555Q1',1663096.93,910651.25,752445.69,28563.0,703512.92,43064.02,12.64,2.61,5.8,6.12,931153.68,8.9,1.54,3.99)])

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
        sqlite3.connect = self.original_connect
        
    def test_dup(self):
        value = [(10,11,12,13,1000,'2022-10-2 00:00:00'), (10,11,12,13,2000,'2022-10-5 00:00:00'), (10,11,12,13,3000,'2022-10-6 00:00:00')]
        stock = Stock('EE','SET')
        stock.insert_stock(value,'1d')

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
        stock.insert_stock(value,'1d')

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
        stock.insert_stock(value,'1d')

        self.cursor.execute("SELECT * FROM stock_price_day")
        result = self.cursor.fetchall()
        self.assertEqual(result,[(1,1,'2022-10-2 00:00:00',10,11,12,13,1000), 
                                 (2,1,'2022-10-3 00:00:00',10,11,12,13,2000), 
                                 (3,1,'2022-10-4 00:00:00',10,11,12,13,3000)])    

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
        sqlite3.connect = self.original_connect
        
    def test_get_news(self):
        stock = Stock('EE','SET')
        result = stock.get_all_news()
        self.assertEqual(result,self.news)

class TestGetStockLocation(unittest.TestCase):
    def setUp(self):
        Stock.get_stock_id = MagicMock(return_value = 1)
        self.location = [("2022-02-03","Thailand",10,10),("2022-02-02","Bangkok",8,8)]
        self.mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=self.mock_conn)
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.mock_cursor.fetchall.return_value = self.location

    def tearDown(self):
        Stock.get_stock_id.reset_mock()
        sqlite3.connect.reset_mock()

    def test_get_location(self):
        stock = Stock('EE','SET')
        result = stock.get_stock_location()
        self.assertEqual(result,self.location)
        self.mock_cursor.execute.assert_called_once_with("SELECT c.[datetime],a.location_name, a.lat, a.lon FROM location AS a INNER JOIN set_location AS b ON a.location_id = b.location_id INNER JOIN set_news AS c ON b.news_id = c.news_id WHERE b.stock_id = 1 AND c.[datetime] >= '' ORDER BY c.[datetime] DESC")





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

    def test_yahoo_new_dict(self):
        News.nasdaq_content_time = MagicMock(return_value = {'content':'test','datetime':'2022-02-02 00:00:00'})
        news = News('NASDAQ')
        result = news.nasdaq_news_dict([{'link':'www.yahoo.com','title':'yahoo'}],'AAPL')
        self.assertEqual(result,[{'content':'test','datetime':'2022-02-02 00:00:00','stock':'AAPL','link':'www.yahoo.com','title':'yahoo'}])
        News.nasdaq_content_time.reset_mock()

    def test_insert_news(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        news = News("NASDAQ")
        news.insert_news({'title':'yahoo','datetime':'2020-10-10','link':'https://finance.yahoo.com','content':'TestYahoo12345'})
        mock_cursor.execute.assert_called_once_with('INSERT INTO nasdaq_news VALUES (null,?,?,?,?)', ('yahoo', '2020-10-10', 'https://finance.yahoo.com', 'TestYahoo12345'))

    def test_get_news_id(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)]

        news = News("NASDAQ")
        result = news.get_news_id('aaaa')
        self.assertEqual(result,1)
        mock_cursor.execute.assert_called_once_with("SELECT news_id FROM nasdaq_news WHERE title = ?",('aaaa',))

    def test_check_relation_have_relation(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]

        news = News("NASDAQ")
        result = news.check_relation(1,2)
        self.assertEqual(result,True)
        mock_cursor.execute.assert_called_once_with("SELECT news_id FROM many_nasdaq_news WHERE stock_id = 1")

    def test_check_relation_have_no_relation(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]

        news = News("NASDAQ")
        result = news.check_relation(1,4)
        self.assertEqual(result,False)
        mock_cursor.execute.assert_called_once_with("SELECT news_id FROM many_nasdaq_news WHERE stock_id = 1")

    def test_get_all_title(self):
        expect_result = ["news1","news2","news3"]
        mock_news = [(symbol,) for symbol in expect_result]
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_news

        news = News("NASDAQ")
        result = news.get_all_title()
        self.assertEqual(result,expect_result)
        mock_cursor.execute.assert_called_once_with("SELECT title FROM nasdaq_news")
    
    def test_get_title_content(self):
        expect_result = [("news1","ssss")]
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = expect_result

        news = News("NASDAQ")
        result = news.get_title_content(1)
        self.assertEqual(result,expect_result[0])
        mock_cursor.execute.assert_called_once_with("SELECT title,content FROM nasdaq_news WHERE news_id = 1")

    def test_insert_many_news(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        news = News("NASDAQ")
        news.insert_many_news(1,2)
        mock_cursor.execute.assert_called_once_with("INSERT INTO many_nasdaq_news VALUES (1,2)")

    def test_insert_check_data_have_news_but_no_relation(self):
        News.get_all_title = MagicMock(return_value = ['yahoo','set'])
        News.get_stock_id = MagicMock(return_value = 1)
        News.get_news_id = MagicMock(return_value = 1)
        News.check_relation = MagicMock(return_value = False)
        News.insert_many_news = MagicMock()
        News.insert_news = MagicMock()

        news = News("NASDAQ")
        news.insert_check_data({'content':'test','datetime':'2022-02-02 00:00:00','stock':'AAPL','link':'www.yahoo.com','title':'yahoo'})

        News.insert_many_news.assert_called_once()
        News.insert_news.assert_not_called()

        News.get_all_title.reset_mock()
        News.get_stock_id.reset_mock()
        News.get_news_id.reset_mock()
        News.check_relation.reset_mock()
        News.insert_many_news.reset_mock()
        News.insert_news.reset_mock()

    def test_insert_check_data_have_news_and_relation(self):
        News.get_all_title = MagicMock(return_value = ['yahoo','set'])
        News.get_stock_id = MagicMock(return_value = 1)
        News.get_news_id = MagicMock(return_value = 1)
        News.check_relation = MagicMock(return_value = True)
        News.insert_many_news = MagicMock()
        News.insert_news = MagicMock()

        news = News("NASDAQ")
        news.insert_check_data({'content':'test','datetime':'2022-02-02 00:00:00','stock':'AAPL','link':'www.yahoo.com','title':'yahoo'})
        
        News.insert_many_news.assert_not_called()
        News.insert_news.assert_not_called()

        News.get_all_title.reset_mock()
        News.get_stock_id.reset_mock()
        News.get_news_id.reset_mock()
        News.check_relation.reset_mock()
        News.insert_many_news.reset_mock()
        News.insert_news.reset_mock()

    def test_insert_check_data_do_not_have_news(self):
        News.get_all_title = MagicMock(return_value = ['yahoo','set'])
        News.get_stock_id = MagicMock(return_value = 1)
        News.get_news_id = MagicMock(return_value = 1)
        News.check_relation = MagicMock(return_value = False)
        News.insert_many_news = MagicMock()
        News.insert_news = MagicMock()

        news = News("NASDAQ")
        news.insert_check_data({'content':'test','datetime':'2022-02-02 00:00:00','stock':'AAPL','link':'www.yahoo.com','title':'news'})

        News.insert_many_news.assert_called_once()
        News.insert_news.assert_called_once()

        News.get_all_title.reset_mock()
        News.get_stock_id.reset_mock()
        News.get_news_id.reset_mock()
        News.check_relation.reset_mock()
        News.insert_many_news.reset_mock()
        News.insert_news.reset_mock()

    def test_fetch_yahoo_news_have_tag(self):
        News.nasdaq_get_all_tags = MagicMock(return_value = ['<li class="js-stream-content Pos(r)">xxxxx</li>','<li class="js-stream-content Pos(r)">yyyyy</li>'])
        News.nasdaq_title_link = MagicMock()
        News.nasdaq_news_dict = MagicMock(return_value = [{},{},{},{}])
        News.insert_check_data = MagicMock()

        news = News('NASDAQ')
        news.fetch_nasdaq_news('AAPL')
        News.nasdaq_get_all_tags.assert_called_once()
        News.nasdaq_title_link.assert_called_once()
        News.nasdaq_news_dict.assert_called_once()
        self.assertEqual(News.insert_check_data.call_count,4)

        News.nasdaq_get_all_tags.reset_mock()
        News.nasdaq_title_link.reset_mock()
        News.nasdaq_news_dict.reset_mock()
        News.insert_check_data.reset_mock()

    def test_fetch_yahoo_news_no_tag(self):
        News.nasdaq_get_all_tags = MagicMock()
        News.nasdaq_title_link = MagicMock()
        News.nasdaq_news_dict = MagicMock(return_value = [{},{},{},{}])
        News.insert_check_data = MagicMock()

        news = News('NASDAQ')
        result = news.fetch_nasdaq_news('AAPL')
        News.nasdaq_get_all_tags.assert_called_once()
        News.nasdaq_title_link.assert_not_called()
        News.nasdaq_news_dict.assert_not_called()
        self.assertEqual(result,None)

        News.nasdaq_get_all_tags.reset_mock()
        News.nasdaq_title_link.reset_mock()
        News.nasdaq_news_dict.reset_mock()
        News.insert_check_data.reset_mock()

    def test_fetch_news(self):
        News.fetch_nasdaq_news = MagicMock()

        news = News('NASDAQ')
        news.fetch_news('AAPL')
        News.fetch_nasdaq_news.assert_called_once_with('AAPL')

        News.fetch_nasdaq_news.reset_mock()

    def test_detect_true(self):
        mock_obj = MagicMock()
        Translator.detect = MagicMock(return_value = mock_obj)
        mock_obj.lang = 'en'

        news = News('NASDAQ')
        result = news.detect('Hello world')
        self.assertEqual(result,True)

        Translator.detect.reset_mock()

    def test_detect_false(self):
        mock_obj = MagicMock()
        Translator.detect = MagicMock(return_value = mock_obj)
        mock_obj.lang = 'th'

        news = News('NASDAQ')
        result = news.detect('Hello world')
        self.assertEqual(result,False)

        Translator.detect.reset_mock()

    def test_translate_text_thai(self):
        News.detect = MagicMock(return_value = False)
        mock_obj = MagicMock()
        Translator.translate = MagicMock(return_value = mock_obj)
        mock_obj.text = 'Hello world'

        news = News('NASDAQ')
        result = news.translate_text('สวัสดีโลก')
        self.assertEqual(result,'Hello world')

        Translator.translate.reset_mock()

    def test_translate_text_eng(self):
        News.detect = MagicMock(return_value = True)
        mock_obj = MagicMock()
        Translator.translate = MagicMock(return_value = mock_obj)

        news = News('NASDAQ')
        result = news.translate_text('Hello world')
        self.assertEqual(result,'Hello world')
        Translator.translate.assert_not_called()

        Translator.translate.reset_mock()
        News.detect.reset_mock()

    def test_translate_paragraph(self):
        News.detect = MagicMock(return_value = False)
        News.translate_text = MagicMock(return_value = 'translate')

        news = News('NASDAQ')
        result = news.translate_paragraph('ฟหกดฟหกดหฟกา่ด้ฟหา่้ดา\nกหด้เ่กด้เ่ห้กาด่เ้หสาก่ด้\nฟ่้เกด่้เ่หก้ดเส้หสกา่้')
        self.assertEqual(result,'translate translate translate ')

        News.detect.reset_mock()
        News.translate_text.reset_mock()

    def test_combine_translate(self):
        News.get_title_content = MagicMock()
        News.translate_text = MagicMock(return_value = 'translate')
        News.translate_paragraph = MagicMock(return_value = 'abcdefg hijk lmnop')

        news = News('NASDAQ')
        result = news.combine_translate(1)
        self.assertEqual(result,'translate abcdefg hijk lmnop')
        News.get_title_content.assert_called_once_with(1)

        News.get_title_content.reset_mock()
        News.translate_text.reset_mock()
        News.translate_paragraph.reset_mock()



class TestLocation(unittest.TestCase):
    def test_get_location_id(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)]

        location = Location('NASDAQ')
        result = location.get_location_id('Thailand')
        self.assertEqual(result,1)
        mock_cursor.execute.assert_called_once_with("SELECT location_id FROM location WHERE location_name = ?",('Thailand',))

        sqlite3.connect.reset_mock()

    def test_get_lo_latest_datetime(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("2022-02-02 00:00:00",)]

        location = Location('NASDAQ')
        result = location.get_lo_latest_datetime(1)
        self.assertEqual(result,"2022-02-02 00:00:00")
        mock_cursor.execute.assert_called_once_with("SELECT DISTINCT a.[datetime] FROM nasdaq_news AS a INNER JOIN nasdaq_location AS b ON a.news_id = b.news_id WHERE b.stock_id = 1 ORDER BY a.[datetime] DESC LIMIT 1")

        sqlite3.connect.reset_mock()

    def test_get_lo_latest_datetime_none(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        location = Location('NASDAQ')
        result = location.get_lo_latest_datetime(1)
        self.assertEqual(result,None)
        mock_cursor.execute.assert_called_once_with("SELECT DISTINCT a.[datetime] FROM nasdaq_news AS a INNER JOIN nasdaq_location AS b ON a.news_id = b.news_id WHERE b.stock_id = 1 ORDER BY a.[datetime] DESC LIMIT 1")

        sqlite3.connect.reset_mock()

    def test_get_all_location_name(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("Thailand",),("Bangkok",)]

        location = Location('NASDAQ')
        result = location.get_all_location_name()
        self.assertEqual(result,["Thailand","Bangkok"])
        mock_cursor.execute.assert_called_once_with("SELECT location_name FROM location")

        sqlite3.connect.reset_mock()

    def test_check_locate_relation(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,),(2,)]

        location = Location('NASDAQ')
        result = location.check_locate_relation(1,2,3)
        self.assertEqual(result,True)
        mock_cursor.execute.assert_called_once_with("SELECT location_id FROM nasdaq_location WHERE news_id = 2 and stock_id = 3")

        sqlite3.connect.reset_mock()

    def test_insert_location(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        location = Location('NASDAQ')
        location.insert_location('Bangkok',{'lat':10,'lon':11})
        mock_cursor.execute.assert_called_once_with('INSERT INTO location VALUES (null,"Bangkok",10,11)')

        sqlite3.connect.reset_mock()

    def test_insert_many_location(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        location = Location('NASDAQ')
        location.insert_many_location(1,2,3)
        mock_cursor.execute.assert_called_once_with('INSERT INTO nasdaq_location VALUES (1,2,3)')

        sqlite3.connect.reset_mock()

    def test_get_all_stock_news_id_has_old_location(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]
        Location.get_stock_id = MagicMock(return_value=1)
        Location.get_lo_latest_datetime = MagicMock(return_value="2022-02-02")

        location = Location('NASDAQ')
        result = location.get_all_stock_news_id('AAPL')
        self.assertEqual(result,[1,2,3])
        mock_cursor.execute.assert_called_once_with("SELECT DISTINCT a.news_id FROM many_nasdaq_news AS a INNER JOIN nasdaq_news AS b ON a.news_id = b.news_id WHERE a.stock_id = 1 AND b.[datetime] > '2022-02-02' ORDER BY b.[datetime] ASC")

        sqlite3.connect.reset_mock()
        Location.get_stock_id.reset_mock()
        Location.get_lo_latest_datetime.reset_mock()

    def test_get_all_stock_news_id_no_old_location(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]
        Location.get_stock_id = MagicMock(return_value=1)
        Location.get_lo_latest_datetime = MagicMock(return_value=None)

        location = Location('NASDAQ')
        result = location.get_all_stock_news_id('AAPL')
        self.assertEqual(result,[1,2,3])
        mock_cursor.execute.assert_called_once_with("SELECT DISTINCT news_id FROM many_nasdaq_news WHERE stock_id = 1")

        sqlite3.connect.reset_mock()
        Location.get_stock_id.reset_mock()
        Location.get_lo_latest_datetime.reset_mock()

    def test_get_all_process_news_id(self):
        mock_conn = MagicMock()
        sqlite3.connect = MagicMock(return_value=mock_conn)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,),(2,),(3,)]
        Location.get_stock_id = MagicMock(return_value=1)
    
        location = Location('NASDAQ')
        result = location.get_all_process_news_id('AAPL')
        self.assertEqual(result,[1,2,3])
        mock_cursor.execute.assert_called_once_with("SELECT DISTINCT news_id FROM nasdaq_location WHERE stock_id = 1")

        sqlite3.connect.reset_mock()
        Location.get_stock_id.reset_mock()

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

    def test_fetch_location_never_has_location(self):
        Location.get_stock_id = MagicMock(return_value = 1)
        Location.get_all_stock_news_id = MagicMock(return_value = [1,2,3])
        Location.get_all_process_news_id = MagicMock(return_value = [1,2])
        Location.get_news_datetime = MagicMock(return_value = '2022-02-02')
        News.combine_translate = MagicMock(return_value = "I live in Bangkok")
        Location.location = MagicMock(return_value = ['Bangkok'])
        Location.get_all_location_name = MagicMock(return_value = ['Thailand'])
        Location.get_location_id = MagicMock(return_value = 1)
        Location.check_locate_relation = MagicMock(return_value = False)
        Location.extract_lat_lon = MagicMock(return_value = {'lat':30,'lon':20})
        Location.insert_many_location = MagicMock()
        Location.insert_location = MagicMock()

        location = Location('NASDAQ')
        location.fetch_location('AAPL')
        Location.extract_lat_lon.assert_called_once_with('Bangkok')
        Location.insert_location.assert_called_once_with('Bangkok',{'lat':30,'lon':20})
        Location.insert_many_location.assert_called_once_with(1,3,1)

        Location.get_stock_id.reset_mock()
        Location.get_all_stock_news_id.reset_mock()
        Location.get_all_process_news_id.reset_mock()
        Location.get_news_datetime.reset_mock()
        News.combine_translate.reset_mock()
        Location.location.reset_mock()
        Location.get_all_location_name.reset_mock()
        Location.get_location_id.reset_mock()
        Location.check_locate_relation.reset_mock()
        Location.extract_lat_lon.reset_mock()
        Location.insert_many_location.reset_mock()
        Location.insert_location.reset_mock()

    def test_fetch_location_has_location_no_relation(self):
        Location.get_stock_id = MagicMock(return_value = 1)
        Location.get_all_stock_news_id = MagicMock(return_value = [1,2,3])
        Location.get_all_process_news_id = MagicMock(return_value = [1,2])
        Location.get_news_datetime = MagicMock(return_value = '2022-02-02')
        News.combine_translate = MagicMock(return_value = "I live in Bangkok")
        Location.location = MagicMock(return_value = ['Bangkok'])
        Location.get_all_location_name = MagicMock(return_value = ['Bangkok'])
        Location.get_location_id = MagicMock(return_value = 1)
        Location.check_locate_relation = MagicMock(return_value = False)
        Location.extract_lat_lon = MagicMock(return_value = {'lat':30,'lon':20})
        Location.insert_many_location = MagicMock()
        Location.insert_location = MagicMock()

        location = Location('NASDAQ')
        location.fetch_location('AAPL')
        Location.extract_lat_lon.assert_not_called()
        Location.insert_location.assert_not_called()
        Location.insert_many_location.assert_called_once_with(1,3,1)

        Location.get_stock_id.reset_mock()
        Location.get_all_stock_news_id.reset_mock()
        Location.get_all_process_news_id.reset_mock()
        Location.get_news_datetime.reset_mock()
        News.combine_translate.reset_mock()
        Location.location.reset_mock()
        Location.get_all_location_name.reset_mock()
        Location.get_location_id.reset_mock()
        Location.check_locate_relation.reset_mock()
        Location.extract_lat_lon.reset_mock()
        Location.insert_many_location.reset_mock()
        Location.insert_location.reset_mock()

    def test_fetch_location_has_relation(self):
        Location.get_stock_id = MagicMock(return_value = 1)
        Location.get_all_stock_news_id = MagicMock(return_value = [1,2,3])
        Location.get_all_process_news_id = MagicMock(return_value = [1,2])
        Location.get_news_datetime = MagicMock(return_value = '2022-02-02')
        News.combine_translate = MagicMock(return_value = "I live in Bangkok")
        Location.location = MagicMock(return_value = ['Bangkok'])
        Location.get_all_location_name = MagicMock(return_value = ['Bangkok'])
        Location.get_location_id = MagicMock(return_value = 1)
        Location.check_locate_relation = MagicMock(return_value = True)
        Location.extract_lat_lon = MagicMock(return_value = {'lat':30,'lon':20})
        Location.insert_many_location = MagicMock()
        Location.insert_location = MagicMock()

        location = Location('NASDAQ')
        location.fetch_location('AAPL')
        Location.extract_lat_lon.assert_not_called()
        Location.insert_location.assert_not_called()
        Location.insert_many_location.assert_not_called()

        Location.get_stock_id.reset_mock()
        Location.get_all_stock_news_id.reset_mock()
        Location.get_all_process_news_id.reset_mock()
        Location.get_news_datetime.reset_mock()
        News.combine_translate.reset_mock()
        Location.location.reset_mock()
        Location.get_all_location_name.reset_mock()
        Location.get_location_id.reset_mock()
        Location.check_locate_relation.reset_mock()
        Location.extract_lat_lon.reset_mock()
        Location.insert_many_location.reset_mock()
        Location.insert_location.reset_mock()

    def test_fetch_location_processed_all_news(self):
        Location.get_stock_id = MagicMock(return_value = 1)
        Location.get_all_stock_news_id = MagicMock(return_value = [1,2,3])
        Location.get_all_process_news_id = MagicMock(return_value = [1,2,3])
        Location.get_news_datetime = MagicMock(return_value = '2022-02-02')
        News.combine_translate = MagicMock(return_value = "I live in Bangkok")
        Location.location = MagicMock(return_value = ['Bangkok'])
        Location.get_all_location_name = MagicMock(return_value = ['Bangkok'])
        Location.get_location_id = MagicMock(return_value = 1)
        Location.check_locate_relation = MagicMock(return_value = True)
        Location.extract_lat_lon = MagicMock(return_value = {'lat':30,'lon':20})
        Location.insert_many_location = MagicMock()
        Location.insert_location = MagicMock()

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

        Location.get_stock_id.reset_mock()
        Location.get_all_stock_news_id.reset_mock()
        Location.get_all_process_news_id.reset_mock()
        Location.get_news_datetime.reset_mock()
        News.combine_translate.reset_mock()
        Location.location.reset_mock()
        Location.get_all_location_name.reset_mock()
        Location.get_location_id.reset_mock()
        Location.check_locate_relation.reset_mock()
        Location.extract_lat_lon.reset_mock()
        Location.insert_many_location.reset_mock()
        Location.insert_location.reset_mock()

if __name__ == '__main__':
    unittest.main()
