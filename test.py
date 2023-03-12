from data.function import Stock,Categories,News,Location
import unittest
from unittest.mock import MagicMock,call,patch
import sqlite3
import requests


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

    def test_case_insensitivity(self):
        industry = Categories("SET")
        result = industry.get_industry_id('fincial')
        self.assertEqual(result, 3)

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

    def test_case_insensitivity(self):
        sector = Categories("SET")
        result = sector.get_sector_id('home')
        self.assertEqual(result, 3)

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

        Categories.get_all_stock.reset_mock()
        sqlite3.connect.reset_mock()
        mock_conn.reset_mock()
        mock_cursor.reset_mock()

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

        Categories.get_all_stock.reset_mock()
        Stock.get_stock_id.reset_mock()
        Stock.table.reset_mock()
        sqlite3.connect.reset_mock()
        mock_conn.reset_mock()
        mock_cursor.reset_mock()
    
    def test_table(self):
        Categories.get_all_stock = MagicMock(return_value = ["AOT","PTT","TRUE"])
        aot = Stock("AOT","SET")
        with self.assertRaises(ValueError) as error:
            aot.table("30m")
        self.assertEqual(str(error.exception),"The interval 30m is not available. The available interval are 1h,1d")
        self.assertEqual(aot.table("1d"),'stock_price_day')
        self.assertEqual(aot.table("1h"),'stock_price_hour')

        Categories.get_all_stock.reset_mock()

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

        Categories.get_all_stock.reset_mock()
        Stock.get_stock_id.reset_mock()
        Stock.table.reset_mock()
        sqlite3.connect.reset_mock()
        mock_conn.reset_mock()
        mock_cursor.reset_mock()
    
    def test_insert_stock(self):
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
        
        Categories.get_all_stock.reset_mock()
        Stock.get_stock_id.reset_mock()
        Stock.table.reset_mock()
        sqlite3.connect.reset_mock()
        mock_conn.reset_mock()
        mock_cursor.reset_mock()










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


if __name__ == '__main__':
    unittest.main()
