from dash_html import plot_candle , plot_finance ,get_sec_indus
import sys

import plotly.graph_objects as go
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from dash import dcc
from dash import html
import dash
import sys     
import threading

app_dash = dash.Dash()  
app_dash2 = dash.Dash()  

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        font = QFont()
        font.setPointSize(9)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1267, 758)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(190, 60, 41, 21))
        self.pushButton.setObjectName("pushButton")

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(40, 60, 141, 22))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.returnPressed.connect(lambda : self.change_stock_graph(self.lineEdit.text()))
        self.pushButton.clicked.connect(lambda : self.change_stock_graph(self.lineEdit.text()))

        self.symbolTopic = QtWidgets.QLabel(self.centralwidget)
        self.symbolTopic.setGeometry(QtCore.QRect(340, 30, 91, 31))
        self.symbolTopic.setObjectName("symbolTopic")
        self.symbolTopic.setFont(font)
        self.symbolName = QtWidgets.QLabel(self.centralwidget)
        self.symbolName.setGeometry(QtCore.QRect(410, 30, 400, 31))
        self.symbolName.setObjectName("symbolName")
        self.symbolName.setFont(font)
        self.sectorTopic = QtWidgets.QLabel(self.centralwidget)
        self.sectorTopic.setGeometry(QtCore.QRect(340, 60, 91, 31))
        self.sectorTopic.setObjectName("sectorTopic")
        self.sectorTopic.setFont(font)
        self.sectorName = QtWidgets.QLabel(self.centralwidget)
        self.sectorName.setGeometry(QtCore.QRect(410, 60, 400, 31))
        self.sectorName.setObjectName("sectorName")
        self.sectorName.setFont(font)
        self.industryTopic = QtWidgets.QLabel(self.centralwidget)
        self.industryTopic.setGeometry(QtCore.QRect(340, 90, 121, 31))
        self.industryTopic.setObjectName("industryTopic")
        self.industryTopic.setFont(font)
        self.industryName = QtWidgets.QLabel(self.centralwidget)
        self.industryName.setGeometry(QtCore.QRect(410, 90, 400, 31))
        self.industryName.setObjectName("industryName")
        self.industryName.setFont(font)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 40, 121, 20))
        self.label.setObjectName("label")

        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(1030, 60, 171, 22))
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(1210, 60, 41, 21))
        self.pushButton_2.setObjectName("pushButton_2")
       # self.pushButton.clicked.connect(lambda : self.change_stock_graph(self.lineEdit.text()))

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(1060, 20, 111, 21))
        self.label_3.setObjectName("label_3")

        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(1050, 40, 131, 21))
        self.label_4.setObjectName("label_4")

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(20, 100, 1231, 611))
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")

        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 61, 20))
        self.label_2.setObjectName("label_2")

        self.comboBox = QtWidgets.QComboBox(self.tab)
        self.comboBox.setGeometry(QtCore.QRect(10, 30, 81, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("Hourly")
        self.comboBox.addItem("Daily")
        self.comboBox.addItem("Monthly")
        self.comboBox.addItem("Quarterly")
        self.comboBox.setCurrentIndex(-1)
        self.comboBox.currentIndexChanged.connect(self.change_interval)

        self.fig=QWebEngineView(self.tab)
        self.fig.load(QUrl("http://localhost:8050"))
        self.fig.setGeometry(QtCore.QRect(10, 60, 1201, 511))
        self.fig.setObjectName("fig")

        self.tabWidget.addTab(self.tab, "")

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.fig2=QWebEngineView(self.tab_2)
        self.fig2.load(QUrl("http://localhost:8051"))
        self.fig2.setGeometry(QtCore.QRect(10, 50, 1201, 521))
        self.fig2.setObjectName("fig2")

        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(20, 20, 91, 16))
        self.label_5.setObjectName("label_5")

        self.comboBox2 = QtWidgets.QComboBox(self.tab_2)
        self.comboBox2.setGeometry(QtCore.QRect(140, 20, 101, 22))
        self.comboBox2.setObjectName("comboBox2")
        self.comboBox2.addItem("Total Asset")
        self.comboBox2.addItem("Net Profit")
        self.comboBox2.addItem("Dividend Yield")
        self.comboBox2.addItem("Revenue")
        self.comboBox2.addItem("ROA & ROE")
        self.comboBox2.setCurrentIndex(-1)
        self.comboBox2.currentIndexChanged.connect(self.change_finance)

        self.tabWidget.addTab(self.tab_2, "")

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1267, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def change_finance(self,index):
        if index == 0:
            # do something for "Option 1"
            app_dash2.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_finance['Total Asset'][0])
        ])
        elif index == 1:
            # do something for "Option 2"
            app_dash2.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_finance['Net Profit'][0])
        ])
        elif index == 2:
            # do something for "Option 3"
            app_dash2.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_finance['Dividend Yield'][0])
        ])
        elif index == 3:
            # do something for "Option 4"
            app_dash2.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_finance['Revenue'][0])
        ])
        elif index == 4:
            # do something for "Option 5"
            app_dash2.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_finance['ROA & ROE'][0])
        ])
        self.fig2.reload()
    

    def change_interval(self,index):
        if index == 0:
            # do something for "Option 1"
            app_dash.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_candle['Hourly'])
        ])
        elif index == 1:
            # do something for "Option 2"
            app_dash.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_candle['Daily'])
        ])
        elif index == 2:
            # do something for "Option 3"
            app_dash.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_candle['Monthly'])
        ])
        elif index == 3:
            # do something for "Option 3"
            app_dash.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_candle['Quarterly'])
        ])
        self.fig.reload()

    def change_stock_graph(self,word):
        self.lineEdit.clear()
        self.pic_candle = plot_candle(word)
        self.pic_finance = plot_finance(word)
        self.comboBox.setCurrentIndex(0)
        self.comboBox2.setCurrentIndex(0)
        sector,industry = get_sec_indus(word)
        self.symbolName.setText(word)
        self.sectorName.setText(sector)
        self.industryName.setText(industry)
        app_dash.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_candle['Hourly'])
        ])
        app_dash2.layout = html.Div([
            dcc.Graph(id='graph', figure=self.pic_finance['Total Asset'][0])
        ])
        self.fig.reload()
        self.fig2.reload()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.symbolTopic.setText(_translate("MainWindow", "Symbol : "))
        self.symbolName.setText(_translate("MainWindow", ""))
        self.sectorTopic.setText(_translate("MainWindow", "Sector : "))
        self.sectorName.setText(_translate("MainWindow", ""))
        self.industryTopic.setText(_translate("MainWindow", "Industry : "))
        self.industryName.setText(_translate("MainWindow", ""))

        self.pushButton.setText(_translate("MainWindow", "Enter"))
        self.label.setText(_translate("MainWindow", "Enter Stock Symbol"))
        self.pushButton_2.setText(_translate("MainWindow", "Enter"))
        self.label_3.setText(_translate("MainWindow", "Enter stock symbol"))
        self.label_4.setText(_translate("MainWindow", "to update lastest price"))
        self.label_2.setText(_translate("MainWindow", "Frequency"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Price"))
        self.label_5.setText(_translate("MainWindow", "Financial statement"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Financial Statement"))


def run_dash_server():
    app_dash.layout = html.Div([
        dcc.Graph(id='graph', figure=go.Figure())
    ])
    app_dash.run_server(debug=True, use_reloader=False,port=8050)

def run_dash_server2():
    app_dash2.layout = html.Div([
        dcc.Graph(id='graph', figure=go.Figure())
    ])
    app_dash2.run_server(debug=True, use_reloader=False,port=8051)

if __name__ == "__main__":
    app_ui = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    dash_thread = threading.Thread(target=run_dash_server)
    dash_thread2 = threading.Thread(target=run_dash_server2)
    dash_thread.start()
    dash_thread2.start()
    sys.exit(app_ui.exec_())

