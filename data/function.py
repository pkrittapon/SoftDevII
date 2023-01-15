import sqlite3
import datetime
import yfinance as yf
import pandas as pd

class Categories:
    def get_index_id(self,symbol):
        """return index id"""
        symbol = symbol.upper()
        if not symbol in self.get_all_index():
            raise ValueError(f"{symbol} is not in index")        
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT index_id FROM [index] WHERE symbol = '{symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def get_industry_id(self,symbol):
        """return industry id"""
        symbol = symbol.upper()
        if not symbol in self.get_all_industry():
            raise ValueError(f"{symbol} is not in industry")       
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT industry_id FROM industry WHERE symbol = '{symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]
    
    def get_sector_id(self,symbol):
        """return sector id""" 
        symbol = symbol.upper()
        if not symbol in self.get_all_sector():
            raise ValueError(f"{symbol} is not in sector")          
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT sector_id FROM sector WHERE symbol = '{symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def insert_stock(self,stock,index,industry,sector):
        """insert new stock to database"""
        index_id = self.get_index_id(index)
        industry_id = self.get_industry_id(industry)
        sector_id = self.get_sector_id(sector)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO stock (symbol,index_id,industry_id,sector_id) VALUES ('{stock.upper()}',{index_id},{industry_id},{sector_id})")
        conn.commit()
        conn.close()
        return f"{stock} has been added"

    def get_all_stock(self):
        """return list of symbol of stock"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM stock")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_index(self):
        """return list of all industry"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM [index]")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_industry(self):
        """return list of all industry"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM industry")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_sector(self):
        """return list of all sector symbol"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM sector")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_sector_in_industrial(self,symbol):
        """return list of all sector symbol that is in the input industry symbol"""
        id = self.get_industry_id(symbol)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM sector WHERE industry_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_stock_in_industrial(self,symbol):
        """return list of all stock symbol that is in the input industry symbol"""
        id = self.get_industry_id(symbol)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM stock WHERE industry_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_stock_in_sector(self,symbol):
        """return list of all stock symbol that is in the input sector symbol"""
        id = self.get_sector_id(symbol)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM stock WHERE sector_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_set100(self):
        """return list of all stock symbol that is in set100"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT stock.symbol FROM set100 LEFT JOIN stock ON stock.stock_id = set100.stock_id")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

def table(type,interval):
    "return table that is available on database"
    available_type = {'stock':['1h','1d'],'industry':['1h'],'sector':['1h']}
    if not type in list(available_type.keys()): #catch error
        raise ValueError(f"This data is not available. The available are {','.join(list(available_type.keys()))}")
    elif not interval in available_type[type]:
        raise ValueError(f"This interval is not support. The supported interval are {','.join(available_type[type])}")
    else:
        if interval == '1h':
            return f'{type}_price_hour'
        elif interval == '1d':
            return f'{type}_price_day'


class Stock:

    def __init__(self,symbol):
        symbol = symbol.upper()
        if not symbol in Categories().get_all_stock():
            raise ValueError(f"{symbol} is not available")
        self.symbol = symbol

    def get_stock_id(self):
        """return id of stock"""       
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT stock_id FROM stock WHERE symbol = '{self.symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def delete(self):
        "delete stock from database"
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM stock WHERE symbol = '{self.symbol}'")
        conn.commit()
        conn.close()
        return f"{self.symbol} has been deleted"

    def table(self,interval):
        "return table that is available on database"
        available_interval = ['1h','1d']
        if not interval in available_interval:
            raise ValueError(f"The interval {interval} is not available. The available interval are {','.join(available_interval)}")
        else:
            if interval == '1h':
                return 'stock_price_hour'
            elif interval == '1d':
                return 'stock_price_day'

    def get_stock_price(self,**kwargs):
        """return the latest price of stock"""
        interval = kwargs.get('interval','1h')
        id = self.get_stock_id()
        table = self.table(interval)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT close FROM {table} WHERE stock_id = {id} order by [datetime] desc limit 1")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def latest_update_time(self, **kwargs):
        """return the latest update time of stock"""
        interval = kwargs.get('interval','1h')
        id = self.get_stock_id()
        table = self.table(interval)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT max([datetime]) from {table} WHERE stock_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def oldest_update_time(self,**kwargs):
        """return the oldest update time of stock"""
        interval = kwargs.get('interval','1h')
        id = self.get_stock_id()
        table = self.table(interval)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT min([datetime]) from {table} WHERE stock_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def get_all_datetime(self,**kwargs):
        interval = kwargs.get('interval','1h')
        id = self.get_stock_id()
        table = self.table(interval)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT [datetime] from {table} WHERE stock_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_stock_price(self,**kwargs):
        """return all stock price between the interval"""
        interval = kwargs.get('interval','1h')
        start = kwargs.get('start',self.oldest_update_time(interval=interval))
        end = kwargs.get('end',self.latest_update_time(interval=interval))
        id = self.get_stock_id()
        table = self.table(interval)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT [datetime],open,high,low,close,volume FROM {table} WHERE [datetime] BETWEEN '{start}' AND '{end}' AND stock_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return data

    def sector(self):
        """return the sector of this stock"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT sector.symbol FROM stock LEFT JOIN sector ON stock.sector_id = sector.sector_id WHERE stock.symbol = '{self.symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def industry(self):
        """return the industry of this stock"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT industry.symbol FROM stock LEFT JOIN industry ON stock.industry_id = industry.industry_id WHERE stock.symbol = '{self.symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def get_stock_and_crypto_data(self,name,start,interval):
        """return list of data of this stock from yahoo finance"""
        start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')# convert string to datetime obj
        if interval == '1h':
            interval = '30m'
        # if interval == '1d':
        #     start = start + datetime.timedelta(days=1)
        # elif interval == '1h':
        #     interval = '30m'
        #     start = start + datetime.timedelta(hours=1)
        data = yf.download(tickers=name, start=start, interval = interval)
        data = data.loc[data["Volume"] != 0 ].drop(["Adj Close"],axis = 1)
        new_data_open = data['Open'].resample("H").first()
        new_data_close = data['Close'].resample("H").last()
        new_data_high = data['High'].resample("H").max()
        new_data_low = data['Low'].resample("H").min()
        new_data_volume = data['Volume'].resample("H").sum()
        new_data = pd.DataFrame({'Open': new_data_open,
                                        'High': new_data_high,
                                        'Low': new_data_low,
                                        'Close': new_data_close,
                                        'Volume': new_data_volume}).dropna()
        new_data["Date"] = new_data.index.strftime('%Y-%m-%d %X') # convert pandas timestamp to string 
        return new_data.values.tolist() #return value in type list

    def insert_stock(self,data,interval):
        """insert data to table in database"""
        id = self.get_stock_id()
        date = self.get_all_datetime(interval = interval)
        table = self.table(interval)
        conn = sqlite3.connect('stock.db',timeout=10)#connect to database
        cursor = conn.cursor()
        for i in data:
            if i[5] in date:
                continue
            else:
                cursor.execute(f"INSERT INTO {table} VALUES (null,{id},'{i[5]}',{i[0]},{i[1]},{i[2]},{i[3]},{i[4]})")#run sql script(insert)
        conn.commit()#commit change to db
        conn.close()#disconnect

    def fetch_stock_price(self,interval):
        """fetch latest price of stock"""
        available_interval = ['1h','1d']
        if not interval in available_interval:
            raise ValueError(f"The interval {interval} is not available. The available interval are {','.join(available_interval)}")
        date = self.latest_update_time(interval=interval)
        try:
            self.insert_stock(self.get_stock_and_crypto_data(self.symbol+'.bk',date,interval),interval)
        except (AttributeError, TypeError) as e:
            return f"Cannot fetch {self.symbol} price in {interval} interval"


# class Sector:

#     def __init__(self,symbol):
#         self.symbol = symbol

#     def get_price(self):
        
#         conn = sqlite3.connect('stock.db',timeout=10)
#         cursor = conn.cursor()
#         cursor.execute(f"SELECT close FROM sector_price WHERE sector = '{self.symbol.upper()}' order by [datetime] desc limit 1")
#         data = cursor.fetchall()
#         conn.close()
#         return data[0][0]

#     def latest_update_time(self):
       
#         conn = sqlite3.connect('stock.db',timeout=10)
#         cursor = conn.cursor()
#         cursor.execute(f"SELECT DISTINCT max([datetime]) from sector_price WHERE sector = '{self.symbol.upper()}'")
#         data = cursor.fetchall()
#         conn.close()
#         return data[0][0]

#     def oldest_update_time(self):
        
#         conn = sqlite3.connect('stock.db',timeout=10)
#         cursor = conn.cursor()
#         cursor.execute(f"SELECT DISTINCT min([datetime]) from sector_price WHERE sector = '{self.symbol.upper()}'")
#         data = cursor.fetchall()
#         conn.close()
#         return data[0][0]

#     def get_all_price(self, **kwargs):
        
#         start = kwargs.get('start',None)
#         end = kwargs.get('end',None)
#         conn = sqlite3.connect('stock.db',timeout=10)
#         cursor = conn.cursor()
#         if start != None and end != None:
#             cursor.execute(f"SELECT [datetime],open,high,low,close FROM sector_price where [datetime] BETWEEN '{start}' AND '{end}' AND sector = '{self.symbol.upper()}'")
#         elif start != None:
#             cursor.execute(f"SELECT [datetime],open,high,low,close FROM sector_price where [datetime] > '{start}'  AND sector = '{self.symbol.upper()}'")
#         elif end != None:
#             cursor.execute(f"SELECT [datetime],open,high,low,close FROM sector_price where [datetime] < '{end}'  AND sector = '{self.symbol.upper()}'")
#         else:
#             cursor.execute(f"SELECT [datetime],open,high,low,close FROM sector_price WHERE sector = '{self.symbol.upper()}' ORDER by [datetime]")
#         data = cursor.fetchall()
#         conn.close()
#         return data


# class Industrial:

#     def __init__(self,symbol):
#         self.symbol = symbol

#     def get_price(self):
       
#         conn = sqlite3.connect('stock.db',timeout=10)
#         cursor = conn.cursor()
#         cursor.execute(f"SELECT close FROM industrial_price WHERE industrial = '{self.symbol.upper()}' order by [datetime] desc limit 1")
#         data = cursor.fetchall()
#         conn.close()
#         return data[0][0]

#     def latest_update_time(self):
        
#         conn = sqlite3.connect('stock.db',timeout=10)
#         cursor = conn.cursor()
#         cursor.execute(f"SELECT DISTINCT max([datetime]) from industrial_price WHERE industrial = '{self.symbol.upper()}'")
#         data = cursor.fetchall()
#         conn.close()
#         return data[0][0]

#     def oldest_update_time(self):
       
#         conn = sqlite3.connect('stock.db',timeout=10)
#         cursor = conn.cursor()
#         cursor.execute(f"SELECT DISTINCT min([datetime]) from industrial_price WHERE industrial = '{self.symbol.upper()}'")
#         data = cursor.fetchall()
#         conn.close()
#         return data[0][0]

#     def get_all_price(self, **kwargs):
       
#         start = kwargs.get('start',None)
#         end = kwargs.get('end',None)
#         conn = sqlite3.connect('stock.db',timeout=10)
#         cursor = conn.cursor()
#         if start != None and end != None:
#             cursor.execute(f"SELECT [datetime],open,high,low,close FROM industrial_price where [datetime] BETWEEN '{start}' AND '{end}' AND industrial = '{self.symbol.upper()}'")
#         elif start != None:
#             cursor.execute(f"SELECT [datetime],open,high,low,close FROM industrial_price where [datetime] > '{start}'  AND industrial = '{self.symbol.upper()}'")
#         elif end != None:
#             cursor.execute(f"SELECT [datetime],open,high,low,close FROM industrial_price where [datetime] < '{end}'  AND industrial = '{self.symbol.upper()}'")
#         else:
#             cursor.execute(f"SELECT [datetime],open,high,low,close FROM industrial_price WHERE industrial = '{self.symbol.upper()}' ORDER by [datetime]")
#         data = cursor.fetchall()
#         conn.close()
#         return data    