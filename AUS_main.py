import time

import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import quote
from dateutil import parser
# Database connection setup using SQLAlchemy
db_user = 'root'
db_password = 'ed%f6!drt§4d'
db_host = 'localhost'
db_name = 'reisewarnung'
encoded_password = quote(db_password)

# Creating a connection string
connection_string = f'mysql+mysqlconnector://{db_user}:{encoded_password}@{db_host}/{db_name}'
engine = create_engine(connection_string)

# Function to scrape and store data
def scrape_and_store(url, engine, current_date):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table containing the travel advisory data
    table = soup.find('table', class_='views-table')

    # List for storing extracted data
    travel_advisories_aus = []

    # Extract rows from the table
    rows = table.find_all('tr')[1:]  # Skip the header row

    for row in rows:
        columns = row.find_all('td')
        country_name = columns[0].get_text(strip=True)
        level = columns[2].get_text(strip=True)

        # Safely handle the "Updated" field and check for the 'time' tag
        time_tag = columns[3].find('time')
        if time_tag:
            date_updated = time_tag['datetime']  # Extract the date in 'datetime' format
            date_updated = parser.isoparse(date_updated)
        else:
            date_updated = None  # Set a default value if no time tag is found
        current_date_s = current_date.date()
        travel_advisories_aus.append({
            'Country': country_name,
            'Level': level,
            'Date_Updated': date_updated,
            'Date': current_date_s,
            'origin': 'AUS'

        })

    # Store data in the database
    df = pd.DataFrame(travel_advisories_aus)
    df.to_sql('travel_advisories_aus', engine, if_exists='append', index=False)

# URL pattern for Wayback Machine snapshots
base_url = "https://web.archive.org/web/{date}/https://www.smartraveller.gov.au/destinations"

# Start and end dates
start_date = datetime(2020, 1, 1)
end_date = datetime.now()

# Iterate through snapshots in 3-month intervals
current_date = start_date
while current_date <= end_date:
    formatted_date = current_date.strftime('%Y%m%d')
    url = base_url.format(date=formatted_date)

    print(f"Scraping data for: {formatted_date}")
    scrape_and_store(url, engine, current_date)

    # Increment the date by 3 months
    current_date += relativedelta(months=3)
    time.sleep(10)

print("Data scraping completed.")
