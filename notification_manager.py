# this part is the notifier - SMS and Email - just two simple functions SMS and e-mail

import vonage
from dotenv import load_dotenv
import os
import smtplib
from flight_search import FlightSearcher
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv(os.path.join(os.getcwd(), '.env'))
fs = FlightSearcher()


class NotificationRelay:
    SMTP_CRED = smtplib.SMTP("smtp.gmail.com", port=587)

    def __init__(self):
        self.results_sms = ""
        self.sms_message_body = ""

    def build_sms(self, city, destination_results):
        """SMS sender (VONAGE)
        the line takes the cheapest picks for every city in your table and adds the line
        to the message only if price has dropped"""
        self.results_sms += f"-> {city}, from {destination_results['price']} {fs.CURRENCY}, \
        for {destination_results['stay']} nights, departing {destination_results['departure_date']}\n"
        if len(self.results_sms) > 0:
            self.sms_message_body = (
                f"Today's hot deals from {fs.search_codes(fs.HOMECITY)[1]}({fs.HOMECITY}): \n"
                f"{self.results_sms}"
            )

    def send_sms(self, sms_to_send):
        """function checks if there is something to send and does so,
        otherwise it says in the console that sms is not needed"""
        if len(self.sms_message_body) > 0:
            client = vonage.Client(key=os.getenv("VONAGE_KEY"), secret=os.getenv("VONAGE_SECRET"))
            sms = vonage.Sms(client)

            response_data = sms.send_message(
                {
                    "from": "Vonage APIs",
                    "to": os.getenv("PHONE_NUMBER"),
                    "text": sms_to_send,
                }
            )
            if response_data["messages"][0]["status"] == "0":
                print("Message sent successfully.")
            else:
                print(f"Message failed with error: {response_data['messages'][0]['error-text']}")

        else:
            print("No hot deals found, skipping sms")

    def compose_mail(self, results):
        """Function uses search results to build up a message"""
        # building email header
        message = MIMEMultipart("alternative")
        message["Subject"] = f"{date.today().strftime('%a, %d %b %Y')} - Airlines' top picks from {fs.search_codes(fs.HOMECITY)[1]}({fs.HOMECITY}"
        message["From"] = os.getenv("MY_EMAIL")
        message["To"] = os.getenv("ADDRESS1")
        # building the html version
        html_message_header = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <body>
                    <h1>Flights from {fs.search_codes(fs.HOMECITY)[1]}({fs.HOMECITY})</h1>"""
        html_message_end = f"""<p>Have a nice journey!</p><br> 
        
        <p>The tool brought you by <b>@nottocodehere</b> and Kiwi.com,  Sheety.co, Google.<p>
         </body>
         </html>"""
        html_message_part2 = ""

        for city in results["destination"]:
            print(f"COMPOSING MAIL FOR {city}")
            html_message_part2 += f"""<h2>Flights from {fs.search_codes(city)[1]}({city})</h2><br>"""

            if len(results["destination"][city]) == 1:
                html_message_part2 += f'''<p>❌︎<b> {results["destination"][city]}</b></p>
                <br>'''
            elif len(results["destination"][city]) > 1:
                for number, flight in enumerate(results["destination"][city]):
                    print(f"COMPOSING MAIL FOR FLIGHT > {flight}")

                    html_message_part2 += f'''<p>✅︎<b>{number+1}.</b> Departure: {flight["departure_date"]}, {flight["stay"]} days, for {flight["price"]}{fs.CURRENCY}. <a href="{flight["link"]}">Book it>>></a></p>
                    '''

            html_message_part2 += """<hr>"""

        # building the plain version

        plain_message_header = f"Flights from {fs.search_codes(fs.HOMECITY)[1]}({fs.HOMECITY}) \n"
        plain_message_end = f"Have a nice journey! \n The tool brought you by @nottocodehere and Kiwi.com,  Sheety.co, Google."
        plain_message_part2 = ""

        for city in results["destination"]:
            plain_message_part2 += f"Flights from {fs.search_codes(city)[1]}({city}) \n"

            if len(results["destination"][city]) == 1:
                plain_message_part2 += f'❌︎ {results["destination"][city]}'

            elif len(results["destination"][city]) > 1:
                for number, flight in enumerate(results["destination"][city]):
                    plain_message_part2 += f"✅︎ {number+1}.Departure: {flight['departure_date']}, {flight['stay']} days, for {flight['price']}{fs.CURRENCY}. Link -> {flight['link']} \n"

            plain_message_part2 += "\n"

        # using mime to build a message
        html_msg = MIMEText(html_message_header + html_message_part2 + html_message_end, "html")
        plain_msg= MIMEText(plain_message_header + plain_message_part2 + plain_message_end, "plain")
        message.attach(html_msg)
        message.attach(plain_msg)

        self.send_mail(email_body=message)

    def send_mail(self, email_body):
        # email sender
        print("Sending mail, connecting")
        connection = self.SMTP_CRED
        connection.starttls()
        connection.login(user=os.getenv("MY_EMAIL"), password=os.getenv("GMAIL_API_KEY").replace("_", " "))
        connection.sendmail(from_addr=os.getenv("MY_EMAIL"), to_addrs=os.getenv("ADDRESS1"),
                            msg=email_body.as_string())
        print("Email sent!")
        connection.close()
