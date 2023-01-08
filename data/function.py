import sqlite3


class Categories:

    def get_all_stock(self):
        """คืนค่าหุ้นทั้งหมด"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM stock")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_industrial(self):
        """คืนค่าดัชนีอุตสาหกรรมทั้งหมด"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT industrial FROM stock")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_sector(self):
        """คืนค่า sector ทั้งหมด"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT sector FROM stock")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_sector_in_industrial(self,industrial):
        """คืนค่า sector ทั้งหมดที่อยู่ในดัชนีอุตสาหกรรมที่ป้อนเข้ามา"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT sector FROM stock WHERE industrial = '{industrial.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_stock_in_industrial(self,industrial):
        """คืนค่าหุ้นทั้งหมดที่อยู่ในดัชนีอุตสาหกรรมที่ป้อนเข้ามา"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM stock WHERE industrial = '{industrial.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_all_stock_in_sector(self,sector):
        """คืนค่าหุ้นทั้งหมดที่อยู่ใน sector ที่ป้อนเข้ามา"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT symbol FROM stock WHERE sector = '{sector.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]

    def get_set100(self):
        """คืนค่าหุ้นทั้งหมดที่อยู่ใน set 100"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT stock.symbol FROM set100 LEFT JOIN stock ON stock.stock_id = set100.stock_id")
        data = cursor.fetchall()
        conn.close()
        return [i[0] for i in data]



class Stock:

    def __init__(self,symbol):
        self.symbol = symbol

    def get_stock_id(self):
        """คืนค่า id ของหุ้น"""       
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT stock_id FROM stock WHERE symbol = '{self.symbol.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0] 

    def get_stock_price(self):
        """คืนค่าราคาล่าสุดของหุ้นใน database"""
        id = self.get_stock_id()
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT close FROM price WHERE stockdata = {id} order by [datetime] desc limit 1")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def latest_update_time(self):
        """คืนค่าเวลาล่าสุดที่หุ้นถูก update"""
        id = self.get_stock_id()
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT max([datetime]) from price WHERE stockdata = {id}")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def oldest_update_time(self):
        """คืนค่าเวลาเก่าสุดที่หุ้นถูก update"""
        id = self.get_stock_id()
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT min([datetime]) from price WHERE stockdata = {id}")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def get_all_stock_price(self, **kwargs):
        """คืนค่าข้อมูลราคาทั้งหมดของหุ้นตามช่วงเวลาที่กำหนด"""
        start = kwargs.get('start',None)
        end = kwargs.get('end',None)
        id = self.get_stock_id()
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        if start != None and end != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close,volume FROM price where [datetime] BETWEEN '{start}' AND '{end}' AND stockdata = {id}")
        elif start != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close,volume FROM price where [datetime] > '{start}'  AND stockdata = {id}")
        elif end != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close,volume FROM price where [datetime] < '{end}'  AND stockdata = {id}")
        else:
            cursor.execute(f"SELECT [datetime],open,high,low,close,volume FROM price WHERE stockdata= {id} ORDER by [datetime]")
        data = cursor.fetchall()
        conn.close()
        return data

    def sector(self):
        """คืนค่าหมวดหมู่"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT sector FROM stock WHERE symbol = '{self.symbol.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def industrial(self):
        """คืนค่าดัชนีอุตสาหกรรม"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT industrial FROM stock WHERE symbol = '{self.symbol.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]


class Sector:

    def __init__(self,symbol):
        self.symbol = symbol

    def get_price(self):
        """คืนค่าราคาล่าสุดของหุ้นใน database"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT close FROM sector_price WHERE sector = '{self.symbol.upper()}' order by [datetime] desc limit 1")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def latest_update_time(self):
        """คืนค่าเวลาล่าสุดที่หุ้นถูก update"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT max([datetime]) from sector_price WHERE sector = '{self.symbol.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def oldest_update_time(self):
        """คืนค่าเวลาเก่าสุดที่หุ้นถูก update"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT min([datetime]) from sector_price WHERE sector = '{self.symbol.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def get_all_price(self, **kwargs):
        """คืนค่าข้อมูลราคาทั้งหมดของหุ้นตามช่วงเวลาที่กำหนด"""
        start = kwargs.get('start',None)
        end = kwargs.get('end',None)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        if start != None and end != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close FROM sector_price where [datetime] BETWEEN '{start}' AND '{end}' AND sector = '{self.symbol.upper()}'")
        elif start != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close FROM sector_price where [datetime] > '{start}'  AND sector = '{self.symbol.upper()}'")
        elif end != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close FROM sector_price where [datetime] < '{end}'  AND sector = '{self.symbol.upper()}'")
        else:
            cursor.execute(f"SELECT [datetime],open,high,low,close FROM sector_price WHERE sector = '{self.symbol.upper()}' ORDER by [datetime]")
        data = cursor.fetchall()
        conn.close()
        return data


class Industrial:

    def __init__(self,symbol):
        self.symbol = symbol

    def get_price(self):
        """คืนค่าราคาล่าสุดของหุ้นใน database"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT close FROM industrial_price WHERE industrial = '{self.symbol.upper()}' order by [datetime] desc limit 1")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def latest_update_time(self):
        """คืนค่าเวลาล่าสุดที่หุ้นถูก update"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT max([datetime]) from industrial_price WHERE industrial = '{self.symbol.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def oldest_update_time(self):
        """คืนค่าเวลาเก่าสุดที่หุ้นถูก update"""
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT min([datetime]) from industrial_price WHERE industrial = '{self.symbol.upper()}'")
        data = cursor.fetchall()
        conn.close()
        return data[0][0]

    def get_all_price(self, **kwargs):
        """คืนค่าข้อมูลราคาทั้งหมดของหุ้นตามช่วงเวลาที่กำหนด"""
        start = kwargs.get('start',None)
        end = kwargs.get('end',None)
        conn = sqlite3.connect('stock.db',timeout=10)
        cursor = conn.cursor()
        if start != None and end != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close FROM industrial_price where [datetime] BETWEEN '{start}' AND '{end}' AND industrial = '{self.symbol.upper()}'")
        elif start != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close FROM industrial_price where [datetime] > '{start}'  AND industrial = '{self.symbol.upper()}'")
        elif end != None:
            cursor.execute(f"SELECT [datetime],open,high,low,close FROM industrial_price where [datetime] < '{end}'  AND industrial = '{self.symbol.upper()}'")
        else:
            cursor.execute(f"SELECT [datetime],open,high,low,close FROM industrial_price WHERE industrial = '{self.symbol.upper()}' ORDER by [datetime]")
        data = cursor.fetchall()
        conn.close()
        return data    