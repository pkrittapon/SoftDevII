import sys
from dash_html import plot_candle , plot_finance ,get_sec_indus,plot_spatial
from data.function import Categories,Stock

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
import plotly.graph_objects as go
from dash import dcc , html
import dash
import threading

app_dash = dash.Dash()  
app_dash2 = dash.Dash()  
app_dash3 = dash.Dash()  

from sidebar import Ui_MainWindow
        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.last_index = None
        self.current_data = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.fig.setZoomFactor(0.88)
        self.ui.fig2.setZoomFactor(0.88)
        self.ui.fig3.setZoomFactor(0.88)
        self.ui.fig4.setZoomFactor(1.6)
        self.ui.fig5.setZoomFactor(1.6)
        self.ui.fig6.setZoomFactor(1.9)

        Set = Categories('SET')
        Nasdaq = Categories('NASDAQ')
        Crypto = Categories('CRYPTO')
        all_symbol = []
        for symbol in Set.get_all_stock():
            all_symbol.append(symbol+'\t- SET')
        for symbol in Nasdaq.get_all_stock():
            all_symbol.append(symbol+'\t- NASDAQ')
        for symbol in Crypto.get_all_stock():
            all_symbol.append(symbol+'\t- CRYPTO')
        self.ui.comboBox_5.addItems(all_symbol)
        # completers only work for editable combo boxes. QComboBox.NoInsert prevents insertion of the search text
        self.ui.comboBox_5.setEditable(True)
        self.ui.comboBox_5.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        # change completion mode of the default completer from InlineCompletion to PopupCompletion
        self.ui.comboBox_5.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # enable partial consecutive search
        self.ui.comboBox_5.completer().setFilterMode(QtCore.Qt.MatchContains)
        self.ui.comboBox_5.completer().setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.ui.comboBox_5.setCurrentIndex(-1)
        self.ui.comboBox_5.currentIndexChanged.connect(self.change_stock_graph)

        self.ui.comboBox.addItem("Hourly")
        self.ui.comboBox.addItem("Daily")
        self.ui.comboBox.addItem("Weekly")
        self.ui.comboBox.addItem("Monthly")
        self.ui.comboBox.addItem("Quarterly")
        self.ui.comboBox.setCurrentIndex(-1)
        self.ui.comboBox.currentIndexChanged.connect(self.change_interval)
        
        self.ui.comboBox_3.addItem("Hourly")
        self.ui.comboBox_3.addItem("Daily")
        self.ui.comboBox_3.addItem("Weekly")
        self.ui.comboBox_3.addItem("Monthly")
        self.ui.comboBox_3.addItem("Quarterly")
        self.ui.comboBox_3.setCurrentIndex(-1)
        self.ui.comboBox_3.currentIndexChanged.connect(self.change_interval)

        self.ui.comboBox_2.currentIndexChanged.connect(self.change_finance)

        self.ui.comboBox_4.currentIndexChanged.connect(self.change_finance)

        self.ui.button_overall_page.clicked.connect(lambda : self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.button_stock_page.clicked.connect(lambda : self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.button_financial_page.clicked.connect(lambda : self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.button_trending_page.clicked.connect(lambda : self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.button_news_page.clicked.connect(lambda : self.ui.stackedWidget.setCurrentIndex(4))
        self.ui.button_update_page.clicked.connect(lambda : self.ui.stackedWidget.setCurrentIndex(5))
        
        
        
        self.ui.progressBar.setValue(0)
        self.ui.update_button.clicked.connect(self.download)
        self.ui.stackedWidget.setCurrentIndex(0)

    def download(self):
        self.ui.label_4.setText("Downloading stock data...")
        self.ui.update_button.setEnabled(False)
        self.ui.progressBar.setValue(0)
        price_state = self.ui.checkBox_price.isChecked()
        statements_state = self.ui.checkBox_statements.isChecked()
        news_state = self.ui.checkBox_news.isChecked()
        if self.current_data != None:
            for i in range(3):  
                if i == 0 and price_state:
                    #load history price
                    stock_data = Stock(self.current_data[0],self.current_data[1])
                    thread1 = threading.Thread(target=self.update_data(stock_data))
                    thread1.start()
                elif i == 1 and statements_state:
                    pass
                    #load statement
                elif i == 2 and news_state:
                    pass
                    #load news

    def update_data(self,stock_obj):
        stock_obj.fetch_stock_price('1h')
        self.ui.progressBar.setValue(50)
        stock_obj.fetch_stock_price('1d')
        self.ui.progressBar.setValue(100)
        self.pic_candle = plot_candle(self.current_data[0],self.current_data[1])
        self.ui.label_4.setText("Stock data downloaded successfully.")
        self.ui.update_button.setEnabled(True)
        if self.last_candle_key == "No data":
            self.last_candle_key = "Hourly"
        app_dash.layout = html.Div([
        dcc.Graph(id='graph', figure=self.pic_candle[self.last_candle_key])
        ])
        interval_list = list(self.pic_candle.keys())
        self.ui.comboBox.clear()
        self.ui.comboBox_3.clear()
        self.ui.comboBox.addItems(interval_list)
        self.ui.comboBox_3.addItems(interval_list)
        self.ui.fig2.reload()
        self.ui.fig5.reload()
        
    def change_finance(self,index):
        key = list(self.pic_finance.keys())[index]
        if len(list(self.pic_finance.keys()))>1:
            app_dash2.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_finance[key][0])
            ])
            self.ui.comboBox_2.setCurrentIndex(index)
            self.ui.comboBox_4.setCurrentIndex(index)
        self.ui.fig2.reload()
        self.ui.fig5.reload()

    def change_interval(self,index):
        key = list(self.pic_candle.keys())[index]
        self.last_candle_key = key
        app_dash.layout = html.Div([
        dcc.Graph(id='graph', figure=self.pic_candle[self.last_candle_key])
        ])
        self.ui.comboBox.setCurrentIndex(index)
        self.ui.comboBox_3.setCurrentIndex(index)
        self.ui.fig.reload()
        self.ui.fig4.reload()

    def change_stock_graph(self,index):
        if index != -1 and index != self.last_index:
            self.last_index = index
            item_text = self.ui.comboBox_5.currentText().split()
            word = item_text[0]
            stock_index = item_text[-1]
            self.current_data = word,stock_index
            self.pic_candle = plot_candle(word,stock_index)
            self.pic_finance = plot_finance(word,stock_index)
            self.pic_spatial = plot_spatial(word,stock_index)

            interval_list = list(self.pic_candle.keys())
            self.ui.comboBox.clear()
            self.ui.comboBox_3.clear()
            self.ui.comboBox.addItems(interval_list)
            self.ui.comboBox_3.addItems(interval_list)

            finance_topic = list(self.pic_finance.keys())
            self.ui.comboBox_2.clear()
            self.ui.comboBox_4.clear()
            self.ui.comboBox_2.addItems(finance_topic)
            self.ui.comboBox_4.addItems(finance_topic)

            self.ui.comboBox.setCurrentIndex(0)
            self.ui.comboBox_2.setCurrentIndex(0)
            self.ui.comboBox_3.setCurrentIndex(0)
            self.ui.comboBox_4.setCurrentIndex(0)
            sector,industry = get_sec_indus(word,stock_index)
            
            self.ui.symbol_name.setText(word)
            self.ui.sector_name.setText(sector)
            self.ui.industry_name.setText(industry)
            self.ui.index_name.setText(stock_index)
            

            if list(self.pic_candle.keys())[0] == "No data":
                app_dash.layout = html.Div([
                    dcc.Graph(id='graph', figure=go.Figure())
                ])
            else:
                self.last_candle_key = "Hourly"
                app_dash.layout = html.Div([
                    dcc.Graph(id='graph', figure=self.pic_candle[self.last_candle_key])
                ])
                
            # app_dash.layout = html.Div([
            #     dcc.Graph(id='graph', figure=self.last_candle)
            # ])
            if len (list(self.pic_finance.keys())) > 1:
                app_dash2.layout = html.Div([
                    dcc.Graph(id='graph', figure=self.pic_finance[list(self.pic_finance.keys())[0]][0])
                ])
            else:
                app_dash2.layout = html.Div([
                    dcc.Graph(id='graph', figure=go.Figure())
                ])
            if list(self.pic_spatial.keys())[0] == "No data":
                app_dash3.layout = html.Div([
                    dcc.Graph(id='graph', figure=go.Figure())
                ])
            else:
                app_dash3.layout = html.Div([
                    dcc.Graph(id='graph', figure=self.pic_spatial['Spatial'])
                ])
            self.ui.fig.reload()
            self.ui.fig2.reload()
            self.ui.fig3.reload()
            self.ui.fig4.reload()
            self.ui.fig5.reload()
            self.ui.fig6.reload()
            self.ui.label_4.setText(("Select topic and click the button to update stock data"))
            self.ui.progressBar.setValue(0)

    

def run_dash_server():
    app_dash.layout = html.Div([
        dcc.Graph(id='graph', figure=go.Figure())
    ])
    app_dash.run_server(use_reloader=False,port=8050)

def run_dash_server2():
    app_dash2.layout = html.Div([
        dcc.Graph(id='graph', figure=go.Figure())
    ])
    app_dash2.run_server(use_reloader=False,port=8051)

def run_dash_server3():
    app_dash3.layout = html.Div([
        dcc.Graph(id='graph', figure=go.Figure())
    ])
    app_dash3.run_server(use_reloader=False,port=8052)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    dash_thread = threading.Thread(target=run_dash_server)
    dash_thread2 = threading.Thread(target=run_dash_server2)
    dash_thread3 = threading.Thread(target=run_dash_server3)

    dash_thread.start()
    dash_thread2.start()
    dash_thread3.start()

    sys.exit(app.exec())



