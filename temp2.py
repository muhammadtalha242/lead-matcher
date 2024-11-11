import pandas as pd

# Load the CSV file into a DataFrame
input_csv = './data/dejuna data feed - buyer dejuna (2).csv'  # Replace this with your actual file path
output_csv = 'dejuna_data_feed_updated_detailed.csv'

# Erstellen eines Mappings von Titeln zu Industrie und Sub-Industrie
mapping = {
    "Elektroinstallationsfirma oder ein Ingenieurbüro für Gebäudetechnik gesucht": ("Ingenieurdienstleistungen", "Elektroinstallation, Gebäudetechnik, Brandschutztechnik"),
    "Heizung Sanitärbetrieb im Raum Celle - Hannover gesucht": ("Handwerk", "Heizung, Sanitär, Klima (SHK)"),
    "Physiotherapeut sucht Praxis in Nürnberg": ("Gesundheitswesen", "Physiotherapie"),
    "Jungunternehmer sucht Physio-Praxis in Düsseldorf": ("Gesundheitswesen", "Physiotherapie, Fitnessstudios"),
    "Schreinermeister sucht Tischlerei zur Übernahme": ("Handwerk", "Schreinerei, Möbelbau"),
    "Geschäftsführer sucht Transportfirma zum Kauf": ("Transport und Logistik", "Spedition, Transportdienstleistungen"),
    "MBI-Kandidat sucht Logistik-Firma": ("Transport und Logistik", "Spedition, Logistikdienstleistungen"),
    "Führungskraft möchte Logistik-Firma übernehmen": ("Transport und Logistik", "Straßentransport, Spedition"),
    "Logistik-Berater sucht Firma zur Übernahme": ("Transport und Logistik", "Spedition, Logistikdienstleistungen"),
    "Logistik-Geschäftsführer sucht Transportunternehmen": ("Transport und Logistik", "Spedition, Transportdienstleistungen"),
    "Disponent möchte sich selbstständig machen": ("Transport und Logistik", "Schüttguttransporte, Schwertransporte"),
    "Geschäftsführer sucht Dienstleistungsunternehmen": ("Dienstleistungssektor", "Logistikdienstleistungen, Spedition"),
    "Logistiker sucht Spedition oder Kontrakt-Logistik": ("Transport und Logistik", "Spedition, Kontraktlogistik, Lagerhaltung"),
    "Geschäftsführer sucht Spedition zur Übernahme": ("Transport und Logistik", "Spedition, Transportdienstleistungen"),
    "Investor kauft Speditionen auf": ("Transport und Logistik", "Spedition, Logistikdienstleistungen"),
    "Inahber von 2 Speditionen sucht weitere Firmen zum Kauf": ("Transport und Logistik", "Spedition, Transportdienstleistungen"),
    "Umzugsunternehmer sucht Möbelspedition": ("Transport und Logistik", "Umzugsdienste, Möbeltransporte"),
    "Familienunternehmen sucht Geschäftsfelderweiterung im Schwerlastverkehr": ("Transport und Logistik", "Schwertransporte, Spezialtransporte"),
    "Unternehmer sucht Transportunternehmen": ("Transport und Logistik", "Spedition, Transportdienstleistungen"),
    "Speditionsgruppe sucht passende Firma zum Kauf": ("Transport und Logistik", "Spedition, Logistikdienstleistungen"),
    "Logistikgruppe sucht Möbelspedition": ("Transport und Logistik", "Möbeltransporte, Umzugsdienste"),
    "Logistik-Immobilien gesucht": ("Immobilien und Logistik", "Logistikimmobilien, Containerdienste"),
    "Geschäftsführer sucht Pflegedienst zur Übernahme": ("Gesundheitswesen", "Ambulanter Pflegedienst, Pflegeleistungen"),
    "Unternehmen sucht Erweiterung: Tank, Behälter, Heizung, Oberflächenschutz etc.": ("Industriedienstleistungen", "Tankbau, Oberflächenschutz, Industrieanstriche"),
    "Unternehmer sucht Hausverwaltung zum Kauf": ("Immobilien", "Hausverwaltung"),
    "Immobilienunternehmer sucht Hausverwaltung": ("Immobilien", "Hausverwaltung"),
    "Elektroingenieur sucht Elektrofirma zur Übernahme": ("Elektroindustrie", "Elektroinstallation, Kommunikationstechnik"),
    "Hausverwalter sucht HV zur Übernahme": ("Immobilien", "Hausverwaltung"),
    "Junger Hausverwalter sucht in Mittelfranken": ("Immobilien", "Hausverwaltung"),
    "Unternehmer sucht Hausverwaltung": ("Immobilien", "Hausverwaltung"),
    "Heizungsbaumeister sucht SHK Betrieb": ("Handwerk", "Heizung, Sanitär, Klima (SHK)"),
    "SHK Betrieb in Sachsen gesucht": ("Handwerk", "Heizung, Sanitär, Klima (SHK)"),
    "Angehender Heizungsbaumeister sucht SHK Betrieb": ("Handwerk", "Heizung, Sanitär, Klima (SHK)"),
    "Firma gesucht:Gebäudetechnik oder Brandschutz": ("Ingenieurdienstleistungen", "Gebäudetechnik, Brandschutztechnik"),
    "Schlossermeister sucht weiteren Schlosserei-Betrieb zur Übernahme.": ("Handwerk", "Metallbau, Schlosserei"),
    "Schreinermeister sucht Tischlerei": ("Handwerk", "Schreinerei, Tischlerei"),
    "KFZ-Meister sucht Werkstatt": ("Fahrzeugdienstleistungen", "Kfz-Reparaturwerkstätten"),
    "Historisches Weingut gesucht": ("Landwirtschaft und Weinbau", "Weinbau, Weingut"),
    "Geschäftsführer sucht Logistik-Unternehmen": ("Transport und Logistik", "Spezialtransporte, Industrielogistik, Pharmalogistik"),
    "Maschinenkonstrukteur sucht Maschinenbau-Betrieb": ("Herstellung und Engineering", "Maschinenbau, Anlagenbau"),
    "Finanzberaterin sucht Versicherungsagentur zur Übernahme": ("Finanzdienstleistungen", "Versicherungsmakler"),
    "Logistik-Firma sucht Spedition zur Übernahme": ("Transport und Logistik", "Spedition, Transportdienstleistungen"),
    "Hausverwaltungsgruppe sucht weitere Hausverwaltung": ("Immobilien", "Hausverwaltung"),
    "Jung-Unternehmer sucht Hausverwaltung zum Kauf": ("Immobilien", "Hausverwaltung"),
    "Ambulanter Pflegedienst in Süd-Hessen gesucht": ("Gesundheitswesen", "Ambulante Pflege, Pflegedienstleistungen"),
    "Industriemeister Metall sucht Schlosserei zur Übernahme": ("Handwerk", "Metallbau, Schlosserei"),
    "Versicherungsmakler sucht Versicherungsagentur": ("Finanzdienstleistungen", "Versicherungsmakler"),
}

# Lesen der CSV-Datei in einen DataFrame
df = pd.read_csv(input_csv, encoding='utf-8')

# Funktion zum Zuordnen der Industrie und Sub-Industrie basierend auf dem Titel
def get_industrie(row):
    titel = row['Titel']
    if titel in mapping:
        return mapping[titel][0]
    else:
        return 'Unbekannt'

def get_sub_industrie(row):
    titel = row['Titel']
    if titel in mapping:
        return mapping[titel][1]
    else:
        return 'Unbekannt'

# Neue Spalten 'Industrie' und 'Sub-Industrie' hinzufügen
df['Industrie'] = df.apply(get_industrie, axis=1)
df['Sub-Industrie'] = df.apply(get_sub_industrie, axis=1)

# Aktualisierten DataFrame in eine neue CSV-Datei schreiben
df.to_csv(output_csv, index=False, encoding='utf-8')
