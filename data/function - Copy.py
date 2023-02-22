import sqlite3
import datetime
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import spacy

class Categories:
    def __init__(self,index):
        index = index.upper()
        if index == 'SET':
            self.basetable = 'stock'
            self.type = 'stock'
        if index == 'NASDAQ':
            self.basetable = 'stock_nasdaq'
            self.type = 'stock'
        if index == 'CRYPTO':
            self.basetable = 'crypto'
            self.type = 'crypto'

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
        cursor.execute(f"INSERT INTO {self.basetable} (symbol,index_id,industry_id,sector_id) VALUES ('{stock.upper()}',{index_id},{industry_id},{sector_id})")
        conn.commit()
        conn.close()
        return f"{stock} has been added"

    def get_all_stock(self):
        """return list of symbol of stock"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM {self.basetable}")
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
        cursor.execute(f"SELECT symbol FROM {self.basetable} WHERE industry_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_stock_in_sector(self,symbol):
        """return list of all stock symbol that is in the input sector symbol"""
        id = self.get_sector_id(symbol)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM {self.basetable} WHERE sector_id = {id}")
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

    def __init__(self,symbol,index):
        symbol = symbol.upper()
        index = index.upper()
        
        if index == 'SET':
            self.basetable = 'stock'
            self.type = 'stock'
            self.price = '.bk'
        if index == 'NASDAQ':
            self.basetable = 'stock_nasdaq'
            self.type = 'stock'
            self.price = ''
        if index == 'CRYPTO':
            self.basetable = 'crypto'
            self.type = 'crypto'
            self.price = '-USD'
        self.symbol = symbol
    
    def insert_new_stock(self,stock):
        """insert new stock to database"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO stock (symbol) VALUES ('{stock.upper()}')")
        conn.commit()
        conn.close()


    def get_stock_id(self):
        """return id of stock"""       
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT {self.type}_id FROM {self.basetable} WHERE symbol = '{self.symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def delete(self):
        "delete stock from database"
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {self.basetable} WHERE symbol = '{self.symbol}'")
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
                return f'{self.basetable}_price_hour'
            elif interval == '1d':
                return f'{self.basetable}_price_day'

    def get_stock_price(self,**kwargs):
        """return the latest price of stock"""
        interval = kwargs.get('interval','1h')
        id = self.get_stock_id()
        table = self.table(interval)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT close FROM {table} WHERE {self.type}_id = {id} order by [datetime] desc limit 1")
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
        cursor.execute(f"SELECT DISTINCT max([datetime]) from {table} WHERE {self.type}_id = {id}")
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
        cursor.execute(f"SELECT DISTINCT min([datetime]) from {table} WHERE {self.type}_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def get_all_datetime(self,**kwargs):
        interval = kwargs.get('interval','1h')
        id = self.get_stock_id()
        table = self.table(interval)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT [datetime] from {table} WHERE {self.type}_id = {id}")
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
        cursor.execute(f"SELECT [datetime],open,high,low,close,volume FROM {table} WHERE [datetime] BETWEEN '{start}' AND '{end}' AND {self.type}_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return data

    def sector(self):
        """return the sector of this stock"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT sector.symbol FROM {self.basetable} LEFT JOIN sector ON {self.basetable}.sector_id = sector.sector_id WHERE {self.basetable}.symbol = '{self.symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def industry(self):
        """return the industry of this stock"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT industry.symbol FROM {self.basetable} LEFT JOIN industry ON {self.basetable}.industry_id = industry.industry_id WHERE {self.basetable}.symbol = '{self.symbol}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def financial_statement(self):
        """return financial statement of the stock"""
        table = ''
        if self.basetable == 'stock':
            table = 'new_financial_statement'
        elif self.basetable == 'stock_nasdaq':
            table = 'nasdaq_financial_statement'
        else:
            return "Does not contain financial statement"
        id = self.get_stock_id()
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE stock_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return data

    def get_new_stock_data(self,name,interval,period):   
        data = yf.download(tickers=name+self.price, interval = interval,period=period)
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

    def get_stock_and_crypto_data(self,name,start,interval):
        """return list of data of this stock from yahoo finance"""
        if interval == '1h':
            interval = '30m'
        if start == None:
            if interval == '30m':
                data = yf.download(tickers=name, period='60d', interval = interval)
            else:
                data = yf.download(tickers=name, period='730d', interval = interval)
        else:
            start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')# convert string to datetime obj
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
            self.insert_stock(self.get_stock_and_crypto_data(self.symbol+self.price,date,interval),interval)
        except (AttributeError, TypeError) as e:
            return f"Cannot fetch {self.symbol} price in {interval} interval"
        
    def fetch_new_stock_price(self):
        
        price_hour = self.get_new_stock_data(self.symbol,'30m','60d')
        price_day = self.get_new_stock_data(self.symbol,'1d','2y')
        self.insert_new_stock(self.symbol)
        self.insert_stock(price_hour,'1h')
        self.insert_stock(price_day,'1d')
        raise ValueError(f"{self.symbol} is not available")
        
    def get_location(self):
        id = self.get_stock_id()
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT location_name,lat,lon FROM location WHERE stock_id = {id}")
        data = cursor.fetchall()
        conn.close()
        return data
    


class News:

    def __init__(self,index):
        self.baseurl = 'https://finance.yahoo.com'
        if index.upper() == 'SET':
            self.news_table = 'set_news'
            self.relation_table = 'many_set_news'
            self.stock_table = 'stock'
            self.index = index.upper()
        elif index.upper() == 'NASDAQ':
            self.news_table = 'nasdaq_news'
            self.relation_table = 'many_nasdaq_news'
            self.stock_table = 'stock_nasdaq'
            self.index = index.upper()
        else:
            raise ValueError('wrong index')


    def set_get_all_tags(self,symbol,page):
        latest = f'https://www.kaohoon.com/tag/{symbol}/page/{page}'
        response = requests.get(latest)
        if response.status_code == 200:
            data = BeautifulSoup(response.text,"html.parser")
            news = data.find_all(attrs={"class": "post-item"})
            return news
        return []

    def set_title_link_time(self,tag):
        # .replace('\n','').replace('“',"").replace('”','')
        result = []
        for data in tag:
            time_tag = data.find(attrs={"class": "date meta-item tie-icon"})
            title_tag = data.find(attrs={"class": "post-title"})
            title = title_tag.find('a')
            date = time_tag.text.split('/')
            result.append({'title':title.text,'datetime':f"{date[2]}-{date[1]}-{date[0]} 00:00:00",'link':title["href"]})
        return result

    def set_content(self,link):
        text = ''
        response = requests.get(link)
        if response.status_code == 200:
            data = BeautifulSoup(response.text,"html.parser")
            try:
                news = data.find(attrs={"itemprop": "articleBody"}).find_all('p')
            except AttributeError:
                return 'null'
            for i in news:
                text = text+i.text+'\n'
            if text == '':
                return 'null'
            return text
        return 'null'

    def set_news_dict(self,li,symbol):
        dict_list = []
        for news in li:
            con = self.set_content(news['link'])
            news['stock'] = symbol.upper()
            news['content'] = con
            dict_list.append(news)
        return dict_list
################################################################

    def nasdaq_get_all_tags(self,symbol):
        latest = f'https://finance.yahoo.com/quote/{symbol.upper()}'
        response = requests.get(latest)
        if response.status_code == 200:
            data = BeautifulSoup(response.text,"html.parser")
            tags = data.find_all(attrs={"class": "js-stream-content Pos(r)"})
            return tags
        return 'Server is not response'

    def nasdaq_title_link(self,tag):
        result = []
        for i in tag:
            title = i.find("a")
            link = title['href']
            if 'https' not in link:
                link = 'https://finance.yahoo.com'+link
            result.append({'title':title.text,'link':link})
        return result

    def nasdaq_content_time(self,link):
        content_dict = {}
        content_text = ""
        response = requests.get(link)
        if response.status_code == 200:
            data = BeautifulSoup(response.text,"html.parser")
            try:
                time = data.find('time')
                content = data.find(attrs={"class": "caas-body"}).find_all('p')
                content_text = ""
                for j in content:
                    if '@' in j.text:
                        break
                    content_text += j.text+'\n'
                content_dict['content'] = content_text
                content_dict['datetime'] = time["datetime"].replace('T',' ').replace('.000Z','')
            except AttributeError:      
                content_dict['content'] = "null"
            return content_dict
        content_dict['content'] = "null"
        content_dict['datetime'] = "null"
        return content_dict

    def nasdaq_news_dict(self,li,symbol):
        dict_list = []
        for news in li:
            con = self.nasdaq_content_time(news['link'])
            news['stock'] = symbol.upper()
            news['datetime'] = con['datetime']
            news['content'] = con['content']
            dict_list.append(news)
        return dict_list


##################################################################
    def insert_news(self,news):
        conn = sqlite3.connect('stock.db',timeout=10)#connect to database
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {self.news_table} VALUES (null,?,?,?,?)", (news['title'],news['datetime'],news['link'],news['content']))
        conn.commit()
        conn.close()

    def get_stock_id(self,symbol):
        """return id of stock"""   
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT stock_id FROM {self.stock_table} WHERE symbol = '{symbol.upper()}'")
        data = cursor.fetchall()
        conn.close()
        if len(data) != 0:
            return data[0][0]
        return None

    def get_news_id(self,title):
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT news_id FROM {self.news_table} WHERE title = ?",(title,))
        data = cursor.fetchall()
        conn.close()
        if len(data) != 0:
            return data[0][0]
        return None

    def check_relation(self,stock_id,news_id):
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT news_id FROM {self.relation_table} WHERE stock_id = {stock_id}")
        data = cursor.fetchall()
        conn.close()
        news = []
        if len(data) != 0:
            news = [i[0] for i in data]
        return news_id in news

    def get_all_title(self):
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT title FROM {self.news_table}")
        data = cursor.fetchall()
        conn.close()
        if len(data) != 0:
            return [i[0] for i in data]
        return []

    def insert_many_news(self,news_id,stock_id):
        conn = sqlite3.connect('stock.db',timeout=10)#connect to database
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {self.relation_table} VALUES ({news_id},{stock_id})")
        conn.commit()
        conn.close()

    def insert_check_data(self,news):
        all_title = self.get_all_title()
        stock_id = self.get_stock_id(news['stock'])
        if news['title'] in all_title:
            news_id = self.get_news_id(news['title'])
            if not self.check_relation(stock_id,news_id):
                self.insert_many_news(news_id,stock_id)
        else:
            self.insert_news(news)
            news_id = self.get_news_id(news['title'])
            self.insert_many_news(news_id,stock_id)
        print('-----------------100%------------------------')

    def fetch_set_news(self,symbol):
        page = 1
        tag = self.set_get_all_tags(symbol,page)
        while(len(tag) != 0 and page < 25):
            dict_list = self.set_title_link_time(tag)
            result = self.set_news_dict(dict_list,symbol)
            for i in result:
                self.insert_check_data(i)
            page += 1
            tag = self.set_get_all_tags(symbol,page)

    def fetch_nasdaq_news(self,symbol):
        tag = self.nasdaq_get_all_tags(symbol)
        if len(tag) == 0:
            return None
        dict_list = self.nasdaq_title_link(tag)
        result = self.nasdaq_news_dict(dict_list,symbol)
        for i in result:
            self.insert_check_data(i)
    
    def fetch_news(self,symbol):
        if self.index == 'SET':
            self.fetch_set_news(symbol)
        elif self.index == 'NASDAQ':
            self.fetch_nasdaq_news(symbol)

    def translate_text(self,text):
        translator = Translator()
        clean_text = text.replace('“',"").replace('”','')
        translated = translator.translate(clean_text).text
        return translated

    def translate_paragraph(self,paragraph):
        array = paragraph.split('\n')
        translated = ''
        for i in array:
            translated += self.translate_text(i)
        return translated
    
    def combine_translate(self,news_id):
        news = self.get_title_content(news_id)
        title = self.translate_text(news[0])
        content = self.translate_paragraph(news[1])
        return title + ' ' + content
    
    
    

class Location:
    def __init__(self,index):
        self.nlp = spacy.load('en_core_web_sm')
        if index.upper() == 'SET':
            self.news_table = 'set_news'
            self.relation_table = 'many_set_news'
            self.stock_table = 'stock'
            self.index = index.upper()
        elif index.upper() == 'NASDAQ':
            self.news_table = 'nasdaq_news'
            self.relation_table = 'many_nasdaq_news'
            self.stock_table = 'stock_nasdaq'
            self.index = index.upper()
        else:
            raise ValueError('wrong index')

    def insert_location(self,location):
        conn = sqlite3.connect('stock.db',timeout=10)#connect to database
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO location VALUES (null,{location["name"]},"{location["lat"]}",{location["lon"]})')
        conn.commit()
        conn.close()

    def insert_many_location(self,stock_id,news_id,location_id):
        conn = sqlite3.connect('stock.db',timeout=10)#connect to database
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO location VALUES ({stock_id},{news_id},{location_id})')
        conn.commit()
        conn.close()

    def get_all_process_news_id(self):
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT news_id FROM location")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def noun(self,text):
        cleantext = text.replace('"','').replace("'","")
        doc = self.nlp(cleantext)
        group = []
        for i in doc.noun_chunks:
            group.append(i.text)
        return group

    def match_stock(self,noun):
        stock = Categories().get_all_stock()
        matching = []
        for i in noun:
            if i in stock:
                matching.append(i)
        return list(set(matching))
    
    def has_numbers(self,inputString):
        return any(char.isdigit() for char in inputString)
    
    def ban_list(self,inputString):
        ban_list = ['(',')',',','/','\\']
        return any(char in ban_list for char in inputString)
                
    def location(self,noun):
        stock = Categories().get_all_stock()
        ban_word = ['SET','BUY','mai']
        possible_location = []
        for i in noun:
            if i in stock or i in ban_word:
                continue
            doc = self.nlp(i)
            for ent in doc.ents:
                if ent.label_ == "GPE":
                    possible_location.append(i)
        possible_location = list(set(possible_location))
        return possible_location    

    def extract_lat_lon(self,location):
        # location = self.geolocator.geocode(location)
        response = requests.get(f'https://nominatim.openstreetmap.org/search.php?q={location}&format=jsonv2')
        data = response.json()
        if len(data) != 0:
            return (data[0]['lat'],data[0]['lon'])
        return None
    
    def get_all_news(self):
        processed_news = self.get_all_process_news_id()
        news = News()
        all_news_id = news.get_all_id()
        data = []
        for i in all_news_id:
            if i in processed_news:
                continue
            text = news.combine_translate(i)
            data.append([i,text])
        return data
    
    def fetch_location(self):
        processed_news = self.get_all_process_news_id()
        news = News()
        all_news_id = news.get_all_id()
        for news_id in all_news_id:
            if news_id in processed_news:
                continue
            text = news.combine_translate(news_id)
            noun = self.noun(text)
            stocks = self.match_stock(noun)
            location = self.location(noun)
            if len(stocks)==0 or len(location)==0:
                continue
            for i in location:
                lat_lon = self.extract_lat_lon(i)
                if lat_lon == None:
                    continue
                for j in stocks:
                    stock = Stock(j)
                    stock_id = stock.get_stock_id()
                    self.insert_location([stock_id,news_id,i,lat_lon[0],lat_lon[1]])
    