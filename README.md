# flight-finder
Helps you to find the cheapest airline ticket, notifies you about hot deals via SMS and email 

The solution is based on services provided by: 
a) https://tequila.kiwi.com/ - helps you to search for airline tickets
b) https://sheety.co/ - SHEETY API, which allows you to read and write pricing data in google sheets
c) https://www.vonage.com/ - Vonage, a service for sms notifications
d) https://docs.google.com/spreadsheets/create + mail.google.com - to set up a sheet and work with mail 

Other comments / schemas are written inside .py files

IMPORTANT: to work properly you have to set up an .env file in the root dir and use dotenv to read id and pass to os library
