import requests
import os
import json
from dotenv import load_dotenv
from pprint import pprint

from datetime import datetime
from time import mktime
from dateutil.relativedelta import relativedelta

from pgAccess import myConnection
from htmlParser import htmlParser

 
class Scraper:
    def __init__(self, params: dict) -> None:
        load_dotenv()
        self.params = params
        self.ids = [33779505]
        self.connection = myConnection()

    def scrapeCars(self) -> None:
        '''
        The main method wich make all of the work - search for good cars
        and return info to google table
        '''
        # get all cars that might help us from API
        # self.get_needed_cars()

        person_dict = {} # id, user_name, phone
        ad_dict = {} # id, add_date, owners_num, last_operation, operation_description, ad_link, user_id

        for id in self.ids:
            # get from ip info about ad for bd
            info = self.get_ad_info(id)
            
            person_dict['id'] = info[1]
            
            ad_dict['id'] = id
            ad_dict['user_id'] = info[1]
            # ad_dict['add_date'] = mktime(datetime.strptime(info[0],
            #                                  '%Y-%m-%d %H:%M:%S').timetuple())

            # ad_dict['add_date'] = datetime.strptime(info[0], '%Y-%m-%d %H:%M:%S')
            ad_dict['add_date'] = info[0]
            ad_dict['ad_link'] = f"https://auto.ria.com/uk{info[2]}"

            # scrape website to get info for bd
            webpageParser = htmlParser(f"https://auto.ria.com/uk{info[2]}")
            
            ad_i = webpageParser.get_ad_info()

            person_dict['user_name'] = ad_i['name']
            person_dict['phone'] = webpageParser.get_phone_numbers()
            ad_dict['owners_num'] = int(ad_i['owners_num'])
            ad_dict['last_operation'] = relativedelta(datetime.now(), datetime.strptime(ad_i["last_operation"], '%d.%m.%Y')).years # difference in years
            ad_dict['operation_description'] = ad_i["operation_description"]

            print(person_dict)
            print(ad_dict)

            # load it to the db
            self.connection.insertUser(person_dict)
            self.connection.insertAd(ad_dict)

        # sort in db by addDate

        # remove unsuitable ad from bd

        # save the rest in google table


    def get_needed_cars(self):
        '''
        Function make GET request to API url and return cars corresponding to the first criteria.
        Parameters are dictionary:
            {name:value}
            which would be converted into string with &

        Return list of id`s of good cars
        '''
        page = 0

        while True:
            # add page to the request
            self.params["page"] = page
            PARAMETERS = self.param_to_string()

            # make a request
            api_url = f"https://developers.ria.com/auto/search?api_key={os.getenv('AUTORIA_API_KEY')}&{PARAMETERS}"
            response = requests.get(api_url)

            if response.ok:
                page_ids = response.json()["result"]["search_result"]
                with open("sample.json", "w") as outfile:
                    outfile.write(json.dumps(response.json(), indent=4))
                
                # count max of pages
                max_page = page_ids["count"] // 100

                # add all ids on all of pages
                self.ids = self.ids + page_ids["ids"]
            else:
                print("Search: Response code is not 200 OK")
            print(f"Page {page} is processed")

            if page == 0:#max_page:
                break

            page += 1

        # save id in the file (ONLY FOR TESTING)
        

    def param_to_string(self) -> str:
        """
        Get parameters dictionary and merge to string:
            name=value&name=value
        Return: string
        """
        answ = ''
        for key in self.params:
            answ += str(key) + '=' + str(self.params[key]) + '&'
        return answ[:-1]

    def get_ad_info(self, id) -> tuple((datetime, int, str)):
        '''
        Get info from API about add. Fill the technical_info with useful info.
        Return (addDate, user_id, linkToView)
        '''

        api_url = f"https://developers.ria.com/auto/info?api_key={os.getenv('AUTORIA_API_KEY')}&auto_id={id}"
        response = requests.get(api_url)

        if response.ok:
            ad = response.json()

            return (ad["addDate"], ad["userId"], ad["linkToView"])
        else:
            print("Ad: Response code is not 200 OK")
            return None


if __name__ == "__main__":
    params = {
        "s_yers[0]": 2018,          # рік випуску від
        "abroad": 2,                # прибрати авто, які не в Україні
        "custom": 1,                # лише розмитнені
        "matched_country": 840,     # пригнали з США
        "under_credit": 0,          # не взято в кредит
        "confiscated_car": 0,       # не конфісковані
        "sellerType": 1,            # продацель - приватна особа
        "top": 0,                   # період подачі - всі
        "saledParam": 2,            # не відображати продані
        "countpage": 100            # скільки оголошень на сторінці
    }

    s = Scraper(params)
    s.scrapeCars()

    # h = htmlParser('https://auto.ria.com/uk/auto_mercedes_benz_s_class_33779505.html')
    # h.get_ad_info()

