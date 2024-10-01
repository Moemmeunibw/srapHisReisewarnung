import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from bs4 import BeautifulSoup
import time
from sqlalchemy import create_engine
from urllib.parse import quote


# MySQL-Verbindungsinformationen
db_host = 'localhost'
db_user = 'root'
db_password = 'ed%f6!drt§4d'
db_name = 'reisewarnung'
table_name = 'travel_advisories_uk'

# URL-encode das Passwort
encoded_password = quote(db_password)

# SQLAlchemy-Engine erstellen
engine = create_engine(f'mysql+mysqlconnector://{db_user}:{encoded_password}@{db_host}/{db_name}', echo=False)

countries = [
    "angola", "afghanistan","albania", "algeria", "andorra",  "antigua-and-barbuda", "argentina",
    "armenia", "australia", "austria", "azerbaijan", "bahamas", "bahrain", "bangladesh", "barbados",
    "belarus", "belgium", "belize", "benin", "bhutan", "bolivia", "bosnia-and-herzegovina", "botswana",
    "brazil", "brunei", "bulgaria", "burkina-faso", "burundi", "cabo-verde", "cambodia", "cameroon",
    "canada", "central-african-republic", "chad", "chile", "china", "colombia", "comoros", "congo",
    "costa-rica", "croatia", "cuba", "cyprus", "czech-republic", "democratic-republic-of-the-congo",
    "denmark", "djibouti", "dominica", "dominican-republic", "east-timor", "ecuador", "egypt",
    "el-salvador", "equatorial-guinea", "eritrea", "estonia", "eswatini", "ethiopia", "fiji",
    "finland", "france", "gabon", "gambia", "georgia", "germany", "ghana", "greece", "grenada",
    "guatemala", "guinea", "guinea-bissau", "guyana", "haiti", "honduras", "hungary", "iceland",
    "india", "indonesia", "iran", "iraq", "ireland", "israel", "italy", "ivory-coast", "jamaica",
    "japan", "jordan", "kazakhstan", "kenya", "kiribati", "kosovo", "kuwait", "kyrgyzstan", "laos",
    "latvia", "lebanon", "lesotho", "liberia", "libya", "liechtenstein", "lithuania", "luxembourg",
    "madagascar", "malawi", "malaysia", "maldives", "mali", "malta", "marshall-islands", "mauritania",
    "mauritius", "mexico", "micronesia", "moldova", "monaco", "mongolia", "montenegro", "morocco",
    "mozambique", "myanmar", "namibia", "nauru", "nepal", "netherlands", "new-zealand", "nicaragua",
    "niger", "nigeria", "north-korea", "north-macedonia", "norway", "oman", "pakistan", "palau",
    "panama", "papua-new-guinea", "paraguay", "peru", "philippines", "poland", "portugal", "qatar",
    "romania", "russia", "rwanda", "saint-kitts-and-nevis", "saint-lucia", "saint-vincent-and-the-grenadines",
    "samoa", "san-marino", "sao-tome-and-principe", "saudi-arabia", "senegal", "serbia", "seychelles",
    "sierra-leone", "singapore", "slovakia", "slovenia", "solomon-islands", "somalia", "south-africa",
    "south-korea", "south-sudan", "spain", "sri-lanka", "sudan", "suriname", "sweden", "switzerland",
    "syria", "taiwan", "tajikistan", "tanzania", "thailand", "togo", "tonga", "trinidad-and-tobago",
    "tunisia", "turkey", "turkmenistan", "tuvalu", "uganda", "ukraine", "united-arab-emirates",
    "united-kingdom", "united-states", "uruguay", "uzbekistan", "vanuatu", "vatican-city", "venezuela",
    "vietnam", "yemen", "zambia", "zimbabwe"
]


# Funktion zum Abrufen von advise_all_travel und advise_essential_travel aus der Website
def get_travel_advice(date_str, country):
    # Erstellen des Links mit dem aktuellen Datum
    url = f"https://web.archive.org/web/{date_str}054038/https://www.gov.uk/foreign-travel-advice/{country}"
    advise_all_travel = 'Not available'
    advise_essential_travel = 'Not available'
    current_date_travel = None  # Standardwert für current_date_travel
    updated_date_travel = None  # Standardwert für updated_date_travel

    try:
        # HTTP-GET Anfrage an die Website
        response = requests.get(url)

        # Überprüfen, ob die Anfrage erfolgreich war
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extrahieren von advise_all_travel und advise_essential_travel
            advice_container = soup.find('div', class_='application-notice help-notice')
            time_container = soup.find('ul', class_='country-metadata')
            advise_all_travel = 'Not available'
            advise_essential_travel = 'Not available'
            current_date_travel = None
            updated_date_travel = None
            if time_container:
                time_texts = time_container.find_all('li')


                current_date_travel = time_texts[0].text.strip() if len(time_texts) > 0 else 'Not available'
                updated_date_travel = time_texts[1].text.strip() if len(time_texts) > 0 else 'Not available'
                #print(current_date_travel)
            else:
                try:
                    time_container = soup.find('div', class_='govuk-metadata')

                    time_container = time_container.find_all('dl')
                    time_container = time_container[0]
                    #print(time_container)
                    time_texts = time_container.find_all('dd')
                    #print(time_texts)
                    current_date_travel = time_texts[0].text.strip() if len(time_texts) > 0 else 'Not available'
                    updated_date_travel = time_texts[1].text.strip() if len(time_texts) > 0 else 'Not available'
                    #print(current_date_travel)
                except:
                    time_container = soup.find_all('dd', class_='gem-c-metadata__definition')
                    current_date_travel = time_container[0].text.strip() if len(time_container) > 0 else 'Not available'
                    updated_date_travel = time_container[1].text.strip() if len(time_container) > 0 else 'Not available'
                    #print(current_date_travel)


            if advice_container and ("FCDO" in advise_all_travel or "FCO" in advise_all_travel):
                # Extraktion der spezifischen Ratschläge
                advise_texts = advice_container.find_all('p')
                advise_all_travel = advise_texts[0].text.strip() if len(advise_texts) > 0 else 'Not available'
                advise_essential_travel = advise_texts[1].text.strip() if len(advise_texts) > 1 else 'blub'
            else:
                try:
                    advice_container = soup.find('article', class_='group')
                    advise_texts = advice_container.find_all('p')
                    if any(e in str(advise_texts) for e in 'FCO'.split()):
                        indexes = [index for index, p in enumerate(advise_texts) if 'FCO' in p.get_text()]
                        advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                            advise_texts) > 0 else 'Not available'
                        try:
                            advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                advise_texts) > 0 else ''
                        except:
                            advise_essential_travel = ''
                        #print(advise_all_travel + "sdsdsdtntgrn gfb")
                    else:
                        indexes = [index for index, p in enumerate(advise_texts) if 'FCDO' in p.get_text()]
                        advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                            advise_texts) > 0 else 'Not available'
                        try:
                            advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                advise_texts) > 0 else ''
                        except:
                            advise_essential_travel = ''
                        #print(advise_all_travel + "hjjjjj")
                    #print(advise_texts)
                    #advise_all_travel = advise_texts[3].text.strip() if len(advise_texts) > 0 else 'Not available'
                    #advise_essential_travel = ''
                    #print(advise_all_travel)
                    #print("check2")
                except:
                    try:

                        advice_container = soup.find('div', class_='content-block')
                        advice_container = advice_container.find('div', class_='inner')
                        advise_texts = advice_container.find_all('p')
                        advise_all_travel = advise_texts[3].text.strip() if len(advise_texts) > 0 else 'Not available'
                        advise_all_travel = advise_all_travel + "sdsd"
                        advise_essential_travel = ''
                    except:
                        advice_container = soup.find('div', class_='gem-c-govspeak govuk-govspeak direction-ltr')
                        if advice_container == None:
                            advice_container = soup.find('div', class_='govuk-govspeak')
                        advise_texts = advice_container.find_all('p')

                        #print(advice_container)
                        #if "FCO" in advise_texts or "FCDO" in advise_texts:
                        if any('FCO' in str(strong) for strong in soup.find_all('strong')) or any('FCDO' in str(strong) for strong in soup.find_all('strong')):
                            advise_texts = soup.find_all('strong')
                            if any(e in str(advise_texts) for e in 'FCO'.split()):
                                indexes = [index for index, p in enumerate(advise_texts) if 'FCO' in p.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(advise_texts) > 0 else 'Not available'
                                try:
                                    advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(advise_texts) > 0 else ''
                                except:
                                    pass
                                #print(advise_all_travel + "sdsdsdtntgrn gfb")
                            else:
                                indexes = [index for index, p in enumerate(advise_texts) if 'FCDO' in p.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(advise_texts) > 0 else 'Not available'
                                try:
                                    advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(advise_texts) > 0 else ''
                                except:
                                    pass
                                #print(advise_all_travel + "hjjjjj")
                            #advise_all_travel = + "sdsdsdsdsd"
                            #advise_essential_travel = ''

                        elif any('FCO' in str(h3) for h3 in advice_container.find_all('h3')) or any('FCDO' in str(h3) for h3 in advice_container.find_all('h3')):
                            advise_texts = advice_container.find_all('h3')
                            #print("hereeeeee")

                            if "FCO" in advise_all_travel or "FCDO" in advise_all_travel:
                                advise_all_travel = advise_all_travel + "sssssss"
                                advise_essential_travel = ''
                            elif any(e in str(advise_texts) for e in 'FCO'.split()):
                                #print(advise_texts)
                                indexes = [index for index, h3 in enumerate(advise_texts) if 'FCO' in h3.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                                    advise_texts) > 0 else 'Not available'
                                try:
                                    advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                        advise_texts) > 0 else ''
                                except:
                                    pass
                                #print(advise_all_travel + "blobfisch2")
                            elif any(e in str(advise_texts) for e in 'FCDO'.split()):
                                #print(advise_texts)
                                indexes = [index for index, h3 in enumerate(advise_texts) if 'FCDO' in h3.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                                    advise_texts) > 0 else 'Not available'
                                try:
                                    advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                        advise_texts) > 0 else ''
                                except:
                                    pass
                                #print(advise_all_travel + "blobfisch2")

                            elif any(e in str(advise_texts) for e in 'FCDO'.split()) or any(e in str(advise_texts) for e in 'FCDO'.split()):
                                indexes = [index for index, h3 in enumerate(advise_texts) if 'FCDO' in h3.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                                    advise_texts) > 0 else 'Not available'
                                advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                    advise_texts) > 0 else ''
                                #print(advise_all_travel + "blobfisch2")
                            else:
                                advise_texts = advice_container.find_all('h3')
                                #print(advise_texts)
                                advise_all_travel =  advise_texts[0].text.strip()
                                advise_all_travel = advise_all_travel + "blobfisch"
                                #print(advise_all_travel)
                        #h2
                        elif any('FCO' in str(h2) for h2 in advice_container.find_all('h2')) or any('FCDO' in str(h2) for h2 in advice_container.find_all('h2')):
                            advise_texts = advice_container.find_all('h2')
                            #print("hereeeeee")

                            if "FCO" in advise_all_travel or "FCDO" in advise_all_travel:
                                advise_all_travel = advise_all_travel + "sssssss"
                                advise_essential_travel = ''
                            elif any(e in str(advise_texts) for e in 'FCO'.split()):
                                #print(advise_texts)
                                indexes = [index for index, h2 in enumerate(advise_texts) if 'FCO' in h2.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                                    advise_texts) > 0 else 'Not available'
                                try:
                                    advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                        advise_texts) > 0 else ''
                                except:
                                    pass
                                #print(advise_all_travel + "blobfisch2")
                            elif any(e in str(advise_texts) for e in 'FCDO'.split()):
                                #print(advise_texts)
                                indexes = [index for index, h2 in enumerate(advise_texts) if 'FCDO' in h2.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                                    advise_texts) > 0 else 'Not available'
                                try:
                                    advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                        advise_texts) > 0 else ''
                                except:
                                    pass
                                #print(advise_all_travel + "blobfisch2")

                            elif any(e in str(advise_texts) for e in 'FCDO'.split()) or any(e in str(advise_texts) for e in 'FCDO'.split()):
                                indexes = [index for index, h2 in enumerate(advise_texts) if 'FCDO' in h2.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                                    advise_texts) > 0 else 'Not available'
                                advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                    advise_texts) > 0 else ''
                                #print(advise_all_travel + "blobfisch2")
                            else:
                                advise_texts = advice_container.find_all('h2')
                                #print(advise_texts)
                                advise_all_travel =  advise_texts[0].text.strip()
                                advise_all_travel = advise_all_travel + "blobfisch"
                                #print(advise_all_travel)
                        #h2end
                        elif any('FCO' in str(p) for p in advice_container.find('p')) or any('FCDO' in str(p) for p in advice_container.find('p')):
                            advise_texts = advice_container.find_all('p')
                            print(advise_texts)
                            print("check")
                            if any(e in str(advise_texts) for e in 'FCO'.split()):
                                indexes = [index for index, p in enumerate(advise_texts) if 'FCO' in p.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(advise_texts) > 0 else 'Not available'
                                try:
                                    advise_all_travel = advise_texts[indexes[0]].text.strip() if len(
                                        advise_texts) > 0 else 'Not available'
                                except:
                                    pass
                                #advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(advise_texts) > 0 else ''
                                #print(advise_all_travel + "sdsdsdtntgrn gfb")
                            else:
                                indexes = [index for index, p in enumerate(advise_texts) if 'FCDO' in p.get_text()]
                                advise_all_travel = advise_texts[indexes[0]].text.strip() if len(advise_texts) > 0 else 'Not available'
                                try:
                                    advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(
                                        advise_texts) > 1 else 'Not available'
                                except:
                                    pass
                                #advise_essential_travel = advise_texts[indexes[1]].text.strip() if len(advise_texts) > 0 else ''
                                #print(advise_all_travel + "hjjjjj")
                            #advise_all_travel = + "sdsdsdsdsd"
                            #advise_essential_travel = ''
                        else:
                            print("ausgesteuert")


        else:
            advise_all_travel = 'Error fetching data'
            advise_essential_travel = 'Error fetching data'

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for date {date_str}: {e}")
        advise_all_travel = 'Error fetching data'
        advise_essential_travel = 'Error fetching data'
        current_date_travel = 'Error fetching data'
        updated_date_travel = 'Error fetching data'
    if '.' in advise_all_travel:
        advise_all_travel = advise_all_travel.split('.')
        advise_all_travel = advise_all_travel[0]
    if '.' in advise_essential_travel:
        advise_essential_travel = advise_essential_travel.split('.')
        advise_essential_travel = advise_essential_travel[0]


    return advise_all_travel, advise_essential_travel, current_date_travel, updated_date_travel


# Startdatum
for country in countries:
    start_date = datetime.strptime("20180101", "%Y%m%d")
    current_date = datetime.now()
    print(start_date)


    # DataFrame zum Speichern der Ergebnisse
    travel_advisories_uk = pd.DataFrame(columns=["country", "Datum", "Datum_Travel", "Datum_Update", "Advice"])

    # Land festlegen
    country = country

    # Schleife zur Erhöhung des Datums um 3 Monate
    while start_date <= current_date:
        # Datum im richtigen Format als String speichern
        date_str = start_date.strftime("%Y%m%d")
        #print("curDate" + str(date_str))

        # Abrufen der Ratschläge von der Website
        advise_all_travel, advise_essential_travel, date_trav, date_update = get_travel_advice(date_str, country)

        # Ratschläge als einen String zusammenfügen
        combined_advice = f"{advise_all_travel}; {advise_essential_travel}"
        #print(advise_all_travel + advise_essential_travel + date_trav + date_update)
        #print(combined_advice)
        print(date_str)
        print(date_trav)
        print(date_update)


        def parse_date(date_str):
            # Überprüfen, ob der Wert nicht 'Not available' ist
            if date_str and date_str != 'Not available':
                try:
                    return datetime.strptime(date_str, "%d %B %Y")
                except ValueError:
                    return pd.NaT  # Falls der Wert nicht konvertiert werden kann, zurückgeben von NaT
            else:
                return pd.NaT  # Falls kein gültiges Datum vorliegt

        datum_datetime = datetime.strptime(date_str, "%Y%m%d")

        # Konvertiere date_trav und date_update in datetime-Objekte
        date_trav = parse_date(date_trav)
        date_update = parse_date(date_update)


        # Ergebnis zum DataFrame hinzufügen
        travel_advisories_uk = pd.concat([travel_advisories_uk, pd.DataFrame({
            "country": [country],
            "Datum": [date_str],
            "Datum_Travel": [date_trav if date_trav is not None else pd.NA],
            "Datum_Update": [date_update if date_update is not None else pd.NA],
            "Advice": [combined_advice if combined_advice is not None else pd.NA],
            "origin":"UK"
        })], ignore_index=True)

        # Datum um 3 Monate erhöhen
        start_date += relativedelta(months=3)

        # Wartezeit hinzufügen, um den Server nicht zu überlasten
        time.sleep(15)

    # DataFrame ausgeben
    print(travel_advisories_uk)
    travel_advisories_uk.to_sql(table_name, engine, if_exists='append', index=False)
