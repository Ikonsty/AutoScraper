import requests
import os
import json
from dotenv import load_dotenv
from pprint import pprint


load_dotenv()
 
# x = count // 100 + 1
# "page": (1-x)
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

def get_cars_with_param(params):
    '''
    Function make GET request to API url and return cars corresponding to the first criteria.
    Parameters are dictionary:
        {name:value}
        which would be converted into string with &

    Return list of id`s of good cars
    '''
    page = 0
    ids = []

    while True:
        # add page to the request
        params["page"] = page
        PARAMETERS = param_to_string(params)

        # make a request
        api_url = f"https://developers.ria.com/auto/search?api_key={os.getenv('AUTORIA_API_KEY')}&{PARAMETERS}"
        response = requests.get(api_url)

        if response.ok:
            page_ids = response.json()["result"]["search_result"]
            
            # count max of pages
            max_page = page_ids["count"] // 100

            # add all ids on all of pages
            ids = ids + page_ids["ids"]
        else:
            print("Response code is not 200 OK")

        if page == max_page:
            break

        page += 1

        # save id in the file (only for testing)
        with open("sample.json", "w") as outfile:
            outfile.write(json.dumps(ids, indent=4))

def param_to_string(params):
    """
    Get parameters dictionary and merge to string:
        name=value&name=value
    Return: string
    """
    answ = ''
    for key in params:
        answ += str(key) + '=' + str(params[key]) + '&'
    return answ[:-1]

if __name__ == "__main__":
    get_cars_with_param(params)