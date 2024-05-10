# this part is used to load/pull/upload data from SHEETY

import os
import requests
from dotenv import load_dotenv
from flight_search import FlightSearcher
from notification_manager import NotificationRelay

# importing keys from .env file
load_dotenv(os.path.join(os.getcwd(), '.env'))
fs = FlightSearcher()
# lowest price option is for setting the minimal historical price, could be set up to any positive integer
LOWEST_PRICE = 2000
# homecity sets up your city of departure. String with 3letter city IATA code,
HOMECITY = fs.HOMECITY

nr = NotificationRelay()

class DataManager:
    def __init__(self):
        """Initialise index list (named precisely as Sheety docs require) and starts loading process"""
        self.index_list = ["city", "iataCode", "lowestPrice", "lowestPrice6Mo", "departureDate", "nights", "hardlink",
                           "updated"]
        self.json_dict = {"price": {}}
        self.load_table()

    def load_table(self):
        """This is all-in-one function - loads everything from your Google table
        Checks for missing data
        Finds and fills iata codes
        initializes flight search
        and forms up the json for upload"""
        # loading table from sheety
        table_init = requests.get(url=os.getenv("SHEETY_ENDPOINT"),
                                  headers={"Authorization": f"Bearer {os.getenv('SHEETY_AUTH')}"})
        table_init.raise_for_status()
        sheety_table = table_init.json()

        # checking and filling columns on price
        for record in sheety_table["prices"]:
            for column in self.index_list:
                if column not in record:
                    record[column] = ""

        for number, record in enumerate(sheety_table["prices"]):
            print(f"Working on {record['city']}, {number + 1}/{len(sheety_table['prices'])}")
            print(f"Checking IATA Code for {record['city']}")
            (iata_code, city_name) = fs.search_codes(record["city"])

            if record.get("iataCode", "NAN") == "NAN" or len(record["iataCode"]) < 3:
                # IATA codes cannot be shorter than 3
                print(f"Got the Code -> {iata_code}, saving")
                record["iataCode"] = iata_code
                self.json_former(dict_to_write=self.json_dict, iataCode=record["iataCode"])
            elif record["city"].lower() == city_name.lower() and record["iataCode"] != iata_code:
                print(f"Code mismatch found, changing {record['iataCode']} to {iata_code}")
                record["iataCode"] = iata_code
                self.json_former(dict_to_write=self.json_dict, iataCode=record["iataCode"])

            fs.search_flights(iata_code=record["iataCode"], hometown_code=HOMECITY)
            # print(f"Found results -> {fs.search_results}")

            if (len(fs.search_results["destination"][record["iataCode"]]) == 1
                    and isinstance(fs.search_results["destination"][record["iataCode"]][0], str)):
                self.json_former(dict_to_write=self.json_dict,
                                 lowestPrice6Mo="No Results",
                                 departureDate="NA",
                                 nights=0,
                                 hardlink="NA",
                                 updated=fs.search_results["timestamp"])

            else:
                self.json_former(dict_to_write=self.json_dict,
                                 lowestPrice6Mo=fs.search_results["destination"][record["iataCode"]][0]["price"],
                                 departureDate=fs.search_results["destination"][record["iataCode"]][0]["departure_date"],
                                 nights=fs.search_results["destination"][record["iataCode"]][0]["stay"],
                                 hardlink=fs.search_results["destination"][record["iataCode"]][0]["link"],
                                 updated=fs.search_results["timestamp"])

            if record["lowestPrice"] == "" or record["lowestPrice"] == 0:
                record["lowestPrice"] = LOWEST_PRICE
                print(f"Recording standard price {record['lowestPrice']} for ticket fare")

            if len(fs.search_results["destination"][record["iataCode"]]) > 1 and isinstance(fs.search_results["destination"][record["iataCode"]][0]["price"], (int,float)) \
                    and fs.search_results["destination"][record["iataCode"]][0]["price"] < record["lowestPrice"]:
                record["lowestPrice"] = fs.search_results["destination"][record["iataCode"]][0]["price"]
                print(f"Lower price found, changing to {record['lowestPrice']}")
                nr.build_sms(city=record["city"],
                             destination_results=fs.search_results["destination"][record["iataCode"]][0])
            self.json_former(dict_to_write=self.json_dict, lowestPrice=record["lowestPrice"])

            self.upload_data(json_to_upload=self.json_dict,
                             line_number=record["id"])
            # deleting the data from previous iteration
            self.json_dict = {"price": {}}

        # if you want to save server space, comment the line below
        fs.write_to_json(json_outfile=fs.search_results)

        # Call Vonage to add to sms
        nr.send_sms(sms_to_send=nr.sms_message_body)

        # Compose and send mail
        nr.compose_mail(results=fs.search_results)

    def json_former(self, dict_to_write, **kwargs):
        """writes key-value pairs to json for uploading. when everything is written, the file is being uploaded"""
        for key, value in kwargs.items():
            dict_to_write["price"][key] = value
        # print(dict_to_write)
        return dict_to_write

    def upload_data(self, json_to_upload, line_number):
        """Uploads fresh results to G-sheet"""
        # print(f"TO UPLOAD {json_to_upload}")
        send = requests.put(url=f"https://api.sheety.co/7c68a8cf840046569cd779e8b0a19dd0/flightDeals/prices/{line_number}",
                            json=json_to_upload,
                            headers={"Authorization": f"Bearer {os.getenv('SHEETY_AUTH')}",
                                     "Content-Type": "application/json"})
        send.raise_for_status()
