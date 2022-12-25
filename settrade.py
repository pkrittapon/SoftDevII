from settrade_v2 import Investor
investor = Investor(
    app_id="6r8eutNBUR9tOj3Z",
    app_secret="AKHhWxddgqt+v5OHir83wBJ4CRMXIQFvGOtnzPocqLYe",
    broker_id="SANDBOX",
    app_code="SANDBOX",
    is_auto_queue = False
)
realtime = investor.RealtimeDataConnection()

market = investor.MarketData()

res = market.get_candlestick(
symbol="AOT",
interval="1d",
start="2015-12-24T00:00",
end="2016-12-24T00:00",
normalized=True,  
)
from datetime import datetime
for i in res['time']:
    timestamp = i
    date_time = datetime.fromtimestamp(timestamp)
    print(date_time)

# print(res['time'])
