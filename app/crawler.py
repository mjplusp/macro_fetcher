import time
import yaml, json
import pandas as pd
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from html_table_parser import parser_functions as parser
from webdriver_manager.chrome import ChromeDriverManager
from storage.sqlite_connector import Database
import utils
import resources.queries as q

class MacroFetcher:
    def __init__(self, headless=True, driver_path="chromedriver"):
        self.telegram_info: dict
        self.web_info: dict
        self.is_signed_in = False
        self.driver: webdriver.Chrome

        self.today = utils.get_day_and_time()[0]
        self.week_start_date: str
        self.week_end_date: str
        self.__set_week_start_end_date()

        self.db_dir: str
        self.db_name: str
        self.db: Database

        self.__init_settings()
        self.__init_chrome_driver(headless=headless, driver_path=driver_path)

        self.driver.implicitly_wait(time_to_wait=2)

    def __init_settings(self) -> None:
        with open("app/settings.yaml") as f:
            keys: dict = yaml.load(f, Loader=yaml.FullLoader)
            self.telegram_info: dict = keys.get("telegram")
            self.web_info: dict = keys.get("web-info")

            self.db_dir = keys.get("db")["path"]
            self.db_name = self.week_start_date + "_" + self.week_end_date + ".sqlite3"
            self.db = Database(self.db_dir + "/" + self.db_name)
            self.__prepare_db()

    def __set_week_start_end_date(self) -> None:
        dt = datetime.strptime(self.today, "%Y%m%d")
        start = dt - timedelta(days=dt.weekday())
        end = start + timedelta(days=6)

        self.week_start_date = start.strftime("%Y%m%d")
        self.week_end_date = end.strftime("%Y%m%d")

        print(f"today: {self.today}, week start: {self.week_start_date}, week end: {self.week_end_date}")

    def __read_meta(self) -> None:
        with open("app/resources/watchlist_meta.json", encoding="utf-8") as d:
            meta_list: list = json.load(d)

        meta_df = pd.DataFrame(meta_list)
        self.__insert_df(meta_df, "macro_meta")

        self.index_symbol_list, self.currency_name_list, self.bond_symbol_list = [], [], []
        self.symbol_map = {}
        self.name_map = {}

        for meta in meta_list:
            self.symbol_map[meta["original_symbol"] + meta["exchange"]] = meta["symbol"]
            self.name_map[meta["name_kr"]] = meta["symbol"]

            meta_type = meta["type"]

            if meta_type == "index":
                self.index_symbol_list.append(meta["original_symbol"])
            elif meta_type == "currency":
                self.currency_name_list.append(meta["name_kr"])
            elif meta_type == "bond":
                self.bond_symbol_list.append(meta["original_symbol"])

    def __insert_df(self, source: pd.DataFrame, table) -> None:
        self.db.cursor.execute("BEGIN TRANSACTION")
        for _, row in source.iterrows():       
            self.db.cursor.execute('INSERT INTO '+table+' ('+ str(', '.join(source.columns))+ ') VALUES '+ str(tuple(row.values))) 
        self.db.cursor.execute("END TRANSACTION")

    def __prepare_db(self) -> None:
        self.db.cursor.execute(q.market_index_table)
        self.db.cursor.execute(q.fx_rate_table)
        self.db.cursor.execute(q.bond_yield_table)
        self.db.cursor.execute(q.macro_meta_table)
        self.__read_meta()

    def __db_roll_needed(self, date) -> bool:
        if date > self.week_end_date:
            print(f"date: {date}, week end date: {self.week_end_date}. DB Roll needed")
            return True

    def __roll_db(self, today) -> None:
        if self.__db_roll_needed(today):
            self.today = today
            self.__set_week_start_end_date()

            self.db.close()
            self.db_name = self.week_start_date + "_" + self.week_end_date + ".sqlite3"
            self.db = Database(self.db_dir + "/" + self.db_name)
            self.__prepare_db()

    def __init_chrome_driver(self, headless: bool, driver_path) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_prefs = {}
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

        if headless:
            chrome_options.add_argument("headless")

        chrome_options.add_argument
        (
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"
        )
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument("--blink-setting=imagesEnable=false")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--log-level=3")

        # Create Chrome webDriver
        self.driver = webdriver.Chrome(
            executable_path=driver_path,
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )
        print("Chrome Driver Setup Completed")

        return None

    def sign_in(self) -> None:
        self.driver.get(self.web_info.get("host") + "/portfolio")
        try:
            id_element = self.driver.find_element(By.ID, "loginFormUser_email")
            id_element.send_keys(self.web_info.get("email"))

            password_element = self.driver.find_element(By.ID, "loginForm_password")
            password_element.send_keys(self.web_info.get("password"))

            time.sleep(1)

            self.driver.execute_script("loginPageFunctions.submitLogin();")

            print("Login Successful")
            self.is_signed_in = True

        except Exception:
            print("Login Failed")

    def enter_watchlist(self) -> None:
        self.driver.get(self.web_info.get("host") + self.web_info.get("watchlist-path"))

    def process_table(self, df: pd.DataFrame, today: str) -> None:
        columns = [
            "date",
            "time",
            "symbol",
            "last",
            "open",
            "high",
            "low",
            "daily_change",
            "daily_pct_change",
            "volume",
            "created_at",
        ]

        # Bond Symbol 전처리
        df["symbol"] = df["unrevised_symbol"].apply(lambda x: x.split("=")[0])

        # Index의 경우 Symbol을 그대로 이용
        index_df = df.loc[df["symbol"].isin(self.index_symbol_list)].copy()
        index_df["symbol"] = (index_df["symbol"] + index_df["exchange"]).apply(lambda x: self.symbol_map[x])
        index_df = index_df[columns]

        # Currency의 경우 Name이 곧 Symbol
        currency_df = df.loc[df["name"].isin(self.currency_name_list)].copy()
        currency_df["symbol"] = currency_df["name"].apply(lambda x: self.name_map[x])
        currency_df = currency_df[columns]

        bond_df = df.loc[df["symbol"].isin(self.bond_symbol_list)].copy()
        bond_df = bond_df[columns]

        # Select Only Updated Data
        _index_df = pd.read_sql(f"SELECT time, symbol FROM market_index WHERE date = '{today}'", self.db.conn)
        _currency_df = pd.read_sql(f"SELECT time, symbol FROM fx_rate WHERE date = '{today}'", self.db.conn)
        _bond_df = pd.read_sql(f"SELECT time, symbol FROM bond_yield WHERE date = '{today}'", self.db.conn)

        macro_df_today = pd.concat([_index_df, _currency_df, _bond_df])
        time_code_pair_list = (macro_df_today["time"] + macro_df_today["symbol"]).to_list()
        index_df = index_df[~(index_df["time"] + index_df["symbol"]).isin(time_code_pair_list)]
        currency_df = currency_df[~(currency_df["time"] + currency_df["symbol"]).isin(time_code_pair_list)]
        bond_df = bond_df[~(bond_df["time"] + bond_df["symbol"]).isin(time_code_pair_list)]

        # Save to DB
        self.__insert_df(index_df, "market_index")
        self.__insert_df(currency_df, "fx_rate")
        self.__insert_df(bond_df, "bond_yield")

    def fetch_data(self) -> None:
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Parse table elements
        watchlist_table_element = soup.find_all("table")[1]
        (today, current_hms) = utils.get_day_and_time()

        self.__roll_db(today)

        if today != self.today:
            self.today = today

        # Make table 2d
        watchlist_table = parser.make2d(watchlist_table_element)

        # Make pandas dataFrame
        df = pd.DataFrame(data=watchlist_table[1:], columns=watchlist_table[0])
        # Filter yesterday data
        df = df.loc[df["시간"].str.match(r"[0-2][0-9]:[0-9][0-9]:[0-9][0-9]")]
        df["시간"] = df["시간"].apply(lambda x: x.replace(":", ""))
        df = df[df["시간"] < current_hms]
        # Type change: string -> float
        df["종가"] = df["종가"].apply(lambda x: float(x.replace(",", "")))
        df["오픈"] = df["오픈"].apply(lambda x: float(x.replace(",", "")))
        df["고가"] = df["고가"].apply(lambda x: float(x.replace(",", "")))
        df["저가"] = df["저가"].apply(lambda x: float(x.replace(",", "")))
        df["변동"] = df["변동"].apply(lambda x: float(x.replace(",", "").replace("+", "")))
        df["변동 %"] = df["변동 %"].apply(lambda x: float(x.replace(",", "").replace("+", "").replace("%", "")))

        df.reset_index(drop=True, inplace=True)
        df["date"] = today
        df["created_at"] = current_hms

        df = df.rename(
            columns={
                "종목": "name",
                "기호": "unrevised_symbol",
                "거래소": "exchange",
                "종가": "last",
                "오픈": "open",
                "고가": "high",
                "저가": "low",
                "변동": "daily_change",
                "변동 %": "daily_pct_change",
                "거래량": "volume",
                "시간": "time",
            }
        )

        df = df[
            [
                "date",
                "time",
                "name",
                "unrevised_symbol",
                "exchange",
                "last",
                "open",
                "high",
                "low",
                "daily_change",
                "daily_pct_change",
                "volume",
                "created_at",
            ]
        ]

        self.process_table(df, today)

        print(f"Data Fetched at {utils.get_day_and_time()}")


if __name__ == "__main__":
    print("Crawler Started")

    crawler = MacroFetcher(False)
    crawler.sign_in()

    if crawler.is_signed_in:
        crawler.enter_watchlist()
        crawler.fetch_data()
