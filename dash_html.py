from data.function import Stock,Categories,Location
import plotly.graph_objects as go
import pandas as pd
import datetime
import numpy as np
from scipy import stats
import threading


def convert_interval(data,period):
    if period not in ["W-MON","MS","QS"]:
         raise Exception("Interval offset is not support. The support interval offset are 'W-MON', 'MS' and 'QS'")
    # Use the resample function to get the open price on the first day of the month
    new_open = data['open'].resample(period).first()

    # Use the resample function to get the close price on the last day of the month
    new_close = data['close'].resample(period).last()

    # Use the resample function to get the maximum and minimum values for each month
    new_high = data['high'].resample(period).max()
    new_low = data['low'].resample(period).min()

    new_ma50 = data['MA50'].resample(period).mean()
    new_ma200 = data['MA200'].resample(period).mean()
    # Use the resample function to get the total volume for each month
    new_volume = data['volume'].resample(period).sum()
    # Create a new DataFrame with the monthly stock prices
    new_prices = pd.DataFrame({'open': new_open,
                                    'high': new_high,
                                    'low': new_low,
                                    'close': new_close,                                
                                    'volume': new_volume,
                                    'MA50': new_ma50,
                                    'MA200': new_ma200,
                                    })
    new_prices = new_prices.reset_index()
    return new_prices

def get_close_date(data,frequency):
    if frequency not in ["1d","1h"]:
         raise Exception("This frequency is not support. The support frequency are '1d' and '1h'")
    # grab first and last observations from df.date and make a continuous date range from that
    dt_all = pd.date_range(start=data['x'].iloc[0],end=data['x'].iloc[-1], freq = frequency)

    # check which dates from your source that also accur in the continuous date range
    dt_obs = [d.strftime("%Y-%m-%d %H:%M:%S") for d in data['x']]

    # isolate missing timestamps
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d %H:%M:%S").tolist() if not d in dt_obs]
    dt_breaks = pd.to_datetime(dt_breaks)
    return dt_breaks

def candle_plot_1_pic(data,close_day,name):
    #Candlestick Chart
    data = data.tail(200)
    data.reset_index(drop=True, inplace=True)

    candle = go.Candlestick(**data.drop(columns=['volume','MA50','MA200']),yaxis = 'y2',name=name)

    #Moving Average 50
    MA50 = go.Scatter(x=data.x, y=data.MA50, line=dict(color='cyan', width=1.5),yaxis = 'y2',name='MA50')

    #Moving Average 200
    MA200 = go.Scatter(x=data.x, y=data.MA200, line=dict(color='#E377C2', width=1.5),yaxis = 'y2',name='MA200')

    #Volume
    volume = go.Bar(x=data.x,y=data.volume,marker={ "color": "gray"},yaxis = 'y',name='Volume')

    trace = [candle,MA50,MA200,volume]

    layout = {
    "xaxis": {"rangeselector": {
        "x": 0, 
        "y": 0.9, 
        "font": {"size": 13}, 
        "visible": True, 
        "bgcolor": "rgba(150, 200, 250, 0.4)", 
        }}, 
    "yaxis": {
        "domain": [0, 0.2], 
        "showticklabels": False
    }, 
    "legend": {
        "x": 0.3, 
        "y": 0.9, 
        "yanchor": "bottom", 
        "orientation": "h"
    }, 
    "margin": {
        "b": 40, 
        "l": 40, 
        "r": 40, 
        "t": 40
    }, 
    "yaxis2": {"domain": [0.2, 0.8]}, 
    "plot_bgcolor": "rgb(250, 250, 250)",
    "title":name+" Candlestick Chart"
    }

    fig = go.Figure(data=trace, layout=layout)
    fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=7,
                     label="1w",
                     step="day",
                     stepmode="backward"),
                dict(count=1,
                     label="1m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(count=5,
                     label="5y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
    
    if len(data['x']) <= 1:# If data have 1 data or less than
        pass
    elif (data['x'][1]- data['x'][0]) < pd.Timedelta(hours=12):# If interval is 1 hour
        fig.update_xaxes(rangebreaks=[dict(dvalue = 60*60*1000, values=close_day)])
    elif data['x'][1] - data['x'][0] < pd.Timedelta(days=7):# If interval is less than 7 day
        fig.update_xaxes(rangebreaks=[dict(values=close_day)])
    fig.update_layout(hovermode='x')
    return fig
    # fig.show()
def run_fetch_price_hour(stock_obj):
    stock_obj.fetch_stock_price('1h')
def run_fetch_price_day(stock_obj):
    stock_obj.fetch_stock_price('1d')
def update_price_when_enter(stock_symbol,index):
    stock_data = Stock(stock_symbol,index)
    thread1 = threading.Thread(target=run_fetch_price_hour(stock_data))
    thread2 = threading.Thread(target=run_fetch_price_day(stock_data))
    thread1.start()
    thread2.start()

def plot_candle(stock_symbol,index):
    
    plot_interval = ['Hourly','Daily','Weekly','Monthly','Quarterly']

    stock_data = Stock(stock_symbol,index)
    pic = {}
    stock_price = []
    for round in plot_interval:
        pull_interval,interval_symbol = '',''
        if round == 'Hourly':
            pull_interval = '1h'
            stock_price = stock_data.get_all_stock_price(interval=pull_interval)
        elif round in ['Daily','Weekly','Monthly','Quarterly']:
            pull_interval = '1d'
            if round == 'Weekly':
                interval_symbol = 'W-MON'
            elif round == 'Monthly':
                interval_symbol = 'MS'
            elif round == 'Quarterly':
                interval_symbol = 'QS'
            else:
                stock_price = stock_data.get_all_stock_price(interval=pull_interval)
        if stock_price == []:
            return {"No data": go.Figure()}
        stock_price_df = pd.DataFrame(stock_price)
        
        stock_price_df = stock_price_df.rename(columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close',5:'volume'})
        stock_price_df['x'] = pd.to_datetime(stock_price_df['x'])
        stock_price_df['MA50'] = stock_price_df.close.rolling(50).mean()
        stock_price_df['MA200'] = stock_price_df.close.rolling(200).mean() 
        stock_price_df.set_index('x', inplace=True)# Set the Date column as the index of the DataFrame
        if round in ['Hourly','Daily']:
            stock_price_df.reset_index(inplace=True)
        else:
            stock_price_df = convert_interval(stock_price_df,interval_symbol)# Convert daily data to monyhly or quarterly
        

        close_day = get_close_date(stock_price_df,pull_interval)# Find Close date
        pic[round]=candle_plot_1_pic(stock_price_df,close_day,stock_symbol)
    return pic

def finance_scater_plot_1_pic(name,fs,financials_data):
    data = fs.dropna()
    data.reset_index(drop=True, inplace=True)
    x = list(range(len(data[financials_data])))
    y = list(data[financials_data])
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    x_line = np.linspace(min(x), max(x), len(data[financials_data]))
    y_line = slope * x_line + intercept
    # Create the line object

    data_line = go.Scatter(x=data["quarter"],y=data[financials_data],mode='lines+markers', name=financials_data)
    regression = go.Scatter(x=data["quarter"], y=y_line, mode='lines', name='Regression Line')

    layout = {
        "yaxis": {
            "domain": [0, 0.7], 
            "showticklabels": True
        }, 
        "legend": {
            "x": 0.4, 
            "y": 0.8, 
            "yanchor": "bottom", 
            "orientation": "h"
        }, 
        "margin": {
            "b": 40, 
            "l": 40, 
            "r": 40, 
            "t": 40
        }, 
        "plot_bgcolor": "rgb(250, 250, 250)"
        }
    # Create a subplot with 2 vertical axes
    fig = go.Figure(data = [data_line,regression],layout=layout)

    fig.update_layout(
        title=name+" "+financials_data,
        hovermode='x'
    )
    fig.update_xaxes(tickangle=60)
    return (fig,slope)

def finance_bar_plot_1_pic(name,fs,financials_data):
    layout = {
        "yaxis": {
            "domain": [0, 0.8], 
            "showticklabels": True
        }, 
        "legend": {
            "x": 0.4, 
            "y": 0.9, 
            "yanchor": "bottom", 
            "orientation": "h"
        }, 
        "margin": {
            "b": 40, 
            "l": 40, 
            "r": 40, 
            "t": 40
        }, 
        "plot_bgcolor": "rgb(250, 250, 250)"
        }

    roa = go.Bar(x=fs["quarter"],y=fs["ROA"],name='ROA%')
    roe = go.Bar(x=fs["quarter"],y=fs["ROE"],name='ROE%')
    fig = go.Figure(data = [roa,roe],layout=layout)
    # Add a title to the plot
    fig.update_layout(
        title=name+" "+"ROA% ROE% by Year",
        hovermode='x'
    )
    fig.update_xaxes(tickangle=60)

    return fig

def plot_finance(stock_symbol,index):
    stock_data = Stock(stock_symbol,index)
    fs = stock_data.financial_statement()
    fs = [i[2:] for i in fs]
    if fs == []:
        return {"No data":go.Figure()}
    if index == "CRYPTO":
        return {"No data":go.Figure()}
    elif index == "SET":
        fs = pd.DataFrame(fs).rename(columns={0:'quarter',1:'Total Asset',2:'Liabilities',3:'Equity',4:'Paid Up Capital',5:'Revenue',6:'Net Profit',7:'EPS',8:'ROA',9:'ROE',10:'Net Profit Margin',11:'Market Capitalization',12:'P/E',13:'P/BE',14:'Dividend Yield'})
        fs.drop(fs.tail(1).index,inplace=True)
    elif index == "NASDAQ":
        fs = pd.DataFrame(fs).rename(columns={0:'quarter',1:'Report EPS',2:'Total Asset',3:'Liabilities',4:'Gross Profit',5:'Total Revenue',6:'Net Income'})
    pics = {}
    if index == "SET":
        for topic in ["Total Asset","Net Profit","Liabilities","Dividend Yield","Revenue"]:
            pics[topic] = finance_scater_plot_1_pic(stock_symbol,fs,topic)
        pics["ROA & ROE"] = finance_bar_plot_1_pic(stock_symbol,fs,["ROA","ROE"]),0
    if index == "NASDAQ":
         for topic in ["Total Asset","Gross Profit","Liabilities","Total Revenue","Net Income","Report EPS"]:
            pics[topic] = finance_scater_plot_1_pic(stock_symbol,fs,topic)
    return pics

def get_sec_indus(stock_symbol,index):
    if index == "CRYPTO":
        return "Crypto","Crypto"
    stock_data = Stock(stock_symbol,index)
    return stock_data.sector(),stock_data.industry()

def plot_spatial(stock_symbol,index):
    stock_location = Location(index)
    data = stock_location.get_stock_location(stock_symbol)
    if data == []:
        return {"No data":go.Figure()}
    df = pd.DataFrame(data).drop(columns=0).rename(columns={1:'location_name',2:'lat',3:'lon'})
    location_counts = df['location_name'].value_counts()
    df['count'] = df['location_name'].map(location_counts)

    fig = go.Figure(data=go.Scattergeo(
                lon = df['lon'],
                lat = df['lat'],
                text = df['location_name'],
                mode = 'markers',
                name='location',
                marker = dict(
                    size = df['count'] * 6, # adjust marker size based on count
                    sizemode = 'diameter',
                    sizemin = 5,
                    color = df['count'], # map color to count
                    colorscale = 'Blues_r', # set diverging color scale
                    reversescale = True,
                    colorbar_title = 'Count',
                    colorbar_thickness = 20,
                    colorbar_len = 0.6
                ),
                hovertemplate = '%{text}<br>Frequency: %{marker.color}'
            ))

    fig.update_layout(
            title = stock_symbol+"'s news location",
            geo_scope='world',
            geo = dict(
                showland = True,
                landcolor = 'rgb(200, 200, 200)')
        )
    return {"Spatial":fig}