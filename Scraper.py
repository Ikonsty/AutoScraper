import requests
import os
import json

from datetime import datetime, timezone
from dotenv import load_dotenv
from pprint import pprint
from pgAccess import myConnection

 
class Scraper:
    def __init__(self, params: dict) -> None:
        load_dotenv()
        self.params = params
        self.ids = []
        self.connection = myConnection()

    def scrapeCars(self) -> None:
        '''
        The main method wich make all of the work - search for good cars
        and return info to google table
        '''
        # get all cars that might help us from API
        self.get_needed_cars()

        person_dict = {} # id, user_name, phone
        ad_dict = {} # id, add_date, owners_num, last_operation, operation_description, ad_link, user_id

        for id in self.ids:
            # get from ip info about ad for bd
            info = self.get_ad_info(id)
            
            person_dict['id'] = info[1]
            
            ad_dict['user_id'] = info[1]
            ad_dict['add_date'] = info[0]
            ad_dict['ad_link'] = f"https://auto.ria.com/uk{info[2]}"

            # scrape website to get info for bd

            # load it to the db
            
            # s.insert_data_db({'id': 323, 'name': 'Ilya', 'phone': '0972846323'})
            # dt = datetime.now(timezone.utc)
            # cur.execute('INSERT INTO mytable (mycol) VALUES (%s)', (dt,))

        # sort in db by addDate

        # remove unsuitable ad from bd

        # save the rest in google table

        # PART FOR TESTING ONLY

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
                
                # count max of pages
                max_page = page_ids["count"] // 100

                # add all ids on all of pages
                self.ids = self.ids + page_ids["ids"]
            else:
                print("Search: Response code is not 200 OK")

            if page == 0:#max_page:
                break

            page += 1

            print(f"Page {page} is processed")


            # save id in the file (ONLY FOR TESTING)
            with open("sample.json", "w") as outfile:
                outfile.write(json.dumps(self.ids, indent=4))

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

    def insert_data_db(self, values: dict) -> None:
        self.connection.insertUser(values)


if __name__ == "__main__":
    params = {
        "s_yers": 2018,
        "abroad": 2,
        "custom": 0,
        "matched_country": 840,
        "under_credit": 0,
        "confiscated_car": 0,
        "sellerType": 1,
        "top": 0,
        "saledParam": 2,
        "countpage": 100
    }

    s = Scraper(params)
    s.scrapeCars()