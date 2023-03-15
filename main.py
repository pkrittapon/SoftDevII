import sys
from connect_ui import plot_candle , plot_finance , get_sec_indus, plot_spatial, get_all_symbol, get_all_sector, get_all_industry, get_all_statement, get_all_symbol_in_sector, get_all_symbol_in_industry, get_all_news, get_top_symbol, plot_treemap
from data.function import Categories,Stock,News,Location
from PyQt5.QtCore import Qt,QThread
from PyQt5 import QtWidgets, QtCore 
from PyQt5.QtWidgets import QMainWindow, QApplication,QPushButton,QTableWidgetItem,QHeaderView,QAbstractScrollArea,QSizePolicy
import plotly.graph_objects as go
from ui_component import Ui_MainWindow
import time
import threading
import plotly.express as px
import pandas as pd


class MyThread_stock(QThread):
    finished = QtCore.pyqtSignal()
    result_ready = QtCore.pyqtSignal(list)
    
    def __init__(self,data,index,filters):
        super().__init__()
        self.data = data
        self.index = index
        self.filters = filters
        
    @QtCore.pyqtSlot()
    def pre_stock(self):
        data = []
        count = 0
        count_pass = 0
        filtered_data = []
        for i, symbol in enumerate(self.data):
            count += 1
            t0 = time.time()
            obj = Stock(symbol,self.index)
            stock_dict = {}
            stock_dict['Symbol'] = symbol

            price = obj.get_stock_price(interval = '1d')
            change = obj.get_percent_change(interval = '1d')
            if change == [] :
                continue
            else:
                price = float('{:.4f}'.format(round(price, 4)).rstrip('0').rstrip('.') or '0')
                stock_dict['Change'] = float('{:.4f}'.format(round(change, 4)).rstrip('0').rstrip('.') or '0')
            count_pass+=1
            stock_dict['Price'] = price
            industry = obj.industry()
            stock_dict['Industry'] = industry
            sector = obj.sector()
            stock_dict['Sector'] = sector

            if self.index == "NASDAQ":
                if self.filters != []:
                    try:
                        financial = obj.financial_statement()[0]
                    except:
                        continue
                    key_dict = {'Report EPS':0,'Total Asset':1,'Liabilities':2,'Gross Profit':3,'Total Revenue':4,'Net Income':5}
                    key_list = self.filters

                    for i in key_list:
                            stock_dict[i[0]] = financial[key_dict[i[0]]+3]
            else:
                if self.filters != []:
                    try:
                        financial = obj.financial_statement()[-2]
                    except:
                        continue
                    key_dict = {'Total Asset':0,'Liabilities':1,'Equity':2,'Paid Up Capital':3,'Revenue':4,'Net Profit':5,'EPS':6,'ROA':7,'ROE':8,'Net Profit Margin':9,'Market Capitalization':10,'P/E':11,'P/BE':12,'Dividend Yield':13}
                    key_list = self.filters
                    for j in key_list:
                        stock_dict[j[0]] = financial[key_dict[j[0]]+3]
            
            data.append(stock_dict)

            # Emit filtered data every 20 symbols processed
            if self.index == "SET":
                number_update_data = 5
            else:
                number_update_data = 1
            if i % number_update_data == number_update_data-1 or i == len(self.data) - 1:
                for stock_data in data:
                    pass_all = True
                    for filter_topic in self.filters:
                        if stock_data[filter_topic[0]] == None:
                            stock_data[filter_topic[0]] = 0
                        if not (float(filter_topic[1]) <= stock_data[filter_topic[0]] and stock_data[filter_topic[0]] <= float(filter_topic[2])):
                            pass_all = False
                            break
                    if pass_all:
                        filtered_data.append(stock_data)
                self.result_ready.emit(filtered_data)
                data = []
            t1 = time.time()
            print(symbol,t1-t0)
        self.result_ready.emit(filtered_data)
        self.finished.emit()

class MyThread_download(QThread):
    ready = QtCore.pyqtSignal()
    finished =  QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(list)

    def __init__(self, symbol,index):
        super().__init__()
        self.symbol = symbol
        self.index = index
        
    
    @QtCore.pyqtSlot()
    def update_data_price(self):
        for i in range(len(self.index)):
            stock_obj = Stock(self.symbol[i],self.index[i])
            try:
                self.ready.emit()
                stock_obj.fetch_stock_price('1h')
                stock_obj.fetch_stock_price('1d')
            except:
                self.error.emit([self.symbol[i],self.index[i]])
        self.ready.emit()
        self.finished.emit()

    @QtCore.pyqtSlot()
    def update_data_statement(self):
        stock_obj = Stock(self.symbol[0],self.index[0])
        stock_obj.fetch_financial()
        self.finished.emit()


    @QtCore.pyqtSlot()
    def update_data_news(self):
        news = News(self.index[0])
        news.fetch_news(self.symbol[0])
        self.finished.emit()

    @QtCore.pyqtSlot()
    def update_data_location(self):
        location = Location(self.index[0])
        location.fetch_location(self.symbol[0])
        self.finished.emit()

class MyThread_crypto(QThread):
    finished = QtCore.pyqtSignal()
    result_ready = QtCore.pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        
    @QtCore.pyqtSlot()
    def search_crypto(self):
        all_symbol_crypto = get_top_symbol("CRYPTO")
        filtered_data = []
        processed_count = 0
        for sym in all_symbol_crypto:
            crypto_obj = Stock(sym,"CRYPTO")
            price = crypto_obj.get_stock_price(interval = '1d')
            change = crypto_obj.get_percent_change(interval = '1d')
            if change == [] :
                continue
            change = float('{:.5f}'.format(round(change, 5)).rstrip('0').rstrip('.') or '0')
            if price == [] or change == []:
                continue
            else:
                filtered_data.append(dict(symbol = sym ,Price = price,Change=change,name=""))
            
            processed_count += 1
            if processed_count % 5 == 0:
                self.result_ready.emit(filtered_data)
            if processed_count >= 200:
                break
        
        self.result_ready.emit(filtered_data)
        self.finished.emit()

class MyThread_treemap(QThread):
    treemap_ready = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal()
    def __init__(self, all_symbol, index):
        super().__init__()
        self.all_symbol = all_symbol
        self.index = index

    @QtCore.pyqtSlot()
    def tree(self):
        global symbol, sector, industry, market_cap
        symbol = []
        sector = []
        industry = []
        market_cap = []

        # Define the number of threads to use
        num_threads = 4

        # Split the symbols into batches for each thread
        batch_size = len(self.all_symbol) // num_threads
        batches = [(i * batch_size, (i + 1) * batch_size, self.index) for i in range(num_threads)]
        batches[-1] = (batches[-1][0], len(self.all_symbol), self.index)
        
        # Create the threads and start processing the batches
        threads = [threading.Thread(target=self.process_symbols_batch, args=batch) for batch in batches]
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        
        if self.index == "CRYPTO":
            df = pd.DataFrame({
            'Coin': symbol,
            'Sector': sector,
            'Industry': industry,
            'Market Capitalization': market_cap})
            fig = px.treemap(df, path = ['Coin'],values='Market Capitalization')
        else:
            df = pd.DataFrame({
            'Company': symbol,
            'Sector': sector,
            'Industry': industry,
            'Market Capitalization': market_cap})
            fig = px.treemap(df, path=['Industry', 'Sector', 'Company'], values='Market Capitalization')

        fig.update_layout(dict(plot_bgcolor = '#1f1f1f',
            paper_bgcolor= '#1f1f1f'))
        fig.update_layout(
        font=dict(
            family="Noto Sans Thai Light",
            size=16,
            color="white"
        )
    )
        fig.update_traces(textfont_color='white')
        # Emit the signal with the resulting treemap
        self.treemap_ready.emit(fig)
        self.finished.emit()

    def process_symbol(self,i, index):
        obj = Stock(i, index)
        if index == "SET":
            try:
                temp_market_cap = obj.financial_statement()[-2][13]
            except:
                return None
        elif index == "NASDAQ" or index == "CRYPTO":
            try:
                amount = obj.get_nasdaq_crypto_amount()
                last_price = obj.get_stock_price()
                temp_market_cap = amount * last_price
            except:
                return None
        sector = obj.sector()
        industry = obj.industry()
        return (i, sector, industry, temp_market_cap)

    # Define a function to process a batch of symbols
    def process_symbols_batch(self,start_index, end_index, index):
        for i in range(start_index, end_index):
            result = self.process_symbol(self.all_symbol[i], index)
            if result is not None:
                symbol.append(result[0])
                sector.append(result[1])
                industry.append(result[2])
                market_cap.append(result[3])
        

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.last_watch_page = None
        self.last_index = None
        self.last_market_page = None

        self.current_data = None
        self.progress2 = 0    
        self.finish2 = 0

        self.progress = 0
        self.finish = 0
        self.finish2 = 0
        self.last_crypto_data = None
        
        self.last_stock_filtered_data_set = None
        self.last_stock_filtered_data_nasdaq = None
        self.inputable = True

        start_pic = go.Figure(layout=dict(plot_bgcolor = '#1f1f1f',
                    paper_bgcolor = '#1f1f1f',
                    font = dict(color = "white")))
        
        self.ui.fig.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
        self.ui.fig2.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
        self.ui.fig3.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
        self.ui.fig4.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
        self.ui.fig5.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
        self.ui.fig6.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
        self.ui.fig7.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
        self.ui.fig8.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
        self.ui.fig9.setHtml(start_pic.to_html(include_plotlyjs='cdn'))

        self.ui.fig.setZoomFactor(0.9)
        self.ui.fig2.setZoomFactor(0.7)
        self.ui.fig3.setZoomFactor(0.6)
        self.ui.fig4.setZoomFactor(1)
        self.ui.fig5.setZoomFactor(1)
        self.ui.fig6.setZoomFactor(1)
        self.ui.fig7.setZoomFactor(1)
        self.ui.fig8.setZoomFactor(1)
        self.ui.fig9.setZoomFactor(1)

        Set = Categories('SET')
        Nasdaq = Categories('NASDAQ')
        Crypto = Categories('CRYPTO')
        all_symbol = []
        for symbol in Set.get_all_stock():
            all_symbol.append(symbol+'\t\t- SET')
        for symbol in Nasdaq.get_all_stock():
            all_symbol.append(symbol+'\t\t- NASDAQ')
        for symbol in Crypto.get_all_stock():
            if len(symbol) > 4:
                all_symbol.append(symbol+'-USD'+'\t- CRYPTO')
            else:
                all_symbol.append(symbol+'-USD'+'\t\t- CRYPTO')
        self.ui.symbol_comboBox.addItems(all_symbol)
        # completers only work for editable combo boxes. QComboBox.NoInsert prevents insertion of the search text
        self.ui.symbol_comboBox.setEditable(True)
        self.ui.symbol_comboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        # change completion mode of the default completer from InlineCompletion to PopupCompletion
        self.ui.symbol_comboBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # enable partial consecutive search
        self.ui.symbol_comboBox.completer().setFilterMode(QtCore.Qt.MatchContains)
        self.ui.symbol_comboBox.completer().setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.ui.symbol_comboBox_2.addItems(all_symbol)
        # completers only work for editable combo boxes. QComboBox.NoInsert prevents insertion of the search text
        self.ui.symbol_comboBox_2.setEditable(True)
        self.ui.symbol_comboBox_2.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        # change completion mode of the default completer from InlineCompletion to PopupCompletion
        self.ui.symbol_comboBox_2.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # enable partial consecutive search
        self.ui.symbol_comboBox_2.completer().setFilterMode(QtCore.Qt.MatchContains)
        self.ui.symbol_comboBox_2.completer().setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.ui.symbol_comboBox_2.setCurrentIndex(-1)
        self.ui.symbol_comboBox_2.currentIndexChanged.connect(self.add_symbol)
        
        self.ui.symbol_comboBox.setCurrentIndex(-1)
        self.ui.symbol_comboBox.currentIndexChanged.connect(self.change_stock_graph)

        self.ui.freq_comboBox.setCurrentIndex(-1)
        self.ui.freq_comboBox.currentIndexChanged.connect(self.change_interval)

        self.ui.freq_comboBox_2.setCurrentIndex(-1)
        self.ui.freq_comboBox_2.currentIndexChanged.connect(self.change_interval)
        
        self.ui.statements_comboBox.setCurrentIndex(-1)
        self.ui.statements_comboBox.currentIndexChanged.connect(self.change_finance)

        self.ui.statements_comboBox_2.setCurrentIndex(-1)
        self.ui.statements_comboBox_2.currentIndexChanged.connect(self.change_finance)

        self.ui.news_comboBox.setCurrentIndex(-1)
        self.ui.news_comboBox_2.setCurrentIndex(-1)
        self.ui.news_comboBox_3.setCurrentIndex(-1)
        self.ui.news_comboBox.currentIndexChanged.connect(self.change_period)
        self.ui.news_comboBox_2.currentIndexChanged.connect(self.change_period)
        self.ui.news_comboBox_3.currentIndexChanged.connect(self.change_period)

        # #load item to dropdown
        self.load_all_sector_indus("SET")
        self.load_filter("SET")
        self.load_all_sector_indus("NASDAQ")
        self.load_filter("NASDAQ")

        self.ui.min_SpinBox_set.setMaximum(9999999999999)
        self.ui.max_SpinBox_set2.setMaximum(9999999999999)
        self.ui.min_SpinBox_nasdaq.setMaximum(9999999999999)
        self.ui.max_SpinBox_nasdaq.setMaximum(9999999999999)

        self.ui.button_market_page.clicked.connect(lambda : self.click_market())
        self.ui.set_button.clicked.connect(lambda : self.click_set())
        self.ui.nasdaq_button.clicked.connect(lambda : self.click_nasdaq())
        self.ui.crypto_button.clicked.connect(lambda : self.click_crypto())
        self.ui.button_watch_page.clicked.connect(lambda : self.click_watch())
        self.ui.button_overall_page.clicked.connect(lambda : self.click_overall())
        self.ui.button_stock_page.clicked.connect(lambda : self.click_stock())
        self.ui.button_financial_page.clicked.connect(lambda : self.click_financial())
        self.ui.button_spatial_page.clicked.connect(lambda : self.click_spatial())
        self.ui.button_news_page.clicked.connect(lambda : self.click_news())
        self.ui.button_update_page.clicked.connect(lambda : self.click_update())
        self.ui.button_update_all_page.clicked.connect(lambda : self.click_update_all())

        self.ui.crypto_tableWidget.setColumnCount(3)
        self.ui.crypto_tableWidget.setHorizontalHeaderLabels(['Symbol', 'Price', 'Change'])
        self.ui.crypto_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.crypto_tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.ui.crypto_tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # #-------------watch search crypto------------------------------
        self.ui.search_button_crypto.clicked.connect(self.search_crypto_buff)
        self.ui.sort_comboBox_crypto2.currentIndexChanged.connect(lambda: self.show_crypto(self.last_crypto_data))

        # #-------------watch search set------------------------------
        self.ui.search_button_set.clicked.connect(self.search_stock_buff_set)
        self.ui.sort_comboBox_set1.currentIndexChanged.connect(lambda: self.show_stock_set(self.last_stock_filtered_data_set))
        self.ui.sort_comboBox_set2.currentIndexChanged.connect(lambda: self.show_stock_set(self.last_stock_filtered_data_set))
        
        ##------------------------treemap---------------------------
        self.ui.search_button_set_2.clicked.connect(self.plot_treemap_set)
        self.ui.search_button_nasdaq_2.clicked.connect(self.plot_treemap_nasdaq)
        self.ui.search_button_crypto_2.clicked.connect(self.plot_treemap_crypto)


        # #-------------watch search nasdaq------------------------------
        self.ui.search_button_nasdaq.clicked.connect(self.search_stock_buff_nasdaq)
        self.ui.sort_comboBox_nasdaq1.currentIndexChanged.connect(lambda: self.show_stock_nasdaq(self.last_stock_filtered_data_nasdaq))
        self.ui.sort_comboBox_nasdaq2.currentIndexChanged.connect(lambda: self.show_stock_nasdaq(self.last_stock_filtered_data_nasdaq))

        # Initialize the news items
        self.news_items = []
        self.news_model = NewsModel(self.news_items)
        self.ui.news_list.setModel(self.news_model)
        self.ui.news_list.clicked.connect(self.show_content)
        self.ui.back_button.clicked.connect(self.hide_content)
        self.ui.news_content.setVisible(False)
        self.ui.back_button.setVisible(False)


        # # filter set
        self.ui.industry_comboBox_set.currentIndexChanged.connect(lambda: self.choose_sec_indus_only_one_set("indus"))
        self.ui.sector_comboBox_set.currentIndexChanged.connect(lambda: self.choose_sec_indus_only_one_set("sec"))
        self.ui.industry_comboBox_set_2.currentIndexChanged.connect(lambda: self.choose_sec_indus_only_one_set_2("indus"))
        self.ui.sector_comboBox_set_2.currentIndexChanged.connect(lambda: self.choose_sec_indus_only_one_set_2("sec"))
        self.ui.filter_tableWidget_set.setColumnCount(4)
        self.ui.filter_tableWidget_set.setRowCount(0)
        self.ui.filter_tableWidget_set.setHorizontalHeaderLabels(["Filter", "Minimum value", "Maximum value", "Remove"])
        self.ui.add_filter_button_set.clicked.connect(self.add_filter_set)
        self.ui.filter_tableWidget_set.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.filter_tableWidget_set.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.ui.filter_tableWidget_set.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # # filter nasdaq
        self.ui.industry_comboBox_nasdaq.currentIndexChanged.connect(lambda: self.choose_sec_indus_only_one_nasdaq("indus"))
        self.ui.sector_comboBox_nasdaq.currentIndexChanged.connect(lambda: self.choose_sec_indus_only_one_nasdaq("sec"))
        self.ui.industry_comboBox_nasdaq_2.currentIndexChanged.connect(lambda: self.choose_sec_indus_only_one_nasdaq_2("indus"))
        self.ui.sector_comboBox_nasdaq_2.currentIndexChanged.connect(lambda: self.choose_sec_indus_only_one_nasdaq_2("sec"))
        self.ui.filter_tableWidget_nasdaq.setColumnCount(4)
        self.ui.filter_tableWidget_nasdaq.setRowCount(0)
        self.ui.filter_tableWidget_nasdaq.setHorizontalHeaderLabels(["Filter", "Minimum value", "Maximum value", "Remove"])
        self.ui.add_filter_button_nasdaq.clicked.connect(self.add_filter_nasdaq)
        self.ui.filter_tableWidget_nasdaq.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.filter_tableWidget_nasdaq.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.ui.filter_tableWidget_nasdaq.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # #stock set
        self.ui.symbol_tableWidget_set.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.symbol_tableWidget_set.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.ui.symbol_tableWidget_set.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # # #stock nasdaq
        self.ui.symbol_tableWidget_nasdaq.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.symbol_tableWidget_nasdaq.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.ui.symbol_tableWidget_nasdaq.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  

        # # download all
        self.ui.tableWidget.setColumnCount(3)
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setHorizontalHeaderLabels(["Symbol", "Index", "Remove"])
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.ui.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)          
        self.ui.start_download_button.clicked.connect(self.update_all)

        self.ui.progressBar.setValue(0)
        self.ui.progressBar_2.setValue(0)
        self.ui.update_button.clicked.connect(self.download)
        self.ui.stackedWidget.setCurrentIndex(6)
        self.ui.stackedWidget_3.setCurrentIndex(0)
        
        self.filter_inputs_set = []
        self.filter_inputs_nasdaq = []
        self.symbol_list = []


# #------------------------------------Watch Filter-------------------------------------------------------------
    def add_filter_set(self):
        # Get input values and create FilterInput object
        filter_name = self.ui.filter_conboBox_set.currentText()
        lower_bound = self.ui.min_SpinBox_set.value()
        upper_bound = self.ui.max_SpinBox_set2.value()
        filter_input = FilterInput(filter_name, lower_bound, upper_bound)

        # Add FilterInput object to list and table
        self.filter_inputs_set.append(filter_input)
        row = self.ui.filter_tableWidget_set.rowCount()
        self.ui.filter_tableWidget_set.insertRow(row)
        self.ui.filter_tableWidget_set.setItem(row, 0, QTableWidgetItem(filter_name))
        self.ui.filter_tableWidget_set.setItem(row, 1, QTableWidgetItem(str(lower_bound)))
        self.ui.filter_tableWidget_set.setItem(row, 2, QTableWidgetItem(str(upper_bound)))

        # Create remove button for row
        button_remove = QPushButton("Remove")
        button_remove.clicked.connect(lambda checked, row=row: self.delete_row_set(row))
        self.ui.filter_tableWidget_set.setCellWidget(row, 3, button_remove)
        self.ui.filter_tableWidget_set.resizeColumnsToContents()
        self.ui.filter_tableWidget_set.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_filter_nasdaq(self):
        # Get input values and create FilterInput object
        filter_name = self.ui.filter_conboBox_nasdaq.currentText()
        lower_bound = self.ui.min_SpinBox_nasdaq.value()
        upper_bound = self.ui.max_SpinBox_nasdaq.value()
        filter_input = FilterInput(filter_name, lower_bound, upper_bound)

        # Add FilterInput object to list and table
        self.filter_inputs_nasdaq.append(filter_input)
        row = self.ui.filter_tableWidget_nasdaq.rowCount()
        self.ui.filter_tableWidget_nasdaq.insertRow(row)
        self.ui.filter_tableWidget_nasdaq.setItem(row, 0, QTableWidgetItem(filter_name))
        self.ui.filter_tableWidget_nasdaq.setItem(row, 1, QTableWidgetItem(str(lower_bound)))
        self.ui.filter_tableWidget_nasdaq.setItem(row, 2, QTableWidgetItem(str(upper_bound)))

        # Create remove button for row
        button_remove = QPushButton("Remove")
        button_remove.clicked.connect(lambda checked, row=row: self.delete_row_nasdaq(row))
        self.ui.filter_tableWidget_nasdaq.setCellWidget(row, 3, button_remove)
        self.ui.filter_tableWidget_nasdaq.resizeColumnsToContents()
        self.ui.filter_tableWidget_nasdaq.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def delete_row_set(self, row):
        # Remove row from table and filter_inputs list
        self.ui.filter_tableWidget_set.removeRow(row)
        self.filter_inputs_set.pop(row)

        # Update remove buttons in table
        for row in range(self.ui.filter_tableWidget_set.rowCount()):
            button_remove = QPushButton("Remove")
            button_remove.clicked.connect(lambda checked, row=row: self.delete_row_set(row))
            self.ui.filter_tableWidget_set.setCellWidget(row, 3, button_remove)
    
    def delete_row_nasdaq(self, row):
        # Remove row from table and filter_inputs list
        self.ui.filter_tableWidget_nasdaq.removeRow(row)
        self.filter_inputs_nasdaq.pop(row)

        # Update remove buttons in table
        for row in range(self.ui.filter_tableWidget_nasdaq.rowCount()):
            button_remove = QPushButton("Remove")
            button_remove.clicked.connect(lambda checked, row=row: self.delete_row_nasdaq(row))
            self.ui.filter_tableWidget_nasdaq.setCellWidget(row, 3, button_remove)

    def load_all_sector_indus(self,index):#load to dropdown
        if index == "SET":
            self.ui.sector_comboBox_set.addItems(sorted(get_all_sector(index)))
            self.ui.industry_comboBox_set.addItems(sorted(get_all_industry(index)))
            self.ui.sector_comboBox_set_2.addItems(sorted(get_all_sector(index)))
            self.ui.industry_comboBox_set_2.addItems(sorted(get_all_industry(index)))
        else:
            self.ui.sector_comboBox_nasdaq.addItems(sorted(get_all_sector(index)))
            self.ui.industry_comboBox_nasdaq.addItems(sorted(get_all_industry(index)))
            self.ui.sector_comboBox_nasdaq_2.addItems(sorted(get_all_sector(index)))
            self.ui.industry_comboBox_nasdaq_2.addItems(sorted(get_all_industry(index)))

    def load_filter(self,index):#load to dropdown
        data = get_all_statement(index)
        if index == "SET":
            self.ui.filter_conboBox_set.clear()
            self.ui.filter_conboBox_set.addItems(data)
        else:
            self.ui.filter_conboBox_nasdaq.clear()
            self.ui.filter_conboBox_nasdaq.addItems(data)
    
    def choose_sec_indus_only_one_set(self,what):
        if self.ui.sector_comboBox_set.currentIndex() == 0 and self.ui.industry_comboBox_set.currentIndex() == 0:
            pass
        elif what == "sec" and self.ui.sector_comboBox_set.currentIndex() != -1:
            self.ui.industry_comboBox_set.setCurrentIndex(-1)
        elif what == "indus" and self.ui.industry_comboBox_set.currentIndex() != -1:
            self.ui.sector_comboBox_set.setCurrentIndex(-1)

    def choose_sec_indus_only_one_set_2(self,what):
        if self.ui.sector_comboBox_set_2.currentIndex() == 0 and self.ui.industry_comboBox_set_2.currentIndex() == 0:
            pass
        elif what == "sec" and self.ui.sector_comboBox_set_2.currentIndex() != -1:
            self.ui.industry_comboBox_set_2.setCurrentIndex(-1)
        elif what == "indus" and self.ui.industry_comboBox_set_2.currentIndex() != -1:
            self.ui.sector_comboBox_set_2.setCurrentIndex(-1)
            
    def choose_sec_indus_only_one_nasdaq(self,what):
        if self.ui.sector_comboBox_nasdaq.currentIndex() == 0 and self.ui.industry_comboBox_nasdaq.currentIndex() == 0:
            pass
        elif what == "sec" and self.ui.sector_comboBox_nasdaq.currentIndex() != -1:
            self.ui.industry_comboBox_nasdaq.setCurrentIndex(-1)
        elif what == "indus" and self.ui.industry_comboBox_nasdaq.currentIndex() != -1:
            self.ui.sector_comboBox_nasdaq.setCurrentIndex(-1)

    def choose_sec_indus_only_one_nasdaq_2(self,what):
        if self.ui.sector_comboBox_nasdaq_2.currentIndex() == 0 and self.ui.industry_comboBox_nasdaq_2.currentIndex() == 0:
            pass
        elif what == "sec" and self.ui.sector_comboBox_nasdaq_2.currentIndex() != -1:
            self.ui.industry_comboBox_nasdaq_2.setCurrentIndex(-1)
        elif what == "indus" and self.ui.industry_comboBox_nasdaq_2.currentIndex() != -1:
            self.ui.sector_comboBox_nasdaq_2.setCurrentIndex(-1)
    
#------------------------------------------Tree Map-----------------------------------------------------------------
    def plot_treemap_set(self):
        input_industry = self.ui.industry_comboBox_set_2.currentText()
        input_sector = self.ui.sector_comboBox_set_2.currentText()
        if input_industry == "All Industry" or input_sector == "All Sector":# get all , no filter sector and indus
            index = "SET"
            self.all_symbol = get_top_symbol("SET")
        elif input_industry != "":# get only stock in industry
            index = "SET"
            self.all_symbol = get_all_symbol_in_industry("SET",input_industry)
        else:# get only stock in sector
            index = "SET"
            self.all_symbol = get_all_symbol_in_sector("SET",input_sector)

        self.treemap = plot_treemap(self.all_symbol,index)
        self.ui.fig7.setHtml(self.treemap.to_html(include_plotlyjs='cdn'))

    def plot_treemap_nasdaq(self):
        input_industry = self.ui.industry_comboBox_nasdaq_2.currentText()
        input_sector = self.ui.sector_comboBox_nasdaq_2.currentText()
        if input_industry == "All Industry" or input_sector == "All Sector":# get all , no filter sector and indus
            index = "NASDAQ"
            all_symbol = get_top_symbol("NASDAQ")
        elif input_industry != "":# get only stock in industry
            index = "NASDAQ"
            all_symbol = get_all_symbol_in_industry("NASDAQ",input_industry)
        else:# get only stock in sector
            index = "NASDAQ"
            all_symbol = get_all_symbol_in_sector("NASDAQ",input_sector)

        self.thread_nasdaq = MyThread_treemap(all_symbol, index)
        self.thread_nasdaq_thread = QThread()
        self.thread_nasdaq.moveToThread(self.thread_nasdaq_thread)
        self.thread_nasdaq.finished.connect(self.thread_nasdaq_thread.quit) # added
        self.thread_nasdaq.finished.connect(self.thread_nasdaq.deleteLater) # added
        self.thread_nasdaq.treemap_ready.connect(self.show_treemap_nasdaq)
        self.thread_nasdaq_thread.started.connect(self.start_worker_treemap_nasdaq) # moved
        self.thread_nasdaq_thread.start()
        self.thread_nasdaq.finished.connect(self.thread_nasdaq_thread.quit)
        self.thread_nasdaq.finished.connect(self.thread_nasdaq_thread.wait)

    def start_worker_treemap_nasdaq(self):
        self.ui.search_button_nasdaq_2.setEnabled(False)
        self.ui.search_button_crypto_2.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.thread_nasdaq, 'tree', QtCore.Qt.QueuedConnection) 

    def show_treemap_nasdaq(self, treemap):
        self.ui.search_button_nasdaq_2.setEnabled(True)
        self.ui.search_button_crypto_2.setEnabled(True)
        self.ui.fig8.setHtml(treemap.to_html(include_plotlyjs='cdn'))

    def plot_treemap_crypto(self):
        index = "CRYPTO"
        all_symbol = get_top_symbol("CRYPTO")

        self.thread_crypto = MyThread_treemap(all_symbol, index)
        self.thread_crypto_thread = QThread()
        self.thread_crypto.moveToThread(self.thread_crypto_thread)
        self.thread_crypto.finished.connect(self.thread_crypto_thread.quit) # added
        self.thread_crypto.finished.connect(self.thread_crypto.deleteLater) # added
        self.thread_crypto.treemap_ready.connect(self.show_treemap_crypto)
        self.thread_crypto_thread.started.connect(self.start_worker_treemap_crypto) # moved
        self.thread_crypto_thread.start()
        self.thread_crypto.finished.connect(self.thread_crypto_thread.quit)
        self.thread_crypto.finished.connect(self.thread_crypto_thread.wait)

    def start_worker_treemap_crypto(self):
        self.ui.search_button_nasdaq_2.setEnabled(False)
        self.ui.search_button_crypto_2.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.thread_crypto, 'tree', QtCore.Qt.QueuedConnection) 

    def show_treemap_crypto(self, treemap):
        self.ui.search_button_nasdaq_2.setEnabled(True)
        self.ui.search_button_crypto_2.setEnabled(True)
        self.ui.fig9.setHtml(treemap.to_html(include_plotlyjs='cdn'))
    

# #------------------------------------- Watch Stock-------------------------------------------------------------
#     #-----------set--------------
    def search_stock_buff_set(self):
        self.ui.search_button_set.setEnabled(False)
        input_industry = self.ui.industry_comboBox_set.currentText()
        input_sector = self.ui.sector_comboBox_set.currentText()
        filter_topics = []
        for row in range(self.ui.filter_tableWidget_set.rowCount()):
            row_data = []
            for col in range(self.ui.filter_tableWidget_set.columnCount()):
                item = self.ui.filter_tableWidget_set.item(row, col)
                if item is not None:
                    row_data.append(item.text())
            filter_topics.append(row_data)
            
        if input_industry == "All Industry" or input_sector == "All Sector":# get all , no filter sector and indus
            index = "SET"
            all_symbol = get_top_symbol("SET")
        elif input_industry != "":# get only stock in industry
            index = "SET"
            all_symbol = get_all_symbol_in_industry("SET",input_industry)
        else:# get only stock in sector
            index = "SET"
            all_symbol = get_all_symbol_in_sector("SET",input_sector)

        self.ui.sort_comboBox_set1.clear()
        self.ui.sort_comboBox_set1.addItem("Sort by Price")
        self.ui.sort_comboBox_set1.addItem("Sort by Change")
        for filter_topic in filter_topics:
            self.ui.sort_comboBox_set1.addItem("Sort by " + filter_topic[0])
        self.worker_thread_set = QThread()
        self.worker_set = MyThread_stock(all_symbol,index,filter_topics)
        self.worker_set.moveToThread(self.worker_thread_set)
        self.worker_set.finished.connect(self.worker_thread_set.quit) # added
        self.worker_set.finished.connect(self.worker_set.deleteLater) # added
        self.worker_set.result_ready.connect(self.get_last_stock_price_set)
        self.worker_thread_set.started.connect(self.start_worker_set)
        self.worker_thread_set.start()
        self.worker_set.finished.connect(self.worker_thread_set.quit)
        self.worker_set.finished.connect(self.worker_thread_set.wait)

    def start_worker_set(self):
        self.ui.search_button_set.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker_set, 'pre_stock', QtCore.Qt.QueuedConnection)

    def get_last_stock_price_set(self,result):
        self.last_stock_filtered_data_set = result
        self.show_stock_set( self.last_stock_filtered_data_set)

    def show_stock_set(self,filtered_data):
        if self.last_stock_filtered_data_set == None or self.last_stock_filtered_data_set == []:
            return
        sort_topic = self.ui.sort_comboBox_set1.currentText()[8:]
        sort_order = self.ui.sort_comboBox_set2.currentIndex()
        # Sort data based on sort order
        if sort_topic == '':
            sort_topic = "Price"
        if sort_order == 0:
            sorted_data = sorted(filtered_data, key=lambda x: x[sort_topic])
        else:
            sorted_data = sorted(filtered_data, key=lambda x: x[sort_topic], reverse=True)

        # Reset table size and display results in table
        first_keys = {'Symbol', 'Price'}
        exclude_keys = {"Industry", "Sector"}
        last_keys = {'Change'}
        # Split the unique_keys set into two sets
        remaining_keys = sorted_data[0].keys() - first_keys - exclude_keys - last_keys

        # Convert the unique_keys set into a list in the desired order
        column_order = ['Symbol', 'Price'] + list(remaining_keys) + list(last_keys)

        # Set the column count for your table
        self.ui.symbol_tableWidget_set.reset()
        self.ui.symbol_tableWidget_set.setRowCount(len(sorted_data))
        self.ui.symbol_tableWidget_set.setColumnCount(len(column_order))
        self.ui.symbol_tableWidget_set.setHorizontalHeaderLabels(column_order)

        # Populate the table with data
        for i, stock in enumerate(sorted_data):
            for j, key in enumerate(column_order):
                value = stock.get(key, '')

                if key == 'Change':
                    item = QTableWidgetItem(str(value)+"%")
                    if value > 0:
                        item.setForeground(Qt.green)
                    elif value < 0:
                        item.setForeground(Qt.red)
                else:
                    item = QTableWidgetItem(str(value))

                self.ui.symbol_tableWidget_set.setItem(i, j, item)

        # Resize the columns to fit the contents
        self.ui.search_button_set.setEnabled(True)
        self.ui.symbol_tableWidget_set.resizeColumnsToContents()
        self.ui.symbol_tableWidget_set.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    #-----------nasdaq-----------
    def search_stock_buff_nasdaq(self):
        self.ui.search_button_nasdaq.setEnabled(False)
        input_industry = self.ui.industry_comboBox_nasdaq.currentText()
        input_sector = self.ui.sector_comboBox_nasdaq.currentText()
        filter_topics = []
        for row in range(self.ui.filter_tableWidget_nasdaq.rowCount()):
            row_data = []
            for col in range(self.ui.filter_tableWidget_nasdaq.columnCount()):
                item = self.ui.filter_tableWidget_nasdaq.item(row, col)
                if item is not None:
                    row_data.append(item.text())
            filter_topics.append(row_data)
            
        if input_industry == "All Industry" or input_sector == "All Sector":# get all , no filter sector and indus
            index = "NASDAQ"
            all_symbol = get_top_symbol("NASDAQ")
        elif input_industry != "":# get only stock in industry
            index = "NASDAQ"
            all_symbol = get_all_symbol_in_industry("NASDAQ",input_industry)
        else:# get only stock in sector
            index = "NASDAQ"
            all_symbol = get_all_symbol_in_sector("NASDAQ",input_sector)

        self.ui.sort_comboBox_nasdaq1.clear()
        self.ui.sort_comboBox_nasdaq1.addItem("Sort by Price")
        self.ui.sort_comboBox_nasdaq1.addItem("Sort by Change")

        for filter_topic in filter_topics:
            self.ui.sort_comboBox_nasdaq1.addItem("Sort by " + filter_topic[0])
        self.worker_thread_nasdaq = QThread()
        self.worker_nasdaq = MyThread_stock(all_symbol,index,filter_topics)
        self.worker_nasdaq.moveToThread(self.worker_thread_nasdaq)
        self.worker_nasdaq.finished.connect(self.worker_thread_nasdaq.quit) # added
        self.worker_nasdaq.finished.connect(self.worker_nasdaq.deleteLater) # added
        self.worker_nasdaq.result_ready.connect(self.get_last_stock_price_nasdaq)
        self.worker_thread_nasdaq.started.connect(self.start_worker_nasdaq)
        self.worker_thread_nasdaq.start()
        self.worker_nasdaq.finished.connect(self.worker_thread_nasdaq.quit)
        self.worker_nasdaq.finished.connect(self.worker_thread_nasdaq.wait)

    def start_worker_nasdaq(self):
        self.ui.search_button_nasdaq.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker_nasdaq, 'pre_stock', QtCore.Qt.QueuedConnection)

    def get_last_stock_price_nasdaq(self,result):
        self.last_stock_filtered_data_nasdaq = result
        self.show_stock_nasdaq( self.last_stock_filtered_data_nasdaq)

    def show_stock_nasdaq(self,filtered_data):
        if self.last_stock_filtered_data_nasdaq == None:
            return
        sort_topic = self.ui.sort_comboBox_nasdaq1.currentText()[8:]
        sort_order = self.ui.sort_comboBox_nasdaq2.currentIndex()
        # Sort data based on sort order
        if sort_topic == '':
            sort_topic = "Price"
        if sort_order == 0:
            sorted_data = sorted(filtered_data, key=lambda x: x[sort_topic])
        else:
            sorted_data = sorted(filtered_data, key=lambda x: x[sort_topic], reverse=True)

        first_keys = {'Symbol', 'Price'}
        exclude_keys = {"Industry", "Sector"}
        last_keys = {'Change'}

        # Split the unique_keys set into two sets
        remaining_keys = sorted_data[0].keys() - first_keys - exclude_keys - last_keys

        # Convert the unique_keys set into a list in the desired order
        column_order = ['Symbol', 'Price'] + sorted(list(remaining_keys)) + list(last_keys)

        # Set the column count for your table
        self.ui.symbol_tableWidget_nasdaq.reset()
        self.ui.symbol_tableWidget_nasdaq.setRowCount(len(sorted_data))
        self.ui.symbol_tableWidget_nasdaq.setColumnCount(len(column_order))
        self.ui.symbol_tableWidget_nasdaq.setHorizontalHeaderLabels(column_order)

        # Populate the table with data
        for i, stock in enumerate(sorted_data):
            for j, key in enumerate(column_order):
                value = stock.get(key, '')

                if key == 'Change':
                    item = QTableWidgetItem(str(value)+"%")
                    if value > 0:
                        item.setForeground(Qt.green)
                    elif value < 0:
                        item.setForeground(Qt.red)
                else:
                    item = QTableWidgetItem(str(value))

                self.ui.symbol_tableWidget_nasdaq.setItem(i, j, item)

        # Resize the columns to fit the contents
        self.ui.search_button_nasdaq.setEnabled(True)
        self.ui.symbol_tableWidget_nasdaq.resizeColumnsToContents()
        self.ui.symbol_tableWidget_nasdaq.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
# # -----------------------------------Crypto Watch---------------------------------------------------------------
    def search_crypto_buff(self):
        self.ui.sort_comboBox_crypto1.clear()
        self.ui.sort_comboBox_crypto1.addItem("Sort by Price")
        self.ui.sort_comboBox_crypto1.addItem("Sort by Change")
        self.worker_thread_cryp = QThread()
        self.worker_cryp = MyThread_crypto()
        self.worker_cryp.moveToThread(self.worker_thread_cryp)
        self.worker_cryp.result_ready.connect(self.get_last_crypto_price)
        self.worker_cryp.finished.connect(self.worker_thread_cryp.quit) # added
        self.worker_cryp.finished.connect(self.worker_cryp.deleteLater) # added
        self.worker_thread_cryp.started.connect(self.start_worker_crypto)
        self.worker_thread_cryp.start()
        self.worker_cryp.finished.connect(self.worker_thread_cryp.quit)
        self.worker_cryp.finished.connect(self.worker_thread_cryp.wait)

    def start_worker_crypto(self):
        self.ui.search_button_crypto.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker_cryp, 'search_crypto', QtCore.Qt.QueuedConnection)

    def get_last_crypto_price(self,result):
        self.last_crypto_data = result
        self.show_crypto(result)
    
    def show_crypto(self,data):
        if self.last_crypto_data == None:
            return
        
        sort_topic = self.ui.sort_comboBox_crypto1.currentText()[8:]
        sort_order = self.ui.sort_comboBox_crypto2.currentIndex()

        if sort_topic == '':
            sort_topic = "Price"
        if sort_order == 0:
            sorted_data = sorted(data, key=lambda x: x[sort_topic])
        else:
            sorted_data = sorted(data, key=lambda x: x[sort_topic], reverse=True)
        
        self.ui.crypto_tableWidget.setRowCount(len(sorted_data))
        for i, stock in enumerate(sorted_data):
            symbol_item = QTableWidgetItem(stock['symbol'])
            symbol_item.setToolTip(stock['name'])
            price_item = QTableWidgetItem(str(stock['Price']))
            change_item = QTableWidgetItem(str(stock['Change'])+"%")
            # change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            if stock['Change'] > 0:
                change_item.setForeground(Qt.green)
            elif stock['Change'] < 0:
                change_item.setForeground(Qt.red)
            else:
                change_item.setForeground(Qt.black)

            self.ui.crypto_tableWidget.setItem(i, 0, symbol_item)
            self.ui.crypto_tableWidget.setItem(i, 1, price_item)
            self.ui.crypto_tableWidget.setItem(i, 2, change_item)
                # Resize table columns
            self.ui.crypto_tableWidget.resizeColumnsToContents()
            self.ui.crypto_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.search_button_crypto.setEnabled(True)
        
# #--------------------------------------------News----------------------------------------------
    def add_news_item(self, title, timestamp, content):
        # Create a new news item
        item = NewsItem(title, timestamp, content)

        # Add the item to the news items list and the model
        self.news_items.append(item)
        self.news_model.layoutChanged.emit()

    def show_content(self, index):
        # Show the content of the selected news item and hide the list view
        item = self.news_items[index.row()]
        self.ui.news_content.setHtml(item.content)
        self.ui.news_content.setVisible(True)
        self.ui.news_list.setVisible(False)
        self.ui.news_comboBox.setVisible(False)
        self.ui.back_button.setVisible(True)
        self.ui.news_label.setText(item.title)
        self.ui.news_content.setGeometry(self.contentsRect())

    def hide_content(self):
        # Hide the content of the selected news item and show the list view
        self.ui.news_content.setVisible(False)
        self.ui.news_list.setVisible(True)
        self.ui.news_comboBox.setVisible(True)
        self.ui.back_button.setVisible(False)
        self.ui.news_label.setText("News")

#----------------------------------------click change page----------------------------------------------
    def click_market(self):
        if self.last_market_page == None:
            self.last_market_page = 0
            self.ui.set_button.setChecked(True)
        if self.last_market_page == 0:
            self.ui.set_button.setChecked(True)
        elif self.last_market_page == 1:
            self.ui.nasdaq_button.setChecked(True)
        elif self.last_market_page == 2:
            self.ui.crypto_button.setChecked(True)
        self.ui.stackedWidget.setCurrentIndex(self.last_market_page)
        self.ui.stackedWidget_3.setCurrentIndex(1)
    def click_watch(self):  
        if self.last_watch_page == None:
            self.last_watch_page = 3
            self.ui.set_button.setChecked(True)
        if self.last_watch_page == 3:
            self.ui.set_button.setChecked(True)
        elif self.last_watch_page == 4:
            self.ui.nasdaq_button.setChecked(True)
        elif self.last_watch_page == 5:
            self.ui.crypto_button.setChecked(True)
        self.ui.stackedWidget.setCurrentIndex(self.last_watch_page)
        self.ui.stackedWidget_3.setCurrentIndex(1)
    def click_set(self):
        if self.ui.button_watch_page.isChecked():
            self.last_watch_page = 3
            self.ui.stackedWidget.setCurrentIndex(3)
        if self.ui.button_market_page.isChecked():
            self.last_market_page = 0
            self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.stackedWidget_3.setCurrentIndex(1)
    def click_nasdaq(self):
        if self.ui.button_watch_page.isChecked():
            self.last_watch_page = 4
            self.ui.stackedWidget.setCurrentIndex(4)
        if self.ui.button_market_page.isChecked():
            self.last_market_page = 1
            self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.stackedWidget_3.setCurrentIndex(1)
    def click_crypto(self):
        if self.ui.button_watch_page.isChecked():
            self.last_watch_page = 5
            self.ui.stackedWidget.setCurrentIndex(5)
        if self.ui.button_market_page.isChecked():
            self.last_market_page = 2
            self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.stackedWidget_3.setCurrentIndex(1)
    def click_overall(self):
        self.ui.stackedWidget.setCurrentIndex(6)
        self.ui.stackedWidget_3.setCurrentIndex(0)
    def click_stock(self):
        self.ui.stackedWidget.setCurrentIndex(7)
        self.ui.stackedWidget_3.setCurrentIndex(0)
    def click_financial(self):
        self.ui.stackedWidget.setCurrentIndex(8)
        self.ui.stackedWidget_3.setCurrentIndex(0)
    def click_news(self):
        self.ui.stackedWidget.setCurrentIndex(9)
        self.ui.stackedWidget_3.setCurrentIndex(0)
    def click_spatial(self):
        self.ui.stackedWidget.setCurrentIndex(10)
        self.ui.stackedWidget_3.setCurrentIndex(0)
    def click_update(self):
        self.ui.stackedWidget.setCurrentIndex(11)
        self.ui.stackedWidget_3.setCurrentIndex(0)
    def click_update_all(self):
        self.ui.stackedWidget.setCurrentIndex(12)
        self.ui.stackedWidget_3.setCurrentIndex(2)

#------------------------------------------download update---------------------------------------------------
    def download(self):
        self.progress = 0
        self.ui.update_button.setEnabled(False)
        self.ui.progressBar.setValue(0)
        price_state = self.ui.checkBox_price.isChecked()
        statements_state = self.ui.checkBox_statements.isChecked()
        news_state = self.ui.checkBox_news.isChecked()
        location_state = self.ui.checkBox_location.isChecked()
        self.load_number = 0
        if news_state and location_state:
            self.load_number += 1
            round = 3
        else:
            round = 4
        if self.current_data != None:
            for i in range(round):  
                if i == 0 and price_state:
                    #load history price
                    self.load_number += 1
                    self.worker_thread = QThread()
                    self.worker = MyThread_download([self.current_data[0]],[self.current_data[1]])
                    self.worker.moveToThread(self.worker_thread)
                    self.worker.finished.connect(self.worker_thread.quit) # added
                    self.worker.finished.connect(self.worker.deleteLater) # added
                    self.worker.finished.connect(lambda :self.update_data("price",False))
                    self.worker_thread.started.connect(self.start_worker_download_price) # moved
                    self.worker_thread.start()
                    self.worker.finished.connect(self.worker_thread.quit)
                    self.worker.finished.connect(self.worker_thread.wait)

                elif i == 1 and statements_state:
                    self.load_number += 1
                    self.worker_thread_statement = QThread()
                    self.worker_statement = MyThread_download([self.current_data[0]],[self.current_data[1]])
                    self.worker_statement.moveToThread(self.worker_thread_statement)
                    self.worker_statement.finished.connect(self.worker_thread_statement.quit) # added
                    self.worker_statement.finished.connect(self.worker_statement.deleteLater) # added
                    self.worker_statement.finished.connect(lambda :self.update_data("statement",False))
                    self.worker_thread_statement.started.connect(self.start_worker_download_statement) # moved
                    self.worker_thread_statement.start()
                    self.worker_statement.finished.connect(self.worker_thread_statement.quit)
                    self.worker_statement.finished.connect(self.worker_thread_statement.wait)
                elif i == 2 and news_state:
                    self.load_number += 1
                    self.worker_thread_news = QThread()
                    self.worker_news = MyThread_download([self.current_data[0]],[self.current_data[1]])
                    self.worker_news.moveToThread(self.worker_thread_news)
                    self.worker_thread_news.finished.connect(self.worker_thread_news.quit) # added
                    self.worker_thread_news.finished.connect(self.worker_news.deleteLater) # added
                    self.worker_news.finished.connect(lambda :self.update_data("news",location_state))
                    self.worker_thread_news.started.connect(self.start_worker_download_news) # moved
                    self.worker_thread_news.start()
                    self.worker_news.finished.connect(self.worker_thread_news.quit)
                    self.worker_news.finished.connect(self.worker_thread_news.wait)
                elif i == 3 and location_state:
                    self.load_number += 1
                    self.worker_thread_location = QThread()
                    self.worker_location = MyThread_download([self.current_data[0]],[self.current_data[1]])
                    self.worker_location.moveToThread(self.worker_thread_location)
                    self.worker_location.finished.connect(self.worker_thread_location.quit) # added
                    self.worker_location.finished.connect(self.worker_location.deleteLater) # added
                    self.worker_location.finished.connect(lambda :self.update_data("location",False))
                    self.worker_thread_location.started.connect(self.start_worker_download_location) # moved
                    self.worker_thread_location.start()
                    self.worker_location.finished.connect(self.worker_thread_location.quit)
                    self.worker_location.finished.connect(self.worker_thread_location.wait)

    def start_worker_download_price(self):
        self.ui.update_button.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker, 'update_data_price', QtCore.Qt.QueuedConnection)

    def start_worker_download_statement(self):
        self.ui.update_button.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker_statement, 'update_data_statement', QtCore.Qt.QueuedConnection)

    def start_worker_download_news(self):
        self.ui.update_button.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker_news, 'update_data_news', QtCore.Qt.QueuedConnection)

    def start_worker_download_location(self):
        self.ui.update_button.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker_location, 'update_data_location', QtCore.Qt.QueuedConnection)

    def start_worker_download_location2(self):
        self.ui.update_button.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker_location2, 'update_data_location', QtCore.Qt.QueuedConnection)
    
    def update_data(self,who,state):
        part = 100/self.load_number
        if state :
            self.worker_thread_location2 = QThread()
            self.worker_location2 = MyThread_download([self.current_data[0]],[self.current_data[1]])
            self.worker_location2.moveToThread(self.worker_thread_location2)
            self.worker_location2.finished.connect(self.worker_thread_location2.quit) # added
            self.worker_location2.finished.connect(self.worker_location2.deleteLater) # added
            self.worker_location2.finished.connect(lambda :self.update_data("location",False))
            self.worker_thread_location2.started.connect(self.start_worker_download_location2) # moved
            self.worker_thread_location2.start()
            self.worker_location2.finished.connect(self.worker_thread_location2.quit)
            self.worker_location2.finished.connect(self.worker_thread_location2.wait)
            
        if who == "price":
            self.progress += part
            self.ui.progressBar.setValue(int(self.progress))
            self.finish += 1
            self.pic_candle = plot_candle(self.current_data[0],self.current_data[1])
            interval_list = list(self.pic_candle.keys())
            if self.last_candle_key == "No data" and len(interval_list) > 1:
                start_pic = go.Figure(layout=dict(plot_bgcolor = '#1f1f1f',
                paper_bgcolor = '#1f1f1f',
                font = dict(color = "white")))
                self.ui.fig.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
                self.ui.fig4.setHtml(start_pic.to_html(include_plotlyjs='cdn'))
            elif self.last_candle_key == "No data" and len(interval_list) < 1:
                self.last_candle_key = "Hourly"
                self.ui.fig.setHtml(self.pic_candle[self.last_candle_key].to_html(include_plotlyjs='cdn'))
                self.ui.fig4.setHtml(self.pic_candle[self.last_candle_key].to_html(include_plotlyjs='cdn'))
            else :
                self.ui.fig.setHtml(self.pic_candle[self.last_candle_key].to_html(include_plotlyjs='cdn'))
                self.ui.fig4.setHtml(self.pic_candle[self.last_candle_key].to_html(include_plotlyjs='cdn'))
            self.ui.freq_comboBox.clear()
            self.ui.freq_comboBox_2.clear()
            self.ui.freq_comboBox.addItems(interval_list)
            self.ui.freq_comboBox_2.addItems(interval_list)

        elif who == "statement":
            self.progress += part
            self.ui.progressBar.setValue(int(self.progress))
            self.finish += 1
            self.pic_finance = plot_finance(self.current_data[0],self.current_data[1])
            finance_topic = list(self.pic_finance.keys())
            self.ui.fig2.setHtml(self.pic_finance[finance_topic[0]][0].to_html(include_plotlyjs='cdn'))
            self.ui.fig5.setHtml(self.pic_finance[finance_topic[0]][0].to_html(include_plotlyjs='cdn'))
            self.ui.statements_comboBox.clear()
            self.ui.statements_comboBox_2.clear()
            self.ui.statements_comboBox.addItems(finance_topic)
            self.ui.statements_comboBox_2.addItems(finance_topic)
        elif who == "news":
            self.progress += part
            self.ui.progressBar.setValue(int(self.progress))
            self.finish += 1
            self.news_items.clear()
            self.news_model.layoutChanged.emit()
            all_news = get_all_news(self.current_data[0],self.current_data[1],"All")
            for each_news in all_news:
                self.add_news_item(each_news[1], each_news[2], each_news[4])
        elif who == "location":
            self.progress += part
            self.ui.progressBar.setValue(int(self.progress))
            self.finish += 1
            self.pic_spatial = plot_spatial(self.current_data[0],self.current_data[1])
            self.ui.fig3.setHtml(self.pic_spatial["All"].to_html(include_plotlyjs='cdn'))
            self.ui.fig6.setHtml(self.pic_spatial["All"].to_html(include_plotlyjs='cdn'))
            self.ui.news_comboBox.setCurrentIndex(4)
            self.ui.news_comboBox_2.setCurrentIndex(4)
            self.ui.news_comboBox_3.setCurrentIndex(4)

        
        if self.finish == self.load_number:
            self.finish = 0
            self.ui.progressBar.setValue(100)
            self.ui.checkBox_location.setChecked(False)
            self.ui.checkBox_news.setChecked(False)
            self.ui.checkBox_price.setChecked(False)
            self.ui.checkBox_statements.setChecked(False)
            self.ui.update_button.setEnabled(True)
            if list(self.pic_spatial.keys())[0] == "No data":
                plane_fig = go.Figure(layout=dict(plot_bgcolor = '#1f1f1f',
                    paper_bgcolor = '#1f1f1f',
                    font = dict(color = "white")))
                self.ui.fig3.setHtml(plane_fig.to_html(include_plotlyjs='cdn'))
                self.ui.fig6.setHtml(plane_fig.to_html(include_plotlyjs='cdn'))
            else:
                # self.ui.fig3.setHtml(s_pic.to_html(include_plotlyjs='cdn'))
                self.ui.fig6.setHtml(self.pic_spatial["All"].to_html(include_plotlyjs='cdn'))
                self.ui.fig3.setHtml(self.pic_spatial["All"].to_html(include_plotlyjs='cdn'))
        

# #-----------------------------------------update all------------------------------------------------------------

    def add_symbol(self):
        if self.inputable == True:
            self.ui.tableWidget.reset()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setHorizontalHeaderLabels(["Symbol","Index","Remove"])
            self.inputable = False
            

        symbol_text = self.ui.symbol_comboBox_2.currentText().split()
        if symbol_text == '':
            return
        symbol, category = symbol_text[0],symbol_text[-1]
        

        symbol_input = SymbolInput(symbol, category)

        self.symbol_list.append(symbol_input)
        for i in range(self.ui.tableWidget.rowCount()):
            if self.ui.tableWidget.item(i,0).text() == symbol and  self.ui.tableWidget.item(i,1).text() == category:
                # item already exists, clear text field and return
                return
            
        row_count = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.verticalHeader().setVisible(False)
        self.ui.tableWidget.insertRow(row_count)
        self.ui.tableWidget.setItem(row_count, 0, QtWidgets.QTableWidgetItem(symbol))
        self.ui.tableWidget.setItem(row_count, 1, QtWidgets.QTableWidgetItem(category))

        button_remove = QPushButton("Remove")
        button_remove.clicked.connect(lambda checked, row=row_count: self.delete_symbol(row_count))
        self.ui.tableWidget.setCellWidget(row_count, 2, button_remove)
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def delete_symbol(self, row):
        # Remove row from table and filter_inputs list
        self.ui.tableWidget.removeRow(row)
        self.symbol_list.pop(row)
        # Update remove buttons in table
        for row in range(self.ui.tableWidget.rowCount()):
            button_remove = QPushButton("Remove")
            button_remove.clicked.connect(lambda checked, row=row: self.delete_symbol(row))
            self.ui.tableWidget.setCellWidget(row, 2, button_remove)

    def update_all(self):  
        set_state = self.ui.set_checkBox.isChecked()
        nasdaq_state = self.ui.nasdaq_checkbox.isChecked()
        crypto_state = self.ui.crypto_checkBox.isChecked()
        if self.ui.tableWidget.rowCount() < 1 and not(set_state) and not(nasdaq_state) and not(crypto_state):
            return
        self.ui.start_download_button.setEnabled(False)
        self.progress2 = 0
        self.ui.progressBar_2.setValue(0)
        self.number_symbol_download = 0
        all_symbol = []
        all_index = []
        self.uncomplete = []
        if set_state:
            symbol = Categories("SET").get_all_stock()
            all_symbol+=(symbol)
            all_index += ["SET"] * len(symbol)

        if nasdaq_state:
            symbol = Categories("NASDAQ").get_all_stock()
            all_symbol+=(symbol)
            all_index += ["NASDAQ"] * len(symbol)

        if crypto_state:
            symbol = Categories("CRYPTO").get_all_stock()
            all_symbol+=(symbol)
            all_index += ["CRYPTO"] * len(symbol)



        for row in range(self.ui.tableWidget.rowCount()):
            symbol = self.ui.tableWidget.item(row, 0).text()
            category = self.ui.tableWidget.item(row, 1).text()
            
            if category == "SET" and set_state == True:
                continue
            if category == "NASDAQ" and nasdaq_state == True:
                continue
            if category == "CRYPTO" and crypto_state == True:
                continue

            if category == "CRYPTO":
                symbol = symbol[:-4]
            all_symbol.append(symbol)
            all_index.append(category)

        self.number_symbol_download = len(all_symbol)
        self.worker_update_all_thread = QThread()
        self.worker_update_all = MyThread_download(all_symbol,all_index)
        self.worker_update_all.moveToThread(self.worker_update_all_thread)
        self.worker_update_all.finished.connect(self.worker_update_all_thread.quit)
        self.worker_update_all.finished.connect(self.worker_update_all.deleteLater)
        self.worker_update_all.ready.connect(self.update_all_finished)
        self.worker_update_all.error.connect(self.error)
        self.worker_update_all_thread.started.connect(self.start_worker_download_all)
        self.worker_update_all_thread.start()
        self.worker_update_all.finished.connect(self.worker_update_all_thread.quit)
        self.worker_update_all.finished.connect(self.worker_update_all_thread.wait)

    def start_worker_download_all(self):
        self.ui.start_download_button.setEnabled(False)
        QtCore.QMetaObject.invokeMethod(self.worker_update_all, 'update_data_price', QtCore.Qt.QueuedConnection)

    def error(self,data):
        self.uncomplete.append(data)

    def update_all_finished(self):
        part = 100/self.number_symbol_download
        self.progress2 += part
        self.ui.progressBar_2.setValue(int(self.progress2))
        self.finish2 += 1

        if self.finish2 == self.number_symbol_download:
            self.finish2 = 0
            self.ui.start_download_button.setEnabled(True)
            self.ui.progressBar_2.setValue(100)
            self.ui.tableWidget.reset()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.setColumnCount(2)
            self.ui.tableWidget.setHorizontalHeaderLabels(["Symbol(Undownloadable "+str(len(self.uncomplete))+" symbols)","Index (Undownloadable)"])
            # Assuming tableWidget is your QTableWidget object
            for i in range(len(self.uncomplete)):
                row_count = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row_count)
                symbol = QTableWidgetItem(self.uncomplete[i][0])
                index = QTableWidgetItem(self.uncomplete[i][1])
                self.ui.tableWidget.setItem(i, 0, symbol)
                self.ui.tableWidget.setItem(i, 1, index)

            self.inputable = True


# #-----------------------------------------change graph---------------------------------------------------------
    def change_finance(self,index):
        key = list(self.pic_finance.keys())[index]

        if len(list(self.pic_finance.keys()))>1:
            self.ui.fig2.setHtml(self.pic_finance[key][0].to_html(include_plotlyjs='cdn'))
            self.ui.fig5.setHtml(self.pic_finance[key][0].to_html(include_plotlyjs='cdn'))

            self.ui.statements_comboBox.setCurrentIndex(index)
            self.ui.statements_comboBox_2.setCurrentIndex(index)

    def change_interval(self,index):
        key = list(self.pic_candle.keys())[index]
        self.last_candle_key = key

        self.ui.fig.setHtml(self.pic_candle[self.last_candle_key].to_html(include_plotlyjs='cdn'))
        self.ui.fig4.setHtml(self.pic_candle[self.last_candle_key].to_html(include_plotlyjs='cdn'))

        self.ui.freq_comboBox.setCurrentIndex(index)
        self.ui.freq_comboBox_2.setCurrentIndex(index)

    def change_period(self,index):
        key = list(self.pic_spatial.keys())[index]

        self.ui.fig3.setHtml(self.pic_spatial[key].to_html(include_plotlyjs='cdn'))
        self.ui.fig6.setHtml(self.pic_spatial[key].to_html(include_plotlyjs='cdn'))

        self.ui.news_comboBox.setCurrentIndex(index)
        self.ui.news_comboBox_2.setCurrentIndex(index)
        self.ui.news_comboBox_3.setCurrentIndex(index)

        self.news_items.clear()
        self.news_model.layoutChanged.emit()

        all_news = get_all_news(self.current_data[0],self.current_data[1],key)
        for each_news in all_news:
            self.add_news_item(each_news[1], each_news[2], each_news[4])
      
    def change_stock_graph(self,index):
        if index != -1 and index != self.last_index:

            #clear news list
            self.news_items.clear()
            self.news_model.layoutChanged.emit()

            self.ui.update_button.setEnabled(True)

            self.last_index = index
            item_text = self.ui.symbol_comboBox.currentText().split()
            stock_index = item_text[-1]
            if stock_index == "CRYPTO":
                word = item_text[0][:-4]
            else:
                word = item_text[0]
            name = Stock(word,item_text[-1]).get_stock_name()
                
            
            self.current_data = word,stock_index
            self.pic_candle = plot_candle(word,stock_index)
            self.pic_finance = plot_finance(word,stock_index)
            self.pic_spatial = plot_spatial(word,stock_index)
            
            interval_list = list(self.pic_candle.keys())
            self.ui.freq_comboBox.clear()
            self.ui.freq_comboBox_2.clear()
            self.ui.freq_comboBox.addItems(interval_list)
            self.ui.freq_comboBox_2.addItems(interval_list)

            finance_topic = list(self.pic_finance.keys())
            self.ui.statements_comboBox.clear()
            self.ui.statements_comboBox_2.clear()
            self.ui.statements_comboBox.addItems(finance_topic)
            self.ui.statements_comboBox_2.addItems(finance_topic)

            period_list = list(self.pic_spatial.keys())
            self.ui.news_comboBox.clear()
            self.ui.news_comboBox_2.clear()
            self.ui.news_comboBox_3.clear()
            self.ui.news_comboBox.addItems(period_list)
            self.ui.news_comboBox_2.addItems(period_list)
            self.ui.news_comboBox_3.addItems(period_list)

            self.ui.freq_comboBox.setCurrentIndex(0)
            self.ui.freq_comboBox_2.setCurrentIndex(0)
            self.ui.statements_comboBox.setCurrentIndex(0)
            self.ui.statements_comboBox_2.setCurrentIndex(0)
            self.ui.news_comboBox.setCurrentIndex(4)
            self.ui.news_comboBox_2.setCurrentIndex(4)
            self.ui.news_comboBox_3.setCurrentIndex(4)
            sector,industry = get_sec_indus(word,stock_index)
            
            self.ui.Main_Symbol_Label.setText(word)
            self.ui.symbol_name.setText(name)
            self.ui.sector_name.setText(sector)
            self.ui.industry_name.setText(industry)
            self.ui.index_name.setText(stock_index)
            
            all_news = get_all_news(word,stock_index,"All")
            for each_news in all_news:
                self.add_news_item(each_news[1], each_news[2], each_news[4])

            if list(self.pic_candle.keys())[0] == "No data":
                plane_fig = go.Figure(layout=dict(plot_bgcolor = '#1f1f1f',
                    paper_bgcolor = '#1f1f1f',
                    font = dict(color = "white")))
                self.ui.fig.setHtml(plane_fig.to_html(include_plotlyjs='cdn'))
                self.ui.fig4.setHtml(plane_fig.to_html(include_plotlyjs='cdn'))
            else:
                self.last_candle_key = "Hourly"
                self.ui.fig.setHtml(self.pic_candle[self.last_candle_key].to_html(include_plotlyjs='cdn'))
                self.ui.fig4.setHtml(self.pic_candle[self.last_candle_key].to_html(include_plotlyjs='cdn'))
    
            if len (list(self.pic_finance.keys())) > 1:
                f_pic = self.pic_finance[list(self.pic_finance.keys())[0]][0]
                self.ui.fig2.setHtml(f_pic.to_html(include_plotlyjs='cdn'))
                self.ui.fig5.setHtml(f_pic.to_html(include_plotlyjs='cdn'))
            else:
                plane_fig = go.Figure(layout=dict(plot_bgcolor = '#1f1f1f',
                    paper_bgcolor = '#1f1f1f',
                    font = dict(color = "white")))
                self.ui.fig2.setHtml(plane_fig.to_html(include_plotlyjs='cdn'))
                self.ui.fig5.setHtml(plane_fig.to_html(include_plotlyjs='cdn'))



            self.ui.progressBar.setValue(0)


class NewsModel(QtCore.QAbstractListModel):
    def __init__(self, items):
        super().__init__()
        self.items = items

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            item = self.items[index.row()]
            return f"{item.title} ({item.timestamp})"
        elif role == Qt.UserRole:
            item = self.items[index.row()]
            return item.content

class NewsItem:
    def __init__(self, title, timestamp, content):
        self.title = title
        self.timestamp = timestamp
        self.content = content

class FilterInput:
    def __init__(self, filter_name, lower_bound, upper_bound):
        self.filter_name = filter_name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        
class SymbolInput:
    def __init__(self, symbol_name, index_name):
        self.symbol_name = symbol_name
        self.index_name = index_name


if __name__ == "__main__":
    app = QApplication(sys.argv)    

    window = MainWindow()

    with open('style.qss', 'r') as f:
        style = f.read()
    app.setStyleSheet(style)
   
    window.show()
    sys.exit(app.exec())


