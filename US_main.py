import time

import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from datetime import datetime
from dateutil.relativedelta import relativedelta

# MySQL-Verbindungsinformationen
db_host = 'localhost'
db_user = 'root'
db_password = 'ed%f6!drt§4d'
db_name = 'reisewarnung'
table_name = 'travel_advisories_us'

# URL-encode das Passwort
encoded_password = quote(db_password)

# SQLAlchemy-Engine erstellen
engine = create_engine(f'mysql+mysqlconnector://{db_user}:{encoded_password}@{db_host}/{db_name}', echo=False)

# Funktion zum Scrapen und Speichern der Daten
def scrape_and_store(url, engine, current_date):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Finde die Tabelle mit den Reisehinweisen
    table = soup.find('div', class_='table-data')
    rows = table.find_all('tr')

    # Liste für die gesammelten Daten
    travel_advisories_US = []

    # Iteriere über die Zeilen und extrahiere die Daten
    for row in rows:
        if row.find('td') is None:
            continue

        country_name = row.find('td').get_text(strip=True)
        country_name = country_name.removesuffix("Travel Advisory")
        country_name = country_name.replace(" ", "")
        print(country_name)
        try:
            level = row.find_all('td')[1].get_text(strip=True)
            print(level)
        except:
            level = None
        try:
            date_updated = row.find_all('td')[2].get_text(strip=True)
            date_updated = datetime.strptime(date_updated, "%B %d, %Y").date()
            print(date_updated)
        except:
            date_updated = None
        current_date_s = current_date.date()

        travel_advisories_US.append({
            'Country': country_name,
            'Level': level,
            'Date_Updated': date_updated,
            'date': current_date_s,
            'origin': 'US'
        })

    # Speichere die Daten in der MySQL-Datenbank
    df = pd.DataFrame(travel_advisories_US)
    df.to_sql(table_name, engine, if_exists='append', index=False)


# Startdatum und Schrittweite (3 Monate)
start_date = datetime(2018, 6, 1)
end_date = datetime.now()

# Schleife, um das Datum um 3 Monate zu steigern und das Scraping durchzuführen
current_date = start_date
while current_date <= end_date:
    print("HHHHHHHERE DATE" + str(current_date))
    # Formatieren des Datums für die URL (YYYYMMDD)
    formatted_date = current_date.strftime('%Y%m%d')
    print(formatted_date)

    # URL für den spezifischen Zeitraum
    url = f"https://web.archive.org/web/{formatted_date}/https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html/"

    # Scraping durchführen und die Daten speichern
    print(f"Scraping data for: {formatted_date}")

    scrape_and_store(url, engine, current_date)

    # Datum um 3 Monate erhöhen
    current_date += relativedelta(months=3)
    time.sleep(12)

# Schließen der MySQL-Verbindung (SQLAlchemy schließt automatisch)
