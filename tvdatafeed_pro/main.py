import time
import json
import pandas as pd
import websocket
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Interval:
    in_1_minute = "1"
    in_5_minute = "5"
    in_15_minute = "15"
    in_30_minute = "30"
    in_1_hour = "60"
    in_1_day = "D"
    in_1_week = "W"
    in_1_month = "M"


class TvDatafeed:
    def __init__(self, auto_login=True):
        self.session = str(random.randint(100000, 999999))
        self.ws = None
        self.auth_token = None
        if auto_login:
            self.auth()

    def auth(self):
        input("Manual login. Press Enter to continue...\n\nBrowser opening... DO NOT CLOSE IT. Press Enter when login complete.\n")
        driver = self.__webdriver_init()
        driver.get("https://www.tradingview.com")
        input("✅ After logging in, press Enter to continue...")
        cookies = driver.get_cookies()
        driver.quit()
        for c in cookies:
            if c['name'] == 'sessionid':
                self.auth_token = c['value']
                break
        if not self.auth_token:
            raise Exception("Login failed or sessionid cookie not found")

    def __webdriver_init(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("detach", True)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def __create_connection(self):
        headers = json.dumps({
            "Origin": "https://www.tradingview.com"
        })
        self.ws = websocket.create_connection(
            "wss://data.tradingview.com/socket.io/websocket",
            header=headers
        )
        self.__send_message("set_auth_token", [self.auth_token])

    def __send_message(self, func, params):
        msg = json.dumps({"m": func, "p": params})
        self.ws.send(f"~m~{len(msg)}~m~{msg}")

    def get_hist(self, symbol, exchange, interval=Interval.in_1_minute, n_bars=100):
        self.__create_connection()
        chart_session = f"cs_{self.session}"
        self.__send_message("chart_create_session", [chart_session, ""])
        self.__send_message("quote_create_session", [f"qs_{self.session}"])
        self.__send_message("quote_add_symbols", [f"qs_{self.session}", f"{exchange}:{symbol}"])
        self.__send_message("resolve_symbol", [chart_session, "s1", f"{exchange}:{symbol}"])
        self.__send_message("create_series", [chart_session, "s1", "s1", interval, n_bars])

        raw_data = []
        timeout = time.time() + 15
        while time.time() < timeout:
            try:
                result = self.ws.recv()
                if "timescale_update" in result:
                    j = json.loads(result.split("~m~")[2])
                    if "timescale_update" in j['m']:
                        raw_data = j['p'][1]['s1']
                        break
            except:
                continue

        if not raw_data:
            raise Exception("No data received from TradingView")

        self.ws.close()
        df = pd.DataFrame(raw_data)
        df['time'] = pd.to_datetime(df['v'].apply(lambda x: x['time']), unit='s')
        df.set_index('time', inplace=True)
        df = df[['v']]
        df = df['v'].apply(pd.Series)
        df.rename(columns={'c': 'close', 'o': 'open', 'h': 'high', 'l': 'low', 'v': 'volume'}, inplace=True)
        return df
