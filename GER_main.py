import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine
from urllib.parse import quote


# MySQL-Verbindungsinformationen
db_host = 'localhost'
db_user = 'root'
db_password = 'ed%f6!drt§4d'
db_name = 'reisewarnung'
table_name = 'travel_advisories_ger'

# URL-encode das Passwort
encoded_password = quote(db_password)

# SQLAlchemy-Engine erstellen
engine = create_engine(f'mysql+mysqlconnector://{db_user}:{encoded_password}@{db_host}/{db_name}', echo=False)
all_countries = [
    "Afghanistan", "Albanien", "Algerien", "Andorra", "Angola", "Antigua und Barbuda", "Argentinien",
    "Armenien", "Australien", "Aserbaidschan", "Bahamas", "Bahrain", "Bangladesch", "Barbados",
    "Belarus", "Belgien", "Belize", "Benin", "Bhutan", "Bolivien", "Bosnien und Herzegowina",
    "Botswana", "Brasilien", "Brunei", "Bulgarien", "Burkina Faso", "Burundi", "Cabo Verde", "Chile",
    "China", "Costa Rica", "Dänemark", "Deutschland", "Dominica", "Dominikanische Republik",
    "Dschibuti", "Ecuador", "El Salvador", "Elfenbeinküste", "Eritrea", "Estland", "Eswatini",
    "Fidschi", "Finnland", "Frankreich", "Gabun", "Gambia", "Georgien", "Ghana", "Grenada",
    "Griechenland", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras",
    "Indien", "Indonesien", "Irak", "Iran", "Irland", "Island", "Israel", "Italien", "Jamaika",
    "Japan", "Jemen", "Jordanien", "Kambodscha", "Kamerun", "Kanada", "Kap Verde", "Kasachstan",
    "Katar", "Kenia", "Kirgisistan", "Kiribati", "Kolumbien", "Komoren", "Kongo", "Demokratische Republik Kongo",
    "Kroatien", "Kuba", "Kuwait", "Laos", "Lesotho", "Lettland", "Libanon", "Liberia", "Libyen",
    "Liechtenstein", "Litauen", "Luxemburg", "Madagaskar", "Malawi", "Malaysia", "Malediven",
    "Mali", "Malta", "Marokko", "Marshallinseln", "Mauretanien", "Mauritius", "Mexiko", "Mikronesien",
    "Moldau", "Monaco", "Mongolei", "Montenegro", "Mosambik", "Myanmar", "Namibia", "Nauru",
    "Nepal", "Neuseeland", "Nicaragua", "Niederlande", "Niger", "Nigeria", "Nordkorea",
    "Nordmazedonien", "Norwegen", "Oman", "Österreich", "Pakistan", "Palau", "Panama",
    "Papua-Neuguinea", "Paraguay", "Peru", "Philippinen", "Polen", "Portugal", "Ruanda",
    "Rumänien", "Russland", "Salomonen", "Sambia", "Samoa", "San Marino", "São Tomé und Príncipe",
    "Saudi-Arabien", "Schweden", "Schweiz", "Senegal", "Serbien", "Seychellen", "Sierra Leone",
    "Simbabwe", "Singapur", "Slowakei", "Slowenien", "Somalia", "Spanien", "Sri Lanka", "St. Kitts und Nevis",
    "St. Lucia", "St. Vincent und die Grenadinen", "Südafrika", "Sudan", "Südsudan", "Suriname",
    "Syrien", "Tadschikistan", "Tansania", "Thailand", "Togo", "Tonga", "Trinidad und Tobago",
    "Tschad", "Tschechien", "Tunesien", "Türkei", "Turkmenistan", "Tuvalu", "Uganda",
    "Ukraine", "Ungarn", "Uruguay", "Usbekistan", "Vanuatu", "Vatikanstadt", "Venezuela",
    "Vereinigte Arabische Emirate", "Vereinigte Staaten", "Vereinigtes Königreich", "Vietnam",
    "Zentralafrikanische Republik", "Zypern"
]

# Funktion, um das Datum um 3 Monate zu erhöhen
def add_months(d, months):
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day,
              [31, 29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30,
               31, 30, 31][month - 1])
    return datetime(year, month, day)


# Startdatum und aktuelles Datum
start_date = datetime(2018, 1, 1)  # Definiere hier das Startdatum
current_date = datetime.now()

# URL-Basis
url_template = "https://web.archive.org/web/{}/https://www.auswaertiges-amt.de/de/ReiseUndSicherheit/10.2.8Reisewarnungen"

# Liste für Ergebnisse
all_data = []
while start_date < current_date:
    # URL mit dem formatierten Datum anpassen (Format: YYYYMMDD)
    date_string = start_date.strftime('%Y%m%d') + "050335"  # Uhrzeit anhängen, hier ein Beispiel
    url = url_template.format(date_string)

    print(f"Scraping URL: {url}")

    # Set für die abgerufenen Länder
    found_countries = set()

    try:
        # Webseite abfragen
        response = requests.get(url)

        # Falls die Seite nicht gefunden wird, einen Fehler abfangen
        if response.status_code != 200:
            print(f"Seite nicht gefunden für {start_date.strftime('%Y-%m-%d')}")
            # Gehe zum nächsten Datum
            start_date = add_months(start_date, 3)
            continue

        # HTML-Inhalt parsen
        soup = BeautifulSoup(response.content, 'html.parser')

        # Finde die relevanten Listenelemente (wie im vorherigen Skript)
        warnings_list = soup.find_all('li', class_='rte__list-item')

        # Daten sammeln
        for item in warnings_list:
            link = item.find('a')
            if link:
                text = link.get_text(strip=True)
                if 'Reisewarnung' in text or 'Teilreisewarnung' in text:
                    # Text aufteilen, um Land und Warnung zu extrahieren
                    # Nimm nur das erste und letzte Element (Land und Warnung), ignoriere den Mittelteil
                    parts = text.split()
                    if len(parts) > 1:
                        country = parts[0] # Land
                        warning_type = parts[-1] # Reisewarnung oder Teilreisewarnung
                        warning_type= warning_type.replace(')','')
                        warning_type = warning_type.replace('(', '')
                        # Füge das Land zu den gefundenen Ländern hinzu
                        found_countries.add(country)
                        # Füge die Daten hinzu
                        all_data.append([start_date.strftime('%Y-%m-%d'), country, warning_type, current_date.strftime('%Y-%m-%d'), 'Ger'])

    except Exception as e:
        print(f"Fehler beim Abrufen der Seite: {e}")

    # Prüfen, ob alle Länder aus der Länderliste enthalten sind
    for country in all_countries:
        if country not in found_countries:
            # Wenn ein Land nicht enthalten ist, füge es mit "None" hinzu
            all_data.append([start_date.strftime('%Y-%m-%d'), country, "None", current_date.strftime('%Y-%m-%d'), 'Ger'])

    # Datum um 3 Monate erhöhen
    start_date = add_months(start_date, 3)

    # Optional: Eine kleine Verzögerung einfügen, um zu viele Anfragen in kurzer Zeit zu vermeiden
    time.sleep(12)

# Die gesammelten Daten in einen DataFrame speichern
travel_advisories_ger = pd.DataFrame(all_data, columns=['Datum', 'Land', 'Warnung', 'Date', 'origin'])
travel_advisories_ger.to_sql(table_name, engine, if_exists='append', index=False)
# DataFrame anzeigen
print(travel_advisories_ger)


