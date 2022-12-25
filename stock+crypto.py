from sqlite3 import connect
import yfinance as yf
from datetime import datetime


def get_stock_and_crypto_data(name,start,end,interval):
    start = datetime.strptime(start, '%Y-%m-%d')# convert string to datetime obj
    end = datetime.strptime(end, '%Y-%m-%d')# convert string to datetime obj
    data = yf.download(tickers=name, start=start, end=end , interval = interval) #get data
    data = data.loc[data["Volume"] != 0 ].drop(["Adj Close"],axis = 1)# ไม่เอาค่า volume = 0
    data["Date"] = data.index.strftime('%Y-%m-%d %X') # convert pandas timestamp to string 
    return data.values.tolist() #return value in type list

def insert_stock(name,data):
    conn = connect('stock.db',timeout=10)#connect to database
    cursor = conn.cursor()
    for i in data:#run sql script(insert)
        cursor.execute(f"INSERT INTO stock VALUES ('{name.upper()}','{i[5]}',{i[0]},{i[1]},{i[2]},{i[3]},{i[4]})")
    conn.commit()#commit change to db
    conn.close()#disconnect

def get_stock(name):
    conn = connect('stock.db',timeout=10)#connect to database
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM stock WHERE name='{name.upper()}'")#run sql script(get data)
    data = cursor.fetchall()#get data as list
    conn.close()#disconnect
    return data