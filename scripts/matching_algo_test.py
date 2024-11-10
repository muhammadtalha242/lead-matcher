import pandas as pd
import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------------
# Step 1: Load Data
# ----------------------------------

# Load seller data
seller_df = pd.read_csv('nexxt_change_sales_listings_20241101_005703.csv')

# Load buyer data
buyer_df = pd.read_csv('dejuna data feed - buyer dejuna-new.csv')

# Ensure text columns are strings
seller_df = seller_df.astype(str)
buyer_df = buyer_df.astype(str)


# ----------------------------------
# Step 2: Data Preprocessing
# ----------------------------------

# 3. Define a helper function to convert date columns
def convert_date_columns(df, date_columns, date_format="%d.%m.%y"):
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
    return df

# 4. Convert date columns
# seller_df = convert_date_columns(seller_df, ['date'], "%d.%m.%y")

# # 5. Define cutoff date
# cutoff_date = pd.to_datetime('2024-01-01')

# # 6. Filter DataFrames
# seller_df_filtered = seller_df[seller_df['date'] > cutoff_date]

# # 7. Optional: Save filtered DataFrames
# seller_df_filtered.to_csv('nexxt_change_sales_listings_after_2024.csv', index=False)
# seller_df = seller_df_filtered;
def preprocess_text(text):
    # Convert to string and lowercase
    text = str(text).lower()
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Define text columns to use based on your data
seller_text_columns = ['title', 'description', 'long_description', 'branchen', 'preisvorstellung']
buyer_text_columns = ['Titel', 'summary', 'long description']

# Ensure the columns exist
seller_text_columns = [col for col in seller_text_columns if col in seller_df.columns]
buyer_text_columns = [col for col in buyer_text_columns if col in buyer_df.columns]

# Apply preprocessing and concatenate text columns
seller_df['processed_text'] = seller_df[seller_text_columns].apply(
    lambda row: ' '.join([preprocess_text(text) for text in row]), axis=1)
buyer_df['processed_text'] = buyer_df[buyer_text_columns].apply(
    lambda row: ' '.join([preprocess_text(text) for text in row]), axis=1)

# ----------------------------------
# Step 3: Industry Classification with Expanded Keywords/Synonyms
# ----------------------------------

# Define the keywords and synonyms
keywords_csv = """
Keyword,Synonym 1,Synonym 2,Synonym 3,Synonym 4,Synonym 5
Tischlerei,Schreinerei,Möbelbau,Tischlermeister,Schreinermeister,Möbelwerkstatt
Zimmerei,Zimmerer,Holzbau,Dachstuhl,Zimmermann,Dachdecker
Hausverwaltung,Immobilienverwaltung,Mietsverwaltung,WEG Verwaltung,Property Management,Immobilienmanagement
Pension,Frühstückspension,Herberge,Boutique Hotel,Gästehaus,Ferienhaus
Gebäudereinigung,Reinigungsfirma,Facility Management,Putzdienst,Hausreinigung,Reinigungsservice
Textilreinigung,Wäscherei,Chemische Reinigung,Bügelservice,Laundry Service,Kleiderreinigung
Heizung Sanitär,Heizungsbau,SHK,Heizung Sanitär Klima,Sanitär Heizung Klima,Installateur
Elektrofirma,Elektrobetrieb,Elektrotechnik,Elektroinstallation,Elektromeister,Elektrotechnikermeister
Dachdeckerei,Dachdeckerbetrieb,Dachdeckerfirma,Dachdeckermeister,Dacharbeiten,Dachsanierung
Malerfirma,Malerbetrieb,Maler,Malermeister,Anstrich,Renovierung
Metallbau,Metallbaufirma,Metallbaubetrieb,Metallbauer,Metallbauunternehmen,Metallbaumeister
Schlosserei,Schlosser,Metallverarbeitung,Stahlbau,Geländerbau,Schlossermeister
Bauunternehmen,Baufirma,Bauträger,Baumeister,Bauhandwerk,Baugeschäft
Maschinenbau,Maschinenbaufirma,Maschinenbauer,Anlagenbau,Engineering,Industrietechnik
Gartenbaubetrieb,Gartenbaufirma,Gartenbauunternehmen,Garten- und Landschaftsbau,Gärtnerei,Gärtner,Landschaftsbau
Glaserei,Glaser,Glasbau,Fensterbau,Spiegelherstellung,Glasbauunternehmen
Behälterbau,Behälteranlagen,Industriebehälter,Behälterbeschichtung,Tankbau,Tankherstellung
Tankschutz,Tankwartung,Tankreinigung,Tankinstandhaltung,Tankreparatur,Tankinstallation
Oberflächenbeschichtung,Oberflächenschutz,Lackierung,Beschichtungstechnik,Galvanik,Beschichtungsservice
Steinmetzbetrieb,Steinmetz,Natursteinbetrieb,Grabsteine,Marmorarbeiten,Steinbildhauer
Hausmeisterservice,Hausmeisterfirma,Hausmeister,Gebäudeservice,Facility Service,Gebäudemanagement
Pflegedienst,Ambulanter Pflegedienst,Krankenpflege,Altenpflege,Pflegeheim,Betreuung
Sanitätshaus,Orthopädietechnik,Rehatechnik,Medizintechnik,Homecare,Gesundheitstechnik
Zahnarztpraxis,Zahnarzt,Dentalpraxis,Mundhygiene,Kieferorthopädie,Zahnmedizin
Arztpraxis,Arzt,Medizinische Praxis,Allgemeinmedizin,Facharztpraxis,Mediziner
Tierarztpraxis,Tierarzt,Veterinärmedizin,Tierklinik,Veterinärpraxis,Tiermedizin
Logistik,Spedition,Transportdienst,Versanddienst,Kurierdienst,Fracht
Physiotherapie,Physiotherapiepraxis,Physiotherapeut,Krankengymnastik,Rehabilitation,Physiotherapeutische Praxis
Gastronomie,Restaurant,Café,Bistro,Gaststätte,Essen,Lokal
Eventmanagement,Veranstaltungsplanung,Eventorganisation,Kongressorganisation,Eventagentur,Eventservice
Onlinehandel,E-Commerce,Onlineshop,Internetverkauf,Webshop,Onlinegeschäft
Autohandel,Kfz-Handel,Gebrauchtwagenhandel,Autohaus,Fahrzeugverkauf,Autohändler
Buchhaltung,Finanzbuchhaltung,Accounting,Bilanzierung,Buchhaltungsservice,Lohnbuchhaltung
IT-Dienstleistungen,Informationstechnologie,IT-Service,Computerdienstleistungen,Softwareentwicklung,EDV-Service
Werbeagentur,Marketingagentur,Werbung,Marketing,Digitalagentur,Kommunikationsagentur
Rechtsanwaltskanzlei,Anwaltskanzlei,Rechtsberatung,Juridische Dienste,Anwalt,Rechtsanwalt
Steuerberatung,Steuerberater,Fiscalberatung,Buchprüfung,Steuerkanzlei,Tax Consulting
Notariat,Notar,Beurkundung,Beglaubigung,Notariatskanzlei,Notariatsservice
Architekturbüro,Architekt,Planungsbüro,Bauplanung,Architekturdesign,Bauzeichner
Ingenieurbüro,Engineering,Baustatik,Bauingenieurwesen,Technisches Büro,Planungsingenieur
Fotostudio,Fotograf,Fotoatelier,Portraitfotografie,Werbefotografie,Bildbearbeitung
Kosmetikstudio,Beauty Salon,Schönheitspflege,Kosmetikerin,Wellnessstudio,Nagelstudio
Friseursalon,Haarstudio,Coiffeur,Haarpflege,Friseurmeister,Haarmode
Reisebüro,Reisedienstleistungen,Urlaubsplanung,Travel Agency,Reisevermittlung,Reiseberatung
Sprachschule,Sprachunterricht,Fremdspracheninstitut,Sprachkurs,Sprachlernzentrum,Language School
Musikschule,Musikunterricht,Instrumentalunterricht,Musikakademie,Musikpädagogik,Musikzentrum
Sportverein,Sportclub,Sportgemeinschaft,Fitnessverein,Turnverein,Sportgemeinschaft
Fitnessstudio,Gym,Fitnesstraining,Sportstudio,Wellnesscenter,Fitnessclub
Kunstgalerie,Galerie,Kunsthandel,Kunstverkauf,Ausstellungsraum,Kunstvermittlung
Handwerksbetrieb,Gewerbebetrieb,Kleingewerbe,Handwerker,Handwerksfirma,Handwerksunternehmen
Landwirtschaft,Bauernhof,Agrarbetrieb,Agrarwirtschaft,Landwirt,Ackerbau
Fischerei,Angelfischerei,Fischzucht,Fischwirtschaft,Fischereibetrieb,Fischereiwesen
Bäckerei,Bäcker,Brotproduktion,Konditorei,Backwaren,Bäckereibetrieb
Metzgerei,Fleischerei,Fleischwaren,Wurstherstellung,Schlachterei,Metzger
Winzerei,Weingut,Weinbau,Weinherstellung,Kellerei,Weinproduktion
Brauer,Brauerei,Bierherstellung,Bierbrauerei,Braukunst,Bierproduktion
Hotel,Unterkunft,Beherbergungsbetrieb,Gastgewerbe,Hotellerie,Hospiz
Verlag,Buchverlag,Zeitschriftenverlag,Verlagswesen,Publikationshaus,Medienhaus
Druckerei,Druckhaus,Printservice,Druckservice,Druckproduktion,Druckbetrieb
Filmproduktion,Videoproduktion,Filmstudio,Filmgesellschaft,Filmherstellung,Medienproduktion
Musikproduktion,Plattenlabel,Recording Studio,Tonstudio,Musiklabel,Musikverlag
Theater,Schauspielhaus,Bühne,Oper,Bühnenkunst,Spielstätte
Museum,Austellungshaus,Kunstmuseum,Naturkundemuseum,Geschichtsmuseum,Museumsbetrieb
Bibliothek,Bücherei,Mediathek,Lesesaal,Buchausleihe,Literaturhaus
Apotheke,Pharmazie,Medikamentenverkauf,Pharmazeutika,Drogerie,Apothekenbetrieb
Supermarkt,Lebensmittelgeschäft,Einkaufsmarkt,Konsum,Biomarkt,Einkaufszentrum
Modegeschäft,Boutique,Kleidungsverkauf,Fashion Store,Textilhandel,Bekleidungsgeschäft
Juwelier,Schmuckgeschäft,Goldschmied,Schmuckhandel,Uhrenhandel,Edelsteinhandel
Optiker,Augenoptik,Brillenfachgeschäft,Sehhilfen,Kontaktlinsen,Augenoptiker
Blumenladen,Florist,Blumengeschäft,Blumenhandel,Gärtnerei,Blumenfachgeschäft
Sportgeschäft,Sportladen,Sportartikelhandel,Sportbedarf,Sportausrüstung,Sportshop
Elektronikhandel,Elektronikgeschäft,Elektrofachmarkt,Elektronikwaren,Technikladen,Elektronikshop
Möbelhandel,Möbelgeschäft,Wohnbedarf,Einrichtungshaus,Möbelhaus,Wohnaccessoires
Spielwarenhandel,Spielzeugladen,Spielzeuggeschäft,Spielehandel,Kinderbedarf,Spieleladen
Baumarkt,Baucenter,Baumarkthandel,Baustoffhandel,Heimwerkermarkt,Bau- und Gartenmarkt
Drogerie,Drogeriemarkt,Körperpflegeprodukte,Hygieneartikel,Schönheitsprodukte,Drogeriewaren
Tankstelle,Autohof,Kraftstoffhandel,Tankservice,Waschstraße,Servicestation
Autowerkstatt,Kfz-Werkstatt,Fahrzeugreparatur,Autoservice,Kfz-Meisterbetrieb,Reparaturwerkstatt
Fahrschule,Fahrunterricht,Führerscheinausbildung,Fahrausbildung,Fahrlehrer,Fahrschulbetrieb
Reinigungsdienst,Reinigungsservice,Gebäudereinigung,Unterhaltsreinigung,Fassadenreinigung,Industriereinigung
Sicherheitsdienst,Bewachungsdienst,Security,Personenschutz,Wachdienst,Sicherheitsservice
Entsorgungsbetrieb,Müllabfuhr,Recyclingunternehmen,Abfallwirtschaft,Schrottplatz,Abfallentsorgung
Installationsbetrieb,Installateur,Heizungsinstallateur,Sanitärinstallateur,Klempner,Gas- und Wasserinstallateur
Energieversorger,Stadtwerke,Elektrizitätswerk,Gasanbieter,Stromlieferant,Energieanbieter
Telekommunikation,Telekommunikationsdienstleister,Telefonanbieter,Internetprovider,Netzbetreiber,Kommunikationsdienst
Immobilienmakler,Immobilienvermittlung,Immobilienagentur,Hausvermittlung,Wohnungsvermittlung,Immobilienbüro
Finanzberatung,Vermögensberatung,Anlageberatung,Finanzdienstleistung,Investmentberatung,Bankberatung
Versicherungsmakler,Versicherungsvermittlung,Versicherungsagentur,Versicherungsberatung,Assekuranz,Versicherungsdienst
Eventtechnik,Veranstaltungstechnik,Bühnenbau,Lichttechnik,Tontechnik,Medientechnik
Kurierdienst,Paketdienst,Expressdienst,Botendienst,Lieferdienst,Kurierservice
Fahrradhandel,Fahrradgeschäft,Radladen,Zweiradhandel,Fahrradwerkstatt,Fahrradservice
Autovermietung,Mietwagenverleih,Fahrzeugvermietung,Car Rental,Leihwagen,Autoverleih
Softwareentwicklung,Programmierdienst,Softwarehaus,App-Entwicklung,Softwaredesign,IT-Entwicklung
Personalberatung,Personalvermittlung,Headhunting,Recruiting,Personalservice,Arbeitsvermittlung
Facility Management,Gebäudemanagement,Liegenschaftsverwaltung,Objektbetreuung,Gebäudeverwaltung,Instandhaltungsservice
Umzugsunternehmen,Umzugsservice,Transportservice,Umzugshilfe,Möbelspedition,Umzugsfirma
Veranstaltungslocation,Eventlocation,Tagungszentrum,Kongresszentrum,Veranstaltungshalle,Eventstätte
Anlagenbau,Industrieanlagenbau,Maschinen- und Anlagenbau,Fertigungsanlagen,Produktionsanlagen,Anlagenengineering
Reparaturservice,Wartungsdienst,Instandsetzung,Servicedienstleistung,Reparaturdienst,Instandhaltungsservice
Kunststoffverarbeitung,Kunststofftechnik,Kunststoffherstellung,Kunststoffindustrie,Plastikverarbeitung,Kunststofffertigung
Chemieunternehmen,Chemiebetrieb,Chemische Industrie,Chemikalienherstellung,Chemieproduktion,Chemiewerk
Pharmaunternehmen,Pharmaindustrie,Arzneimittelhersteller,Pharmakonzern,Medikamentenherstellung,Pharmabetrieb
Textilindustrie,Bekleidungsindustrie,Textilherstellung,Bekleidungsherstellung,Textilproduktion,Bekleidungsfertigung
Papierfabrik,Papierherstellung,Papierindustrie,Zellstoffproduktion,Papierproduktion,Papierverarbeitung
Holzverarbeitung,Holzindustrie,Sägewerk,Holzbearbeitung,Holzhandel,Holzfertigung
Metallverarbeitung,Metallindustrie,Stahlbau,Metallbearbeitung,Metallfertigung,Schweißtechnik
Glasherstellung,Glasindustrie,Glasproduktion,Glasfabrik,Glasverarbeitung,Glaswerke
Keramikherstellung,Keramikindustrie,Keramikproduktion,Keramikfabrik,Tonwarenherstellung,Porzellanherstellung
Gummiherstellung,Gummiindustrie,Gummiproduktion,Gummiwarenfabrik,Kautschukverarbeitung,Gummiverarbeitung
Elektronikherstellung,Elektronikindustrie,Elektronikproduktion,Elektrogeräteherstellung,Elektronikfertigung,Elektronikwarenproduktion
Kraftfahrzeugherstellung,Automobilindustrie,Autoproduktion,Fahrzeugbau,Automobilherstellung,Autofabrik
Luft- und Raumfahrt,Luftfahrtindustrie,Raumfahrttechnik,Flugzeugbau,Aerospace,Luftfahrttechnik
Schiffbau,Schiffswerft,Marinetechnik,Schiffsproduktion,Schiffstechnik,Schiffsindustrie
Möbelherstellung,Möbelindustrie,Möbelproduktion,Möbelfabrik,Möbeldesign,Möbelfertigung
Medizintechnik,Medizinische Geräte,Medizinprodukte,Healthcare Technology,Medizinausrüstung,Gesundheitstechnologie
Spielzeugherstellung,Spielwarenproduktion,Spielzeugindustrie,Spieleherstellung,Kinderspielwaren,Spielzeugfabrik
Musikinstrumentenbau,Instrumentenbau,Musikinstrumentenherstellung,Instrumentenfertigung,Musikinstrumentenindustrie,Instrumentenbauer
Schuhherstellung,Schuhindustrie,Schuhproduktion,Schuhfabrik,Schuhfertigung,Schuhmanufaktur
Bekleidungsherstellung,Textilfertigung,Kleidungsproduktion,Kleidungsfabrik,Bekleidungsfabrik,Kleidungsfertigung
Forschung und Entwicklung,Innovation,Research and Development,F&E,Laborforschung,Technologieentwicklung
Umwelttechnik,Umweltschutztechnik,Recyclingtechnik,Abwassertechnik,Erneuerbare Energien,Nachhaltigkeitstechnik
Energieversorgung,Stromversorgung,Gasanbieter,Energieerzeugung,Energieunternehmen,Energiedienstleister
Wasserversorgung,Wasserwirtschaft,Wasseraufbereitung,Wasserwerke,Trinkwasserversorgung,Wasserdienstleister
Abfallwirtschaft,Entsorgung,Recycling,Abfallentsorgung,Müllentsorgung,Wertstoffsammlung
Verkehrsbetrieb,Öffentlicher Nahverkehr,Busunternehmen,Bahngesellschaft,Verkehrsdienstleister,Personenverkehr
Lagerlogistik,Lagerhaltung,Logistikzentrum,Distributionszentrum,Lagerdienstleistung,Logistikdienstleister
Postdienstleister,Briefdienst,Kurierdienst,Postservice,Paketdienst,Postzustellung
Telekommunikationsdienstleister,Telefonanbieter,Internetdienstleister,Netzbetreiber,Kommunikationsanbieter,Telekomunternehmen
Bankwesen,Bank,Bankinstitut,Kreditinstitut,Geldinstitut,Finanzinstitut
Versicherungsgesellschaft,Versicherungsunternehmen,Assekuranz,Versicherungsdienstleister,Versicherungskonzern,Versicherer
Immobiliengesellschaft,Immobilienunternehmen,Bauträger,Immobilienentwicklung,Projektentwicklung,Immobilieninvestment
Rechtsberatung,Anwaltskanzlei,Juristische Beratung,Rechtsdienstleistung,Rechtsanwalt,Anwaltspraxis
Steuerberatungsgesellschaft,Wirtschaftsprüfung,Buchprüfung,Finanzberatung,Steuerkanzlei,Steuerdienstleistung
Unternehmensberatung,Beratungsgesellschaft,Managementberatung,Business Consulting,Consultingfirma,Beratungsunternehmen
Werbedienstleister,Werbeunternehmen,Marketingdienstleister,Marketingunternehmen,Werbeagentur,Kommunikationsagentur
Marktforschung,Meinungsforschung,Marktanalyse,Marketingforschung,Umfrageinstitut,Marktforschungsinstitut
Forschungseinrichtung,Forschungsinstitut,Labor,Laboratorium,Forschungszentrum,Wissenschaftliches Institut
Schulen,Bildungseinrichtung,Grundschule,Gymnasium,Förderschule,Bildungsinstitut
Hochschule,Universität,Fachhochschule,Akademie,Bildungsstätte,Hochschulinstitut
Krankenhaus,Hospital,Klinik,Medizinisches Zentrum,Universitätsklinik,Medizinische Einrichtung
Altenpflegeheim,Pflegeheim,Seniorenresidenz,Seniorenheim,Altenheim,Pflegeeinrichtung
Kindertagesstätte,Kita,Kindergarten,Tagesbetreuung,Kindereinrichtung,Krippe
Theaterbetrieb,Bühnenbetrieb,Bühnenhaus,Opernhaus,Schauspielhaus,Theaterhaus
Filmverleih,Kino,Kinobetrieb,Lichtspielhaus,Filmtheater,Kinoservice
Sportanlage,Sportstätte,Sportzentrum,Trainingszentrum,Sportplatz,Sportarena
Freizeitpark,Vergnügungspark,Erlebnispark,Freizeitzentrum,Freizeiteinrichtung,Freizeitattraktion
Tourismusdienstleister,Reiseveranstalter,Touristikunternehmen,Touristinformation,Touristikdienstleister,Tourismusunternehmen
Reinigungsmittelhersteller,Putzmittelhersteller,Reinigungschemikalienhersteller,Hygieneartikelhersteller,Waschmittelhersteller,Reinigungsproduktehersteller
Spielbank,Casino,Gambling,Spielhalle,Glücksspielbetrieb,Spielkasino
Lotterieunternehmen,Lottogesellschaft,Glücksspielanbieter,Tombola,Lotterieveranstalter,Lottoanbieter
Seefahrt,Schifffahrt,Reederei,Schiffsverkehr,Seetransport,Schiffsunternehmen
Luftfahrtgesellschaft,Airline,Fluggesellschaft,Fluglinie,Luftverkehrsunternehmen,Flugdienst
Bildungszentrum,Weiterbildungsinstitut,Erwachsenenbildung,Bildungseinrichtung,Bildungsakademie,Fortbildungszentrum
Forschungslabor,Laboratorium,Forschungsstätte,Forschungszentrum,Laborinstitut,Wissenschaftslabor
Werkstatt,Kfz-Werkstatt,Reparaturwerkstatt,Servicewerkstatt,Fahrzeugservice,Werkstattbetrieb
Tankstellenbetrieb,Tankstellenservice,Tankstellenunternehmen,Raststätte,Kraftstoffservice,Tankstellenkette
Veranstaltungsdienstleister,Eventdienstleister,Veranstaltungsservice,Eventservice,Eventausstattung,Veranstaltungstechnik
Medienunternehmen,Medienhaus,Rundfunkanstalt,Fernsehsender,Hörfunksender,Medienkonzern
Nachrichtenagentur,Presseagentur,News Agency,Pressedienst,Pressebüro,Nachrichtendienst
"""

# Parse the keywords CSV string into a dictionary
from io import StringIO

keywords_dict = {}
keywords_lines = keywords_csv.strip().split('\n')
header = keywords_lines[0].split(',')

for line in keywords_lines[1:]:
    # Skip empty lines
    if not line.strip():
        continue
    tokens = [token.strip() for token in line.split(',')]
    keyword = tokens[0]
    synonyms = tokens[1:]  # Include all remaining tokens as synonyms
    if keyword:
        keywords_dict[keyword.lower()] = [syn.lower() for syn in synonyms if syn]

# Create a mapping from synonyms to keywords and a set of all synonyms
synonym_to_keyword = {}
all_keywords_synonyms = set()
for keyword, synonyms in keywords_dict.items():
    all_terms = [keyword] + synonyms
    for term in all_terms:
        term_lower = term.lower()
        synonym_to_keyword[term_lower] = keyword
        all_keywords_synonyms.add(term_lower)

# Build a regex pattern to match any of the synonyms
# Sort synonyms by length to match longer phrases first
sorted_synonyms = sorted(all_keywords_synonyms, key=lambda x: -len(x))
escaped_synonyms = [re.escape(synonym) for synonym in sorted_synonyms]
pattern = r'\b(' + '|'.join(escaped_synonyms) + r')\b'

def classify_industry(text):
    matched_keywords = set(re.findall(pattern, text))
    industries = set()
    for term in matched_keywords:
        keyword = synonym_to_keyword[term]
        industries.add(keyword)
    return list(industries)

# Classify industries for buyers and sellers
seller_df['industries'] = seller_df['processed_text'].apply(classify_industry)
buyer_df['industries'] = buyer_df['processed_text'].apply(classify_industry)

# Remove entries with no industry classification
# seller_df = seller_df[seller_df['industries'].apply(len) > 0]
# buyer_df = buyer_df[buyer_df['industries'].apply(len) > 0]

# Check number of entries after industry classification
print(f"Number of sellers after industry classification: {len(seller_df)}")
print(f"Number of buyers after industry classification: {len(buyer_df)}")

# Ensure there are entries to process
if len(seller_df) == 0 or len(buyer_df) == 0:
    print("No sellers or buyers to process after industry classification.")
    exit()

# ----------------------------------
# Step 4: Location Preprocessing
# ----------------------------------

def extract_city_state(location_str):
    if pd.isnull(location_str):
        return ('', '')
    # Convert to lowercase
    location_str = str(location_str).lower().strip()
    # Handle multiple locations separated by newlines or commas
    location_str = location_str.replace('\n', ',').replace('/', ',')
    # Split on commas and other delimiters
    delimiters = [',', '-', ';', '>', ':']
    regex_pattern = '|'.join(map(re.escape, delimiters))
    parts = re.split(regex_pattern, location_str)
    parts = [part.strip() for part in parts if part.strip()]
    # Return the list of locations
    return parts

# Apply to seller and buyer dataframes
seller_df['locations'] = seller_df['location'].apply(extract_city_state)
buyer_df['locations'] = buyer_df['location (state + city)'].apply(extract_city_state)

# Standardize state and city names (optional, can be improved with a mapping)
def standardize_location_names(location_list):
    return [loc.lower() for loc in location_list]

seller_df['locations'] = seller_df['locations'].apply(standardize_location_names)
buyer_df['locations'] = buyer_df['locations'].apply(standardize_location_names)

# ----------------------------------
# Step 5: Matching Algorithm
# ----------------------------------

# Vectorize using TF-IDF with bigrams
vectorizer = TfidfVectorizer(ngram_range=(1, 2))
all_texts = pd.concat([seller_df['processed_text'], buyer_df['processed_text']], ignore_index=True)
tfidf_matrix = vectorizer.fit_transform(all_texts)

# Split the TF-IDF matrix
seller_tfidf = tfidf_matrix[:len(seller_df)]
buyer_tfidf = tfidf_matrix[len(seller_df):]

# Compute cosine similarity
similarity_matrix = cosine_similarity(buyer_tfidf, seller_tfidf)

# Set a similarity threshold
SIMILARITY_THRESHOLD = 0.40

# Initialize matches list to store match details
matches_list = []

# Matching loop with location and industry matching
for buyer_idx in range(similarity_matrix.shape[0]):
    buyer_info = buyer_df.iloc[buyer_idx]
    buyer_locations = set(buyer_info['locations'])
    buyer_industries = set(buyer_info['industries'])
    for seller_idx in range(similarity_matrix.shape[1]):
        similarity_score = similarity_matrix[buyer_idx, seller_idx]
        if similarity_score >= SIMILARITY_THRESHOLD:
            seller_info = seller_df.iloc[seller_idx]
            seller_locations = set(seller_info['locations'])
            seller_industries = set(seller_info['industries'])
            # Check for industry overlap
            industry_match = buyer_industries.intersection(seller_industries)
            if industry_match:
                # Check if any location matches (city OR state)
                location_match = buyer_locations.intersection(seller_locations)
                if location_match:
                    # Extract matched keywords
                    buyer_keywords = ', '.join(buyer_info['industries'])
                    seller_keywords = ', '.join(seller_info['industries'])
                    matches_list.append({
                        'buyer_idx': buyer_idx,
                        'seller_idx': seller_idx,
                        'similarity_score': similarity_score,
                        'matched_industries': ', '.join(industry_match),
                        'buyer_keywords': buyer_keywords,
                        'seller_keywords': seller_keywords,
                        'matched_locations': ', '.join(location_match),
                        'buyer_locations': ', '.join(buyer_locations),
                        'seller_locations': ', '.join(seller_locations),
                        'buyer_data': buyer_info.to_dict(),
                        'seller_data': seller_info.to_dict()
                    })

# ----------------------------------
# Step 6: Output Results
# ----------------------------------

# Output the matches and create Excel file
if matches_list:
    # Create a DataFrame from matches_list
    matches_df = pd.DataFrame(matches_list)
    
    # Expand buyer and seller data columns
    buyer_data_df = pd.DataFrame(matches_df['buyer_data'].tolist()).add_prefix('buyer_')
    seller_data_df = pd.DataFrame(matches_df['seller_data'].tolist()).add_prefix('seller_')
    
    # Combine all data into a single DataFrame
    final_df = pd.concat([matches_df.drop(['buyer_data', 'seller_data'], axis=1), buyer_data_df, seller_data_df], axis=1)
    
    # Reorder columns for better readability
    columns_order = [
        'buyer_idx', 'seller_idx', 'similarity_score', 'matched_industries',
        'buyer_keywords', 'seller_keywords', 'matched_locations',
        'buyer_locations', 'seller_locations'
    ] + list(buyer_data_df.columns) + list(seller_data_df.columns)
    final_df = final_df[columns_order]
    
    # Save matches to an Excel file
    final_df.to_excel('matches.xlsx', index=False)
    
    print("Matches have been saved to 'matches.xlsx'.")
else:
    print("No matches found.")
