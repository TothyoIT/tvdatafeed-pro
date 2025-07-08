## 🚀 Quickstart (v0.2.0+)

from tvdatafeed_pro import TvDatafeed, Interval

tv = TvDatafeed(auto_login=True)
df = tv.get_hist('EURGBP', 'FX_IDC', Interval.in_1_minute, n_bars=50)
print(df.tail())
tv.close()

