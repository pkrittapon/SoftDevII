from data.function import Stock, Categories, Location
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime
import numpy as np
from scipy import stats


def convert_interval(data, period):
    if period not in ["W-MON", "MS", "QS"]:
        raise Exception(
            "Interval offset is not support. The support interval offset are 'W-MON', 'MS' and 'QS'")
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


def get_close_date(data, frequency):
    if frequency not in ["1d", "1h"]:
        raise Exception(
            "This frequency is not support. The support frequency are '1d' and '1h'")
    # grab first and last observations from df.date and make a continuous date range from that
    dt_all = pd.date_range(
        start=data['x'].iloc[0], end=data['x'].iloc[-1], freq=frequency)

    # check which dates from your source that also accur in the continuous date range
    dt_obs = [d.strftime("%Y-%m-%d %H:%M:%S") for d in data['x']]

    # isolate missing timestamps
    dt_breaks = [d for d in dt_all.strftime(
        "%Y-%m-%d %H:%M:%S").tolist() if not d in dt_obs]
    dt_breaks = pd.to_datetime(dt_breaks)
    return dt_breaks


def candle_plot_1_pic(data, close_day, name, index, plot_interval):
    # Candlestick Chart
    candle = go.Candlestick(**data.drop(columns=['volume', 'MA50', 'MA200']), yaxis='y2', name=name,
                            increasing_line_color='#00D50E', decreasing_line_color='#FF0000')

    # Moving Average 50
    MA50 = go.Scatter(x=data.x, y=data.MA50, line=dict(
        color='#00FFFF', width=1.5), yaxis='y2', name='MA50')

    # Moving Average 200
    MA200 = go.Scatter(x=data.x, y=data.MA200, line=dict(
        color='#8558FF', width=1.5), yaxis='y2', name='MA200')

    # Volume
    volume = go.Bar(x=data.x, y=data.volume, marker={
                    "color": "lightgrey"}, yaxis='y', name='Volume')

    trace = [candle, MA50, MA200, volume]

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
        "yaxis2": {"domain": [0.2, 0.8]},
        "title": name+" Candlestick Chart",
        'plot_bgcolor': '#1f1f1f',
        'paper_bgcolor': '#1f1f1f'
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

    if len(data['x']) <= 1:  # If data have 1 data or less than
        pass
    elif plot_interval == 'Hourly':  # If interval is 1 hour
        fig.update_xaxes(
            rangebreaks=[dict(dvalue=60*60*1000, values=close_day)])
    elif plot_interval == 'Daily':  # If interval is less than 7 day
        fig.update_xaxes(rangebreaks=[dict(values=close_day)])
    fig.update_layout(hovermode='x unified',
                      font=dict(
                          family="Noto Sans Thai Light",
                          size=16,
                          color="white"
                      ))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    if index == "CRYPTO":
        fig.update_layout(dict(title=name+"-USD "+"Candlestick Chart"))
    return fig
    # fig.show()


def plot_candle(stock_symbol, index):

    plot_interval = ['Hourly', 'Daily', 'Weekly', 'Monthly', 'Quarterly']

    stock_data = Stock(stock_symbol, index)
    pic = {}
    stock_price = []
    for round in plot_interval:
        pull_interval, interval_symbol = '', ''
        if round == 'Hourly':
            pull_interval = '1h'
            stock_price = stock_data.get_all_stock_price(
                interval=pull_interval)
        elif round in ['Daily', 'Weekly', 'Monthly', 'Quarterly']:
            pull_interval = '1d'
            if round == 'Weekly':
                interval_symbol = 'W-MON'
            elif round == 'Monthly':
                interval_symbol = 'MS'
            elif round == 'Quarterly':
                interval_symbol = 'QS'
            else:
                stock_price = stock_data.get_all_stock_price(
                    interval=pull_interval)
        if stock_price == []:
            return {"No data": go.Figure()}
        stock_price_df = pd.DataFrame(stock_price)

        stock_price_df = stock_price_df.rename(
            columns={0: 'x', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        stock_price_df['x'] = pd.to_datetime(stock_price_df['x'])
        stock_price_df['MA50'] = stock_price_df.close.rolling(50).mean()
        stock_price_df['MA200'] = stock_price_df.close.rolling(200).mean()
        # Set the Date column as the index of the DataFrame
        stock_price_df.set_index('x', inplace=True)

        if round in ['Hourly', 'Daily']:
            stock_price_df.reset_index(inplace=True)
        else:
            # Convert daily data to monyhly or quarterly
            stock_price_df = convert_interval(stock_price_df, interval_symbol)

        stock_price_df = stock_price_df.tail(240)
        stock_price_df.reset_index(drop=True, inplace=True)
        if index != "CRYPTO":
            stock_price_df['open'] = stock_price_df['open'].apply(lambda x: "{:.4f}".format(
                x).rstrip('0').rstrip('.') if x % 1 != 0 else "{:.1f}".format(x))
            stock_price_df['high'] = stock_price_df['high'].apply(lambda x: "{:.4f}".format(
                x).rstrip('0').rstrip('.') if x % 1 != 0 else "{:.1f}".format(x))
            stock_price_df['low'] = stock_price_df['low'].apply(lambda x: "{:.4f}".format(
                x).rstrip('0').rstrip('.') if x % 1 != 0 else "{:.1f}".format(x))
            stock_price_df['close'] = stock_price_df['close'].apply(lambda x: "{:.4f}".format(
                x).rstrip('0').rstrip('.') if x % 1 != 0 else "{:.1f}".format(x))
        close_day = get_close_date(
            stock_price_df, pull_interval)  # Find Close date
        pic[round] = candle_plot_1_pic(
            stock_price_df, close_day, stock_symbol, index, round)
    return pic


def finance_scater_plot_1_pic(name, fs, financials_data, index):
    data = fs[["quarter", financials_data]].dropna()
    data.reset_index(drop=True, inplace=True)
    x = list(range(len(data[financials_data])))
    y = list(data[financials_data])
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    x_line = np.linspace(min(x), max(x), len(data[financials_data]))
    y_line = slope * x_line + intercept

    if index == "NASDAQ":
        slope *= -1
    reg_color = "lightgray"
    if float(slope) > 0:
        reg_color = "#00D50E"
    elif float(slope) < 0:
        reg_color = "#FF0000"
    else:
        reg_color = "lightgray"

    data_line = go.Scatter(x=data["quarter"], y=data[financials_data], line=dict(
        color='#0050FF', width=2), mode='lines+markers', name=financials_data)
    regression = go.Scatter(x=data["quarter"], y=y_line, mode='lines', line=dict(
        color=reg_color, width=2), name='Regression Line')

    layout = {
        "yaxis": {
            "domain": [0, 0.9],
            "showticklabels": True
        },
        "legend": {
            "x": 0.4,
            "y": 0.9,
            "yanchor": "bottom",
            "orientation": "h"
        },
        "margin": {
            "b": 60,
            "l": 60,
            "r": 60,
            "t": 60
        },
        'plot_bgcolor': '#1f1f1f',
        'paper_bgcolor': '#1f1f1f'
    }
    # Create a subplot with 2 vertical axes
    fig = go.Figure(data=[data_line, regression], layout=layout)

    fig.update_layout(
        title=name+" "+financials_data,
        hovermode='x unified',
        font=dict(
            family="Noto Sans Thai Light",
            size=16,
            color="white"
        ))
    fig.update_xaxes(tickangle=60)
    return (fig, slope)


def finance_bar_plot_1_pic(name, fs, financials_data):
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
        'plot_bgcolor': '#1f1f1f',
        'paper_bgcolor': '#1f1f1f'
    }

    roa = go.Bar(x=fs["quarter"], y=fs["ROA"],
                 name='ROA%', marker={"color": "#003CFF"})
    roe = go.Bar(x=fs["quarter"], y=fs["ROE"],
                 name='ROE%', marker={"color": "#00C020"})
    fig = go.Figure(data=[roa, roe], layout=layout)
    # Add a title to the plot
    fig.update_layout(
        title=name+" "+"ROA% ROE% by Year",
        hovermode='x unified',
        font=dict(
            family="Noto Sans Thai Light",
            size=16,
            color="white"
        ))

    fig.update_xaxes(tickangle=60)

    return fig


def plot_finance(stock_symbol, index):
    stock_data = Stock(stock_symbol, index)
    fs = stock_data.financial_statement()
    fs = [i[2:] for i in fs]
    if fs == []:
        return {"No data": go.Figure()}
    if index == "CRYPTO":
        return {"No data": go.Figure()}
    elif index == "SET":
        fs = pd.DataFrame(fs).rename(columns={0: 'quarter', 1: 'Total Asset', 2: 'Liabilities', 3: 'Equity', 4: 'Paid Up Capital', 5: 'Revenue',
                                              6: 'Net Profit', 7: 'EPS', 8: 'ROA', 9: 'ROE', 10: 'Net Profit Margin', 11: 'Market Capitalization', 12: 'P/E', 13: 'P/BE', 14: 'Dividend Yield'})
        # fs.drop(fs.tail(1).index,inplace=True)
    elif index == "NASDAQ":
        fs = pd.DataFrame(fs).rename(columns={0: 'quarter', 1: 'Report EPS', 2: 'Total Asset',
                                              3: 'Liabilities', 4: 'Gross Profit', 5: 'Total Revenue', 6: 'Net Income'})
    pics = {}
    if index == "SET":
        for topic in ["Total Asset", "Net Profit", "Liabilities", "Dividend Yield", "Revenue"]:
            pics[topic] = finance_scater_plot_1_pic(
                stock_symbol, fs, topic, index)
        pics["ROA & ROE"] = finance_bar_plot_1_pic(
            stock_symbol, fs, ["ROA", "ROE"]), 0
    if index == "NASDAQ":
        for topic in ["Total Asset", "Gross Profit", "Liabilities", "Total Revenue", "Net Income", "Report EPS"]:
            pics[topic] = finance_scater_plot_1_pic(
                stock_symbol, fs, topic, index)
    return pics


def get_sec_indus(stock_symbol, index):
    if index == "CRYPTO":
        return "Crypto", "Crypto"
    stock_data = Stock(stock_symbol, index)
    return stock_data.sector(), stock_data.industry()


def map_value(value, from_low, from_high, to_low, to_high):
    if from_low == from_high:
        from_high += 1
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low


def plot_spatial(stock_symbol, index):
    stock_location = Stock(stock_symbol, index)
    period_key = ["1 Day", "1 Week", "1 Month", "Year to Date", "All"]
    period = ["1d", "1w", "1m", "y2023", "all"]
    pics = {}
    for key, i in zip(period_key, period):
        data = stock_location.get_stock_location(interval=i)
        pic = plot_spatial_1_pic(stock_symbol, data, key)
        pics |= pic
    if pics == {}:
        return {"No data": go.Figure()}
    return pics


def plot_spatial_1_pic(stock_symbol, data, period):

    if data == []:
        fig = go.Figure(go.Scattermapbox(), layout={
            'mapbox': {'style': "carto-darkmatter"},
            'title': {'text': stock_symbol + "'s news location"},
            'plot_bgcolor': '#1f1f1f',
            'paper_bgcolor': '#1f1f1f',
            'font': {'family': "Noto Sans Thai Light", 'size': 16, 'color': "white"},
        })
        fig.update_layout(mapbox_center={"lat": 20, "lon": 0}, mapbox_zoom=1.5)
        return {period: fig}

    df = pd.DataFrame(data).drop(columns=0).rename(
        columns={1: 'location_name', 2: 'latitude', 3: 'longitude'})
    location_counts = df['location_name'].value_counts()
    df['frequency'] = df['location_name'].map(location_counts)
    df['count'] = df['frequency'].apply(map_value, args=(
        df['frequency'].min(), df['frequency'].max(), 1, 50))
    fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="frequency", size="count", hover_name="location_name",
                            color_continuous_scale=px.colors.sequential.Blues,
                            zoom=1.5, center=dict(lat=20, lon=0),
                            mapbox_style="carto-darkmatter",
                            hover_data={'count': False,  # remove species from hover data
                                        'location_name': False,  # customize hover for
                                        })

    fig.update_layout(title=stock_symbol + "'s news location",
                      plot_bgcolor='#1f1f1f',
                      paper_bgcolor='#1f1f1f',
                      font=dict(family="Noto Sans Thai Light", size=16, color="white"))
    return {period: fig}


def get_all_sector(index):
    cat = Categories(index)
    return cat.get_all_sector()


def get_all_industry(index):
    cat = Categories(index)
    return cat.get_all_industry()


def get_top_symbol(index):
    obj = Categories(index)
    return obj.get_top_stock()


def get_all_symbol(index):
    obj = Categories(index)
    return obj.get_all_stock()


def get_all_statement(index):
    if index == "SET":
        financial_list = ['Total Asset', 'Liabilities', 'Equity', 'Paid Up Capital', 'Revenue', 'Net Profit',
                          'EPS', 'ROA', 'ROE', 'Net Profit Margin', 'Market Capitalization', 'P/E', 'P/BE', 'Dividend Yield']
    elif index == "NASDAQ":
        financial_list = ['Total Asset', 'Liabilities',
                          'Gross Profit', 'Total Revenue', 'Net Income', 'Report EPS']
    else:
        financial_list = []
    return financial_list


def get_all_symbol_in_sector(index, sector):
    obj = Categories(index)
    return obj.get_all_stock_in_sector(sector)


def get_all_symbol_in_industry(index, industry):
    obj = Categories(index)
    return obj.get_all_stock_in_industrial(industry)


def get_all_news(symbol, index, period):
    obj = Stock(symbol, index)
    convert = {'1 Day': '1d', '1 Week': '1w', '1 Month': '1m',
               'Year to Date': 'y2023', 'All': 'all'}
    period = convert[period]
    return obj.get_all_news(interval=period)


def plot_treemap(all_symbol, index):
    symbol = []
    name = []
    sector = []
    industry = []
    market_cap = []

    for i in all_symbol:
        obj = Stock(i, index)
        try:
            temp_market_cap = obj.financial_statement()[-1][13]
        except:
            continue
        symbol.append(i)
        name.append(obj.get_stock_name())
        sector.append(obj.sector())
        industry.append(obj.industry())
        market_cap.append(temp_market_cap)

    df = pd.DataFrame({
        'Company': symbol,
        'Name': name,
        'Sector': sector,
        'Industry': industry,
        'Market Capitalization': market_cap})
    fig = px.treemap(df, path=['Industry', 'Sector',
                     'Company'], values='Market Capitalization', custom_data=[df['Name']])

    fig.update_layout(dict(plot_bgcolor='#1f1f1f',
                           paper_bgcolor='#1f1f1f'))
    fig.update_layout(
        hovermode='x unified',
        font=dict(
            family="Noto Sans Thai Light",
            size=16,
            color="white"
        )
    )
    fig.update_traces(textfont_color='white',
                      hovertemplate='<b>%{label}</b><br>' +
                      'Company: %{customdata[0]}<br>' +
                      'ID: %{id}<br>' +
                      'Market Capitalization: %{value}')

    return fig
