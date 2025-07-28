import requests
from bs4 import BeautifulSoup
import datetime
import smtplib
from email.message import EmailMessage
import os  # For secure env vars
import ssl  # For secure connections

# Get today's date (like checking timestamps in network logs)
today_str = datetime.date.today().strftime('%b %d')  # e.g., 'Jul 28' for filtering

# Fetch the calendar page (public, no auth needed)
url = 'https://www.myfxbook.com/forex-economic-calendar'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}  # Mimic browser for ethics
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the events table (based on page structure: table with id 'economicCalendarTable' or class 'table')
table = soup.find('table', id='economicCalendarTable')  # Adjust if needed; inspect page in browser dev tools (F12)
if not table:
    print("Table not found - check page structure.")
    exit()

# Extract rows, filter for today and relevant currencies
events = []
relevant_currencies = ['EUR', 'GBP', 'USD']
for row in table.find_all('tr')[1:]:  # Skip header
    cells = row.find_all('td')
    if len(cells) >= 6:  # Columns: time (with days until), empty?, currency, event, forecast, previous (adjusted for 2025 structure)
        event_time_full = cells[0].text.strip()  # e.g., 'Jul 28, 08:30 | 0 days'
        currency = cells[2].text.strip()  # Shifted: currency now in cell 2
        impact = "N/A"  # No impact column in current structure
        event_name = cells[3].text.strip()  # Event in cell 3
        forecast = cells[4].text.strip()  # Forecast in cell 4
        previous = cells[5].text.strip()  # Previous in cell 5
        
        # Filter: today (check if today's date string is in the time part)
        event_time = event_time_full.split('|')[0].strip()  # e.g., 'Jul 28, 08:30'
        if today_str in event_time and currency in relevant_currencies:
            events.append({
                'Time': event_time,
                'Currency': currency,
                'Impact': impact,
                'Event': event_name,
                'Forecast': forecast,
                'Previous': previous
            })

# Format as simple text table (for email body)
if events:
    email_body = "Today's Forex Events for EURUSD/GBPUSD (from myFXbook):\n\n"
    email_body += "{:<20} {:<5} {:<10} {:<40} {:<10} {:<10}\n".format('Time', 'Curr', 'Impact', 'Event', 'Forecast', 'Previous')
    for event in events:
        email_body += "{:<20} {:<5} {:<10} {:<40} {:<10} {:<10}\n".format(
            event['Time'], event['Currency'], event['Impact'], event['Event'], event['Forecast'], event['Previous']
        )
else:
    email_body = "No relevant events today for EUR/GBP/USD. God Bless Kraken"

# Send email (securely using env vars)
from_email = os.getenv('FROM_EMAIL')  # Fixed typo from 'FROM_MAIL'
to_email = os.getenv('TO_EMAIL')
smtp_server = 'smtp.gmail.com'
password = os.getenv('EMAIL_PASSWORD')  # Use app password!

msg = EmailMessage()
msg.set_content(email_body)
msg['Subject'] = f"Daily Forex Events - {datetime.date.today().strftime('%Y-%m-%d')}"
msg['From'] = from_email
msg['To'] = to_email

# Enhanced send with EHLO for robust auth (TLS on 587 first; swap to SSL/465 if needed)
try:
    server = smtplib.SMTP(smtp_server, 587)
    server.ehlo()  # Better handshake
    server.starttls(context=ssl.create_default_context())
    server.ehlo()  # Re-EHLO after TLS
    server.login(from_email, password)
    server.send_message(msg)
    server.quit()
    print("Email sent via TLS/587!")
except Exception as e:
    print(f"Error sending email: {e}")
    # If 587 fails, uncomment this block for SSL/465 test
    # try:
    #     context = ssl.create_default_context()
    #     with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
    #         server.login(from_email, password)
    #         server.send_message(msg)
    #     print("Email sent via SSL/465!")
    # except Exception as e:
    #     print(f"SSL Error: {e}")