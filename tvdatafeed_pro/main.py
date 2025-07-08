# tvdatafeed_pro/main.py — v0.2.0

import time, json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pathlib import Path
import chromedriver_autoinstaller

class Interval:
    in_1_minute = '1m'
    in_5_minute = '5m'
    in_15_minute = '15m'
    in_1_hour = '1h'
    in_daily = '1d'
    in_weekly = '1W'

class TvDatafeed:
    def __init__(self, auto_login=True, headless=False):
        self.session_file = Path(__file__).parent / "session.json"
        chromedriver_autoinstaller.install()
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        self.browser = webdriver.Chrome(options=options)
        self.logged_in = False
        if auto_login:
            self.login()
    
    def login(self):
        self.browser.get("https://www.tradingview.com/accounts/signin/")
        print("🚀 Log in to TradingView in the opened browser...")
        time.sleep(15)
        self.logged_in = True
        session = {c["name"]: c["value"] for c in self.browser.get_cookies()}
        with open(self.session_file, "w") as f:
            json.dump(session, f)
        print(f"✅ session.json saved ({self.session_file})")
    
    def get_hist(self, symbol, exchange, interval=Interval.in_1_minute, n_bars=100):
        assert self.logged_in, "Must log in first"
        url = f"https://www.tradingview.com/chart/?symbol={exchange}%3A{symbol}"
        self.browser.get(url)
        time.sleep(5)
        script = """
        const data = window.tvWidget.activeChart()
            .getSeries()
            .mainSeries()
            .bars()
            ._value.dataCache;
        return data.slice(-arguments[0]).map(x => ({
            time: new Date(x.v[0]).toISOString(),
            open: x.v[1], high: x.v[2], low: x.v[3],
            close: x.v[4], volume: x.v[5]
        }));
        """
        raw = self.browser.execute_script(script, n_bars)
        df = pd.DataFrame(raw)
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        return df

    def close(self):
        self.browser.quit()
