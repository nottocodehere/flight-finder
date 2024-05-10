from data_manager import DataManager
from flight_search import FlightSearcher
# from notification_manager import NotificationRelay

dm = DataManager()  # launches everything


# To run the searcher - ensure you have your .env file with filled up keys, it is needed for "python anywhere" service
# moreover. it is a good thing not to leave traces and be secure

# Write your preferred  params in Flight_search.py

# change only keys, not commands or names
# no spaces, no quotes
# for gmail key which comes with spaces, change spaces with underscore, the code will read it properly
# ----------- KEY SCHEMA ----------- #
# export MY_EMAIL=test@gmail.com - gmail goes here
# export ADDRESS1=mailbox@mailserver.org (if you want another recipient for your emails
# export GMAIL_API_KEY=xxxx_xxxx_xxxx_xxxx
# export VONAGE_KEY= yor key for sms service
# export VONAGE_SECRET= your secret key for sms service
# export PHONE_NUMBER= full number with country code, no symbols
# export SHEETY_AUTH= your authorisation token goes here (use the third option with key, bearer type)
# export SHEETY_ENDPOINT= link to your project goes here
# export TEQUILA_API= api key for ticket search
# export TEQUILA_ENDPOINT=https://api.tequila.kiwi.com - no need to change
