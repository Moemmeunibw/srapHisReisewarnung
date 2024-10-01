import time

import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

# Database connection setup using SQLAlchemy
db_user = 'root'
db_password = 'ed%f6!drt§4d'
db_host = 'localhost'
db_name = 'reisewarnung'
encoded_password = quote(db_password)

# Creating a connection string
connection_string = f'mysql+mysqlconnector://{db_user}:{encoded_password}@{db_host}/{db_name}'
engine = create_engine(connection_string)


def scrape_and_store(url, engine, current_date):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the section containing the travel advisories
    table = soup.find('table', class_='wb-tables', id='reportlist')

    if not table:
        print("Table not found")
        return

    rows = table.find_all('tr')[1:]  # Skip the header row

    # List for storing extracted data
    travel_advisories = []

    for row in rows:
        columns = row.find_all('td')

        # Check if the row contains enough columns
        if len(columns) < 3:
            print("Skipping row, not enough columns:", columns)
            continue

        # Debugging: Print columns to inspect
        print("Row columns:", columns)

        destination = columns[1].get_text(strip=True)  # Adjust index based on actual structure
        risk_level = columns[2].get_text(strip=True)
        last_updated = columns[3].get_text(strip=True)
        #current_date = current_date.date()
        last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
        travel_advisories.append({
            'Country': destination,
            'Level': risk_level,
            'Date_Updated': last_updated,
            'Date' : current_date,
            'origin' : 'Canada'
        })

    # Store data in the database
    df = pd.DataFrame(travel_advisories)
    df.to_sql('travel_advisories_can', engine, if_exists='append', index=False)


# URL pattern for Wayback Machine snapshots
base_url = "https://web.archive.org/web/{date}/https://travel.gc.ca/travelling/advisories"

# Start and end dates
start_date = datetime(2015, 1, 1)
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
    time.sleep(12)
print("Data scraping completed.")