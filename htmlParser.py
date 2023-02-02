from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
import time
from pprint import pprint
from bs4 import BeautifulSoup

class htmlParser:
    def __init__(self, page) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--incognito')
        self.options.add_argument('--headless')
    
        self.driver = webdriver.Chrome('/snap/bin/chromium.chromedriver', options=self.options) # f"{os.getenv('CHROME_PATH')}" / service=Service(ChromeDriverManager().install())
        self.page = page
        self.driver.get(self.page)


    def get_phone_numbers(self) -> str:
        '''
        On the Page:
        Uses selenium to open a phone number and then read it with BeautifulSoup
        Return str with number
        '''
        
        show_phone = self.driver.find_element(By.CLASS_NAME, "phone_show_link")

        if show_phone.is_displayed():
            self.driver.execute_script('arguments[0].click();', show_phone)
            time.sleep(1)
    
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        numbers = soup.find("div", class_="popup-successful-call-desk")
        return numbers.text


    def get_ad_info(self) -> dict:
        '''
        Return: seller name,                                    str
                number of owners of the car,                    int
                last operation (how many years in the past),    str
                description of operation                        str
        '''

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        ad_info = {}

        name = soup.find("div", class_="seller_info_name")

        ad_info['name'] = name.text

        # check if car is tracked by MIA or is from USA
        if soup.find('span', string='за реєстрами МВС'):
            owners_num_label = soup.find("span", string='Кількість власників')
            ad_info["owners_num"] = owners_num_label.parent.find("span", class_='argument').text

            last_operation_label = soup.find("span", string='Остання операція')
            ad_info["last_operation"] = last_operation_label.parent.find("span", class_="argument").text.split(" ")[0]
            
            if last_operation_label.parent.find("span", class_="size13"):
                ad_info["operation_description"] = last_operation_label.parent.find("span", class_="size13").text
            else:
                ad_info["operation_description"] = ""
        else:
            ad_info["owners_num"] = 0
            ad_info["last_operation"] = ""
            ad_info["operation_description"] = ""
        return ad_info
