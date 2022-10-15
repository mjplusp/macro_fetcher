import time
import yaml, json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from html_table_parser import parser_functions as parser
from webdriver_manager.chrome import ChromeDriverManager

class MacroFetcher:
    def __init__(self, headless = True):
        self.telegram_info: dict
        self.web_info: dict
        self.is_signed_in = False
        self.driver: webdriver.Chrome

        self.__init_settings()
        self.__read_meta()
        self.__init_chrome_driver(headless = headless)

        self.driver.implicitly_wait(time_to_wait=2)
        
  
    def __init_settings(self) -> None:
        with open("app/settings.yaml") as f:
            keys: dict = yaml.load(f, Loader=yaml.FullLoader)
            self.telegram_info: dict = keys.get("telegram")
            self.web_info: dict = keys.get("web-info")

    def __read_meta(self) -> None:
        with open('app/resources/watchlist_meta.json', encoding="utf-8") as d:
            dictData: dict = json.load(d)
            index_meta = dictData.get("index_meta")
            currency_meta = dictData.get("currency_meta")
            bond_meta = dictData.get("bond_meta")
        
        self.index_symbol_list, self.currency_symbol_list, self.bond_symbol_list = [], [], []
        self.symbol_map = {}

        for metas in index_meta:
            self.index_symbol_list.append(metas["original_symbol"])
            self.symbol_map[metas["original_symbol"]+metas["exchange"]] = metas["symbol"]
        for metas in currency_meta:
            self.currency_symbol_list.append(metas["original_symbol"])
            self.symbol_map[metas["original_symbol"]+metas["exchange"]] = metas["symbol"]
        for metas in bond_meta:
            self.bond_symbol_list.append(metas["original_symbol"])
            self.symbol_map[metas["original_symbol"]+metas["exchange"]] = metas["symbol"]

    def __init_chrome_driver(self, headless: bool) -> None:
        chrome_options = webdriver.ChromeOptions()

        chrome_prefs = {}
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

        if headless:
            chrome_options.add_argument("headless")

        chrome_options.add_argument
        ("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70")
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument("--blink-setting=imagesEnable=false")
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--log-level=3')

        # Create Chrome webDriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("Chrome Driver Setup Completed")
        
        return None
    
    def sign_in(self) -> None:
        self.driver.get(self.web_info.get("host") +"/portfolio")
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
    
    def process_table(self, df: pd.DataFrame) -> None:
        columns = ["symbol", "exchange", "last", "open", "high", "low", "daily_change", "daily_pct_change", "volume", "as_of"]

        df["symbol"] = df["unrevised_symbol"].apply(lambda x: x.split("=")[0])

        index_df = df.loc[df['unrevised_symbol'].isin(self.index_symbol_list)].copy()
        index_df = index_df[columns]
        index_df = self.transform_symbol(index_df)

        currency_df = df.loc[df['name'].isin(self.currency_symbol_list)].copy()
        currency_df["symbol"] = currency_df["name"]
        currency_df = currency_df[columns]
        currency_df = self.transform_symbol(currency_df)

        
        bond_df = df.loc[df['symbol'].isin(self.bond_symbol_list)].copy()
        bond_df = bond_df[columns]
        bond_df = self.transform_symbol(bond_df)

        print(index_df)
        print(currency_df)
        print(bond_df)
    
    def transform_symbol(self, df: pd.DataFrame) -> None:
        columns = ["symbol", "last", "open", "high", "low", "daily_change", "daily_pct_change", "volume", "as_of"]
        df.loc[:,"symbol_checker"] = df["symbol"] + df["exchange"]
        df.loc[:,"symbol"] = df["symbol_checker"].apply(lambda x: self.symbol_map[x])
        return df[columns]
    
    def fetch_infinitely(self) -> None:
        self.driver.get(self.web_info.get("host") + self.web_info.get("watchlist-path"))

        while True:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Parse table elements
            watchlist_table_element = soup.find_all("table")[1]

            # Make table 2d
            watchlist_table = parser.make2d(watchlist_table_element)

            # Make pandas dataFrame
            df = pd.DataFrame(data=watchlist_table[1:], columns=watchlist_table[0])
            df.reset_index(drop=True, inplace=True)

            df = df.rename(columns={
                "Name":"name",
                "Symbol":"unrevised_symbol",
                "Exchange":"exchange",
                "Last":"last",
                "Open":"open",
                "High":"high",
                "Low":"low",
                "Chg.":"daily_change",
                "Chg. %":"daily_pct_change",
                "Vol.":"volume",
                "Time":"as_of",
                })
            
            df = df[["name", "unrevised_symbol", "exchange", "last", "open", "high", "low", "daily_change", "daily_pct_change", "volume", "as_of"]]

            # Drop DataFrame
            # df = df.drop(labels=["매수", "매도", "연장시간", "연장시간 (%)", "다음 실적 발표일"], axis=1)

            # print(df)
            # df.to_excel("test.xlsx")
            self.process_table(df)

            time.sleep(60)

if __name__ == "__main__":
    print("Crawler Started")
    
    crawler = MacroFetcher(False)
    crawler.sign_in()

    if crawler.is_signed_in:
        crawler.fetch_infinitely()