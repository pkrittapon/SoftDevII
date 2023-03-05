from .function import Stock,Categories
import yfinance as yf
import datetime
from sqlite3 import connect

class FetchStock:

    def get_stock_and_crypto_data(self,name,start,interval):
        start_unix = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')# convert string to datetime obj
        # if interval == '1d':
        start_unix = start_unix + datetime.timedelta(days=1)
        # elif interval == '1h':
        #     start_unix = start + datetime.timedelta(hours=1)
        data = yf.download(tickers=name, start=start_unix, interval = interval) #get data
        print(data)
        data = data.loc[data["Volume"] != 0 ].drop(["Adj Close"],axis = 1)# ไม่เอาค่า volume = 0
        data["Date"] = data.index.strftime('%Y-%m-%d %X') # convert pandas timestamp to string 
        return data.values.tolist() #return value in type list

    def insert_stock(self,id,data,table):
        conn = connect('stock.db',timeout=10)#connect to database
        cursor = conn.cursor()
        for i in data:#run sql script(insert)
            cursor.execute(f"INSERT INTO {table} VALUES (null,{id},'{i[5]}',{i[0]},{i[1]},{i[2]},{i[3]},{i[4]})")
        conn.commit()#commit change to db
        conn.close()#disconnect


    def fetch_stock_price(self,interval):
        support = ['1h','1d']
        if not interval in support:
            return None
        for symbol in Categories().get_all_stock():
            stock = Stock(symbol)
            table = stock.table(interval)
            date = stock.latest_update_time(interval=interval)
            try:
                self.insert_stock(stock.get_stock_id(),self.get_stock_and_crypto_data(symbol+'.bk',date,interval),table)
            except (AttributeError, TypeError) as e:
                continue
