# this part is used to load/ data from tequila API
import requests
import os
import datetime as dt
from datetime import date, timedelta
from time import gmtime, strftime
from dotenv import load_dotenv
import json

# importing keys from .env file
load_dotenv(os.path.join(os.getcwd(), '.env'))

class FlightSearcher:
    # enter your city-of-departure IATA code here - ex.: MOW stands for Moscow
    HOMECITY = "VIE"
    # NIGHTS are minimal and maximal duration of your stay
    NIGHTS_MIN = 15
    NIGHTS_MAX = 21
    # how many results you will get for every search. if no results for given destinations, the machine will inform you
    LIMIT_RESULT = 5
    # set stopover cap. Be advised, the number is always +1 to your number of stopovers.
    # 1 is direct flight, 2 means one stopover like VIE->PAR->DOH
    STOPOVERS = 2
    # set currency
    CURRENCY = "USD"

    HOMECITY: str
    NIGHTS_MIN: int
    NIGHTS_MAX: int
    LIMIT_RESULT: int
    STOPOVERS: int
    CURRENCY: str

    # two params for searching. to modify, change dates in timedelta. By default, it searches from tomorrow to 6 months
    DATE_FROM = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    DATE_END = (date.today() + timedelta(days=183)).strftime("%d/%m/%Y")

    def __init__(self):
        """basic init function, with paths to location searcher and main searcher"""
        self.location_query = "https://api.tequila.kiwi.com/locations/query"
        self.search_query = "https://api.tequila.kiwi.com/v2/search"
        self.search_results = {
            "homecity": self.HOMECITY,
            "destination": {},
            "timestamp": strftime("%Y-%m-%d %H:%M:%S", gmtime())
        }

    def search_codes(self, city):
        """This function does the dirty job - searches IATA codes for you """
        iata_code = requests.get(self.location_query, params={"term": city, "location_types": "airport"},
                                 headers={"apikey": os.getenv("TEQUILA_API")})
        iata_code.raise_for_status()
        iata_json = iata_code.json()

        return iata_json["locations"][0]["city"]["code"], iata_json["locations"][0]["city"]["name"]

    def search_flights(self, iata_code, hometown_code=HOMECITY):
        """The function takes IATA CODE and HOMECITY codes and gets a *json for every city->city direction """
        search_params = {
            "fly_from": hometown_code,
            "fly_to": iata_code,
            "date_from": self.DATE_FROM,
            "date_to": self.DATE_END,
            "nights_in_dst_from": self.NIGHTS_MIN,
            "nights_in_dst_to": self.NIGHTS_MAX,
            "curr": self.CURRENCY,
            "max_stopovers": self.STOPOVERS
        }
        # print(search_params)

        search_tickets = requests.get(self.search_query, params=search_params, headers={"apikey": os.getenv("TEQUILA_API"), "accept": "application/json"})
        search_tickets.raise_for_status()
        search_tickets_json = search_tickets.json()

# took down all the current data_saving to avoid heavy space usage (1 json file weights approx 3.5 MB)
#         with open(f"{hometown_code}-{iata_code}_search_results.json", "w") as outfile:
#             json.dump(self.search_tickets_json, outfile, indent=4)

        if len(search_tickets_json["data"]) > self.LIMIT_RESULT:
            output_limit = self.LIMIT_RESULT
        elif 1 > len(search_tickets_json["data"]) > self.LIMIT_RESULT:
            output_limit = len(search_tickets_json["data"])
        else:
            output_limit = 0

        self.search_results["destination"][iata_code] = []
        self.extract_attributes(results=search_tickets_json, limit=output_limit,
                                result_list=self.search_results["destination"][iata_code])

    def extract_attributes(self, results, limit, result_list):
        """extracts attributes from search_results or reports that nothing has been found"""
        if limit > 0:
            for item in results["data"][0:limit]:
                result_list.append({"city": item["cityTo"],
                                    "departure_date": dt.datetime.fromisoformat(item["local_departure"]).strftime("%a, %d %b %Y at %H:%M"),
                                    "price": item["price"],
                                    "stay": item["nightsInDest"],
                                    "link": item["deep_link"]
                                    })
        elif limit == 0:
            result_list.append(f"No flights found to selected dates from {self.DATE_FROM} to {self.DATE_END}")
        # print(f"FINAL RESULTS: {result_list}")

    def write_to_json(self, json_outfile):
        """Records our ticket findings to local json file"""
        with open(f"flights_from_{self.HOMECITY}_search_results.json", "w") as outfile:
            json.dump(json_outfile, outfile, indent=4)
