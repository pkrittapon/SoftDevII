import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
view = QWebEngineView()
view.load(QUrl("http://localhost:8050"))
view.show()

sys.exit(app.exec_())

# import sys
# from PyQt5.QtCore import QUrl
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt5 import QtWidgets

# def my_function(text):
#     print("Text entered:", text)
#     textfield.clear()

# app = QtWidgets.QApplication([])
# label = QtWidgets.QLabel("Enter your name:")
# textfield = QtWidgets.QLineEdit()
# textfield.returnPressed.connect(lambda: my_function(textfield.text()))

# layout = QtWidgets.QVBoxLayout()
# layout.addWidget(label)
# layout.addWidget(textfield)
# view = QWebEngineView()

# window = QtWidgets.QWidget()
# window.setLayout(layout)
# window.show()
# app.exec_()

# import dash
# import dash_core_components as dcc
# import dash_html_components as html

# from dash.dependencies import Input, Output
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# from PyQt5 import QtWidgets
# import threading
# import pandas as pd

# def convert_interval(data,period):
#     if period not in ["MS","QS"]:
#          raise Exception("Interval offset is not support. The support interval offset are 'MS' and 'QS'")
#     # Use the resample function to get the open price on the first day of the month
#     new_open = data['open'].resample(period).first()

#     # Use the resample function to get the close price on the last day of the month
#     new_close = data['close'].resample(period).last()

#     # Use the resample function to get the maximum and minimum values for each month
#     new_high = data['high'].resample(period).max()
#     new_low = data['low'].resample(period).min()

#     new_ma50 = data['MA50'].resample(period).mean()
#     new_ma200 = data['MA200'].resample(period).mean()
#     # Use the resample function to get the total volume for each month
#     new_volume = data['volume'].resample(period).sum()
#     # Create a new DataFrame with the monthly stock prices
#     new_prices = pd.DataFrame({'open': new_open,
#                                     'high': new_high,
#                                     'low': new_low,
#                                     'close': new_close,                                
#                                     'volume': new_volume,
#                                     'MA50': new_ma50,
#                                     'MA200': new_ma200,
#                                     })
#     new_prices = new_prices.reset_index()
#     return new_prices

# def get_close_date(data,frequency):
#     if frequency not in ["1d","1h"]:
#          raise Exception("This frequency is not support. The support frequency are '1d' and '1h'")
#     # grab first and last observations from df.date and make a continuous date range from that
#     dt_all = pd.date_range(start=data['x'].iloc[0],end=data['x'].iloc[-1], freq = frequency)

#     # check which dates from your source that also accur in the continuous date range
#     dt_obs = [d.strftime("%Y-%m-%d %H:%M:%S") for d in data['x']]

#     # isolate missing timestamps
#     dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d %H:%M:%S").tolist() if not d in dt_obs]
#     dt_breaks = pd.to_datetime(dt_breaks)
#     return dt_breaks

# def candle_plot(data,close_day,name):
#     #Candlestick Chart
#     candle = go.Candlestick(**data.drop(columns=['volume','MA50','MA200']),yaxis = 'y2',name=name)

#     #Moving Average 50
#     MA50 = go.Scatter(x=data.x, y=data.MA50, line=dict(color='cyan', width=1.5),yaxis = 'y2',name='MA50')

#     #Moving Average 200
#     MA200 = go.Scatter(x=data.x, y=data.MA200, line=dict(color='#E377C2', width=1.5),yaxis = 'y2',name='MA200')

#     #Volume
#     volume = go.Bar(x=data.x,y=data.volume,marker={ "color": "gray"},yaxis = 'y',name='Volume')

#     trace = [candle,MA50,MA200,volume]

#     layout = {
#     "xaxis": {"rangeselector": {
#         "x": 0, 
#         "y": 0.9, 
#         "font": {"size": 13}, 
#         "visible": True, 
#         "bgcolor": "rgba(150, 200, 250, 0.4)", 
#         }}, 
#     "yaxis": {
#         "domain": [0, 0.2], 
#         "showticklabels": False
#     }, 
#     "legend": {
#         "x": 0.3, 
#         "y": 0.9, 
#         "yanchor": "bottom", 
#         "orientation": "h"
#     }, 
#     "margin": {
#         "b": 40, 
#         "l": 40, 
#         "r": 40, 
#         "t": 40
#     }, 
#     "yaxis2": {"domain": [0.2, 0.8]}, 
#     "plot_bgcolor": "rgb(250, 250, 250)",
#     "title":name+" Candlestick Chart"
#     }

#     fig = go.Figure(data=trace, layout=layout)
#     if len(data['x']) <= 1:# If data have 1 data or less than
#         pass
#     elif str(data['x'][1]- data['x'][0]) == '0 days 01:00:00':# If interval is 1 hour
#         fig.update_xaxes(rangebreaks=[dict(dvalue = 60*60*1000, values=close_day)])
#     elif data['x'][1] - data['x'][0] <= pd.Timedelta(days=7):# If interval is less than 7 day
#         fig.update_xaxes(rangebreaks=[dict(values=close_day)])
#     fig.update_layout(hovermode='x')
#     return fig
#     # fig.show()

# def plot_candlestick(symbol):
#     from data.function import Stock
#     print(symbol)
#     textfield.clear()
#     # Fetch data for the stock symbol
#     PTT = Stock(symbol)
#     data = PTT.get_all_stock_price(interval='1h')
#     stock_price_df = pd.DataFrame(data)
#     stock_price_df = stock_price_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})
#     stock_price_df['x'] = pd.to_datetime(stock_price_df['x'])
#     stock_price_df['MA50'] = stock_price_df.close.rolling(50).mean()
#     stock_price_df['MA200'] = stock_price_df.close.rolling(200).mean() 
#     stock_price_df.set_index('x', inplace=True)# Set the Date column as the index of the DataFrame

#     if 'hourly' in ['hourly','daily']:
#         stock_price_df.reset_index(inplace=True)
#     else:
#         stock_price_df = convert_interval(stock_price_df,"MS")# Convert daily data to monyhly or quarterly

#     close_day = get_close_date(stock_price_df,'1h')# Find Close date
#     pic = candle_plot(stock_price_df,close_day,symbol)
#     return pic

# def run_dash_app(symbol):
#     fig = plot_candlestick(symbol)
#     app = dash.Dash()
#     app.layout = html.Div([
#         dcc.Graph(figure=fig)
#     ])

#     if __name__ == '__main__':
#         app.run_server(debug=True, use_reloader=False) 

# app = QtWidgets.QApplication([])
# label = QtWidgets.QLabel("Enter stock symbol:")
# textfield = QtWidgets.QLineEdit()
# textfield.returnPressed.connect(lambda: run_dash_app(textfield.text()))

# layout = QtWidgets.QVBoxLayout()
# layout.addWidget(label)
# layout.addWidget(textfield)

# window = QtWidgets.QWidget()
# window.setLayout(layout)
# window.show()

# # Create and start a new thread for the Dash app
# dash_thread = threading.Thread(target=run_dash_app('PTT'))
# dash_thread.start()

# app.exec_()



