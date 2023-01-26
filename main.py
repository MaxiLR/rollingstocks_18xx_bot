from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import gspread
import requests
from bs4 import BeautifulSoup
from time import sleep


ROOM_URL = "https://18xx.games/game/"
TEST_ROOM_URL = "https://18xx.games/hotseat/"

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
# options.add_argument('--headless')  # Browser doesn't show up
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_argument('--start-maximized')
options.add_argument('--disable-extension')
options.add_argument("--remote-debugging-port=9222")
options.add_argument(
    '--user-data-dir=Chrome_session_save')


def GET_SHEETS():
    API_Account = gspread.service_account(filename='credentials.json')
    GoogleWorksheets = API_Account.open('Test').worksheets()
    return GoogleWorksheets


def GET_DATA(Worksheet):
    List_of_Dicts = Worksheet.get_all_records()
    DF = pd.DataFrame(List_of_Dicts)
    return DF


if __name__ == '__main__':
    SHEETS = GET_SHEETS()

    for SHEET in SHEETS:
        ROOM_ID = SHEET.title
        ROOM_DATA_DF = GET_DATA(SHEET)
        GS_COMPANIES = list()

        GS_COMPANIES.append(ROOM_DATA_DF.iloc[0, 0])
        GS_COMPANIES.append(ROOM_DATA_DF.iloc[1, 0])
        GS_COMPANIES.append(ROOM_DATA_DF.iloc[2, 0])

        HIGHEST_BIDS = list()

        HIGHEST_BIDS.append(ROOM_DATA_DF.iloc[0, 1])
        HIGHEST_BIDS.append(ROOM_DATA_DF.iloc[1, 1])
        HIGHEST_BIDS.append(ROOM_DATA_DF.iloc[2, 1])

        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)

        driver.get(TEST_ROOM_URL + ROOM_ID)

        WP_COMPANIES_CARDS = []
        ALLDIVS = wait.until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "div")))

        for DIV in ALLDIVS:
            if (DIV.get_attribute("style") == "display: inline-block; vertical-align: top;"):
                WP_COMPANIES_CARDS.append(DIV)

        USERNAME = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div[1]/div/a[2]"))).text.split(' ')[1]
        USERNAME = USERNAME[1:-1]

        PLAYERLIST = driver.find_elements(By.TAG_NAME, "li")[5:8]

        for P in PLAYERLIST:
            if (P.find_element(By.TAG_NAME, "a").text == USERNAME):
                PLAYER_WebElement = P
                break

        while (driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div/h4").text.split(',')[1] == " Phase 1 - Investment Round - Sell then Buy Shares"):
            if (PLAYER_WebElement.get_attribute("style") == "float: left; list-style: none; padding-right: 1rem; text-decoration: underline; font-size: 1.1rem; font-weight: bold;"):
                # USER'S TURN
                SELECTED_CARD = 0
                count = 0
                for CARD in WP_COMPANIES_CARDS:
                    count += 1
                    if (len(CARD.find_elements(By.TAG_NAME, "button")) > 0):
                        SELECTED_CARD = CARD
                        break
                    
                if (SELECTED_CARD == 0):
                    # SELECT A CARD IF NOT SELECTED
                    count = 1
                    SELECTED_CARD = driver.find_element(
                        By.XPATH, "/html/body/div[1]/div[4]/div/div/div[6]/div[1]/div[1]")
                    SELECTED_CARD.click()
                    
                SELECTED_CARD_COMPANY_NAME = SELECTED_CARD.find_element(
                    By.XPATH, f"/html/body/div[1]/div[4]/div/div/div[6]/div[{count}]/div/div[1]/div[1]/div[1]").text
                HIGHEST_BID_ON_SELECTED_CARD = int(ROOM_DATA_DF.iloc[ROOM_DATA_DF.loc[ROOM_DATA_DF["COMPANY NAMES"] == SELECTED_CARD_COMPANY_NAME].index[0], 1])
                CURRENT_BID = int(driver.find_element(By.CLASS_NAME, "margined_bottom").find_element(
                    By.TAG_NAME, "input").get_attribute("min"))

                if (CURRENT_BID <= HIGHEST_BID_ON_SELECTED_CARD):
                    driver.find_element(By.CLASS_NAME, "margined_bottom").find_element(By.TAG_NAME,"button").click()
                else:
                    driver.find_element(
                        By.XPATH, "/html/body/div[1]/div[4]/div/div/div[5]/button").click()
                        
            sleep(5)
        driver.quit()
