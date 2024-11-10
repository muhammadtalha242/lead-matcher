import pandas as pd
import re
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
import spacy
from sklearn.preprocessing import LabelEncoder

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

# Load spaCy German Model
nlp = spacy.load('de_core_news_sm')

# ----------------------------------
# Step 3: Extract Industries using NER
# ----------------------------------

def extract_industry_entities(text):
    doc = nlp(text)
    industries = []
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'NORP', 'PRODUCT']:
            industries.append(ent.text)
    return industries

# Apply to seller and buyer dataframes
seller_df['extracted_industries'] = seller_df['processed_text'].apply(extract_industry_entities)
buyer_df['extracted_industries'] = buyer_df['processed_text'].apply(extract_industry_entities)

# ----------------------------------
# Step 4: Map Extracted Industries to NACE Codes
# ----------------------------------

# Expanded NACE mapping
nace_mapping = {
    'landwirtschaft': '01',
    'forstwirtschaft': '02',
    'fischerei': '03',
    'bergbau': '05-09',
    'verarbeitendes gewerbe': '10-33',
    'herstellung von nahrungsmitteln': '10',
    'herstellung von getränken': '11',
    'herstellung von textilien': '13',
    'herstellung von bekleidung': '14',
    'herstellung von holzwaren': '16',
    'papierherstellung': '17',
    'druckgewerbe': '18',
    'chemische industrie': '20',
    'pharmaindustrie': '21',
    'kunststoffindustrie': '22',
    'metallindustrie': '24-25',
    'maschinenbau': '28',
    'fahrzeugbau': '29-30',
    'möbelherstellung': '31',
    'energieversorgung': '35',
    'wasserversorgung': '36',
    'baugewerbe': '41-43',
    'großhandel': '46',
    'einzelhandel': '47',
    'kraftfahrzeughandel': '45',
    'verkehr und lagerei': '49-53',
    'post und kurierdienste': '53',
    'gastgewerbe': '55-56',
    'information und kommunikation': '58-63',
    'it-dienstleistungen': '62',
    'finanzdienstleistungen': '64-66',
    'versicherungen': '65',
    'immobilien': '68',
    'rechtsberatung': '69',
    'unternehmensberatung': '70',
    'architektur': '71',
    'forschung und entwicklung': '72',
    'werbung': '73',
    'arbeitsvermittlung': '78',
    'sicherheitsdienste': '80',
    'gebäudereinigung': '81',
    'bildung': '85',
    'gesundheitswesen': '86',
    'krankenhäuser': '86.1',
    'arztpraxen': '86.2',
    'pflegeheime': '87',
    'sozialwesen': '88',
    'kunst und unterhaltung': '90-93',
    'sportvereine': '93',
    'friseure': '96.02',
    'bestattungsunternehmen': '96.03',
    'reparatur von computern': '95.11',
    'herstellung von elektronischen bauteilen': '26',
    'telekommunikation': '61',
    'elektroinstallationen': '43.21',
    'sanitärinstallationen': '43.22',
    'maler und lackierer': '43.34',
    'dachdeckerei': '43.91',
    'großhandel mit maschinen': '46.6',
    'einzelhandel mit kosmetik': '47.75',
    'call center': '82.20',
    'reisebüros': '79.11',
    'eventmanagement': '82.30',
    'herstellung von schmuck': '32.12',
    'fotografie': '74.20',
    'verlagswesen': '58',
    'filmproduktion': '59.11',
    'rundfunk': '60',
    'programmierung': '62.01',
    'datenverarbeitung': '63.11',
    'webportale': '63.12',
    'bankwesen': '64.1',
    'versicherungsmakler': '66.22',
    'mietwagenunternehmen': '77.11',
    'transportvermittlung': '52.29',
    'lagerhaltung': '52.10',
    'personaldienstleistungen': '78.1',
    'sicherheitsberatung': '80.1',
    'gebäudebetreuung': '81.1',
    'gartengestaltung': '81.3',
    'reinigung von gebäuden': '81.21',
    'entsorgung': '38',
    'abwasserentsorgung': '37',
    'herstellung von möbeln': '31',
    'herstellung von sportgeräten': '32.30',
    'reparatur von haushaltsgeräten': '95.22',
    'herstellung von fahrzeugen': '29-30',
    'luftfahrt': '30.3',
    'raumfahrt': '30.3',
    'erbringung von dienstleistungen für die landwirtschaft': '01.6',
    'bäcker': '10.71',
    'metzger': '10.13',
    'herstellung von backwaren': '10.71',
    'herstellung von fleischwaren': '10.13',
    'getränkeherstellung': '11',
    'weinbau': '01.21',
    'brauerei': '11.05',
    'herstellung von bekleidung': '14',
    'druckerei': '18.12',
    'herstellung von medizinischen geräten': '32.5',
    'herstellung von pharmazeutischen erzeugnissen': '21',
    'optiker': '47.78',
    'einzelhandel mit brillen': '47.78',
    'spielzeugherstellung': '32.4',
    'sportvereine': '93.12',
    'freiberufliche wissenschaftliche tätigkeiten': '74.9',
    'herstellung von software': '62.01',
    'datenverarbeitung und hosting': '63.11',
    'internetportale': '63.12',
    'versicherung': '65',
    'rückversicherung': '65.2',
    'rentenversicherung': '65.3',
    'makler': '66.22',
    'vermietung von kraftfahrzeugen': '77.11',
    'vermietung von baumaschinen': '77.32',
    'transport': '49',
    'personenbeförderung': '49.3',
    'güterbeförderung': '49.4',
    'taxiunternehmen': '49.32',
    'speditionen': '52.29',
    'lagerung': '52.10',
    'postdienste': '53',
    'kurierdienste': '53.2',
    'hotellerie': '55',
    'gastronomie': '56',
    'restaurants': '56.1',
    'cafés': '56.1',
    'bars': '56.3',
    'caterer': '56.21',
    'informationsdienstleistungen': '63',
    'bibliotheken': '91.01',
    'archive': '91.01',
    'museen': '91.02',
    'rechtsanwälte': '69.1',
    'notare': '69.1',
    'wirtschaftsprüfer': '69.2',
    'steuerberater': '69.2',
    'werbeagenturen': '73.11',
    'markt- und meinungsforschung': '73.20',
    'industriebau': '41.2',
    'wohnungsbau': '41.2',
    'abbrucharbeiten': '43.11',
    'vorbereitende baustellenarbeiten': '43.12',
    'installation von gas- wasser- heizungsanlagen': '43.22',
    'installation von elektrischen anlagen': '43.21',
    'isolierarbeiten': '43.29',
    'malerbetriebe': '43.34',
    'gerüstbau': '43.99',
    'dämmarbeiten': '43.29',
    'reparatur von elektronischen und optischen geräten': '33.13',
    'herstellung von feinmechanischen instrumenten': '26.5',
    'herstellung von uhren': '26.52',
    'herstellung von medizinischen instrumenten': '32.5',
    'herstellung von spielen und spielzeug': '32.4',
    'herstellung von sportartikeln': '32.3',
    'herstellung von schmuck und verwandten erzeugnissen': '32.1',
    'herstellung von musikinstrumenten': '32.2',
    'reparatur von sonstigen waren': '95.2',
    'wäscherei': '96.01',
    'textilreinigung': '96.01',
    'friseursalons': '96.02',
    'kosmetiksalons': '96.02',
    'bestattungswesen': '96.03',
    'fitnesscenter': '93.13',
    'tätowierstudios': '96.09',
    'sonstige persönliche dienstleistungen': '96.09',
    'hausmeisterdienste': '81.1',
    'gartengestaltung und pflege': '81.3',
    'verpackungsdienstleistungen': '82.92',
    'bürodienstleistungen': '82.11',
    'callcenter-dienstleistungen': '82.20',
    'inkassobüros': '82.91',
    'messen und ausstellungen': '82.30',
    'kongressveranstalter': '82.30',
    'reinigung von gebäuden': '81.21',
    'straßenreinigung': '81.29',
    'landschaftsbau': '81.3',
    'öffentliche verwaltung': '84',
    'verteidigung': '84.22',
    'sozialversicherung': '84.3',
    'erziehung und unterricht': '85',
    'vorschulbildung': '85.1',
    'schulbildung': '85.2',
    'hochschulbildung': '85.4',
    'erwachsenenbildung': '85.5',
    'gesundheitswesen': '86',
    'allgemeinmedizin': '86.21',
    'facharztpraxen': '86.22',
    'krankenhäuser': '86.1',
    'pflegeheime': '87.1',
    'altenheime': '87.3',
    'sozialwesen': '88',
    'kinderbetreuung': '88.91',
    'jugendarbeit': '88.99',
    'theater': '90.01',
    'musikveranstaltungen': '90.04',
    'museen': '91.02',
    'bibliotheken': '91.01',
    'sportvereine': '93.12',
    'freizeitparks': '93.21',
    'glücksspiel und wetten': '92',
    'lotterien': '92.00',
    'tageszeitungen': '58.13',
    'zeitschriftenverlage': '58.14',
    'buchverlage': '58.11',
    'herstellung von datenverarbeitungsgeräten': '26.20',
    'reparatur von haushaltsgeräten und hausrat': '95.2',
    'reparatur von computern und kommunikationsgeräten': '95.1',
    'sekundarschulen': '85.31',
    'finanzämter': '84.11',
    'anwaltskanzleien': '69.1',
    'logopädie': '86.90',
    'zahnarztpraxen': '86.23',
    'tierarztpraxen': '75',
    'veterinärwesen': '75',
    'klavierbauer': '32.20',
    'musikschulen': '85.52',
    'fotolabore': '74.20',
    'grafikdesign': '74.10',
    'herstellung von lederschuhen': '15.20',
    'sägewerke': '16.10',
    'herstellung von holzprodukten': '16.2',
    'herstellung von papier und pappe': '17.1',
    'herstellung von papierwaren': '17.2',
    'herstellung von chemikalien': '20',
    'herstellung von düngemitteln': '20.15',
    'herstellung von kunststoffen': '22.2',
    'herstellung von glaswaren': '23.1',
    'herstellung von keramik': '23.2',
    'herstellung von beton': '23.5',
    'herstellung von metallwaren': '25',
    'herstellung von stahlkonstruktionen': '25.11',
    'herstellung von werkzeugen': '25.73',
    'herstellung von elektronischen bauteilen': '26.1',
    'maschinenbau': '28',
    'herstellung von büromaschinen': '28.23',
    'herstellung von landmaschinen': '28.3',
    'herstellung von haushaltsgeräten': '27.5',
    'herstellung von fahrzeugen': '29',
    'herstellung von eisenbahnlokomotiven': '30.2',
    'herstellung von luft- und raumfahrzeugen': '30.3',
    'herstellung von motorrädern': '30.91',
    'herstellung von möbeln': '31',
    'herstellung von schmuck': '32.12',
    'herstellung von medizinischen und zahnmedizinischen instrumenten': '32.5',
    'herstellung von spielen und spielzeug': '32.4',
    'herstellung von sportgeräten': '32.3',
    'herstellung von musikinstrumenten': '32.2',
    # Add more mappings as needed
}


def extract_industry_keywords(text):
    industry_terms = list(nace_mapping.keys())
    industries = []
    text_lower = text.lower()
    for term in industry_terms:
        if term in text_lower:
            industries.append(term)
    return industries

# Apply to seller and buyer dataframes
seller_df['extracted_industries'] = seller_df['processed_text'].apply(extract_industry_keywords)
buyer_df['extracted_industries'] = buyer_df['processed_text'].apply(extract_industry_keywords)


# ----------------------------------
# Step 5: Location Preprocessing
# ----------------------------------

def extract_locations(location_str):
    if pd.isnull(location_str):
        return []
    # Convert to lowercase
    location_str = str(location_str).lower().strip()
    # Replace newlines and slashes with commas
    location_str = location_str.replace('\n', ',').replace('/', ',')
    # Split on commas and other delimiters
    delimiters = [',', '-', ';', '>', ':']
    regex_pattern = '|'.join(map(re.escape, delimiters))
    parts = re.split(regex_pattern, location_str)
    parts = [part.strip() for part in parts if part.strip()]
    # Return unique locations
    return list(set(parts))

# Apply to seller and buyer dataframes
seller_df['locations'] = seller_df['location'].apply(extract_locations)
buyer_df['locations'] = buyer_df['location (state + city)'].apply(extract_locations)

# Standardize location names (optional)
german_states = [
    'baden-wuerttemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
    'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
    'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
    'sachsen-anhalt', 'schleswig-holstein', 'thueringen'
]

def standardize_location_names(location_list):
    standardized_locations = []
    for loc in location_list:
        loc_lower = loc.lower()
        loc_lower = loc_lower.replace('ü', 'ue').replace('ö', 'oe').replace('ä', 'ae').replace('ß', 'ss')
        loc_lower = loc_lower.strip()
        if loc_lower in german_states:
            standardized_locations.append(loc_lower)
        else:
            # Handle city names or keep as is
            standardized_locations.append(loc_lower)
    return list(set(standardized_locations))

seller_df['locations'] = seller_df['locations'].apply(standardize_location_names)
buyer_df['locations'] = buyer_df['locations'].apply(standardize_location_names)

# ----------------------------------
# Step 6: Matching Algorithm
# ----------------------------------

from torch.nn.functional import cosine_similarity

# Load the model for semantic similarity
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

# Encode the texts
print("Encoding seller texts...")
seller_embeddings = model.encode(seller_df['processed_text'].tolist(), convert_to_tensor=True, show_progress_bar=True)

print("Encoding buyer texts...")
buyer_embeddings = model.encode(buyer_df['processed_text'].tolist(), convert_to_tensor=True, show_progress_bar=True)

# Set a similarity threshold
SIMILARITY_THRESHOLD = 0.5  # Adjust as needed

matches_list = []

# Matching loop
print("Finding matches...")
for buyer_idx in range(len(buyer_df)):
    buyer_info = buyer_df.iloc[buyer_idx]
    buyer_locations = set(buyer_info['locations'])
    buyer_nace_codes = set(buyer_info['extracted_industries'])
    if not buyer_nace_codes:
        continue  # Skip if no industry codes
    for seller_idx in range(len(seller_df)):
        seller_info = seller_df.iloc[seller_idx]
        seller_locations = set(seller_info['locations'])
        seller_nace_codes = set(seller_info['extracted_industries'])
        if not seller_nace_codes:
            continue  # Skip if no industry codes
        # Check for exact location match
        location_match = buyer_locations.intersection(seller_locations)
        if location_match:
            # Check for industry code match
            industry_match = buyer_nace_codes.intersection(seller_nace_codes)
            if industry_match:
                # Compute semantic similarity
                similarity_score = cosine_similarity(
                    buyer_embeddings[buyer_idx].unsqueeze(0),
                    seller_embeddings[seller_idx].unsqueeze(0)
                ).item()
                if similarity_score >= SIMILARITY_THRESHOLD:
                    matches_list.append({
                        'buyer_idx': buyer_idx,
                        'seller_idx': seller_idx,
                        'similarity_score': similarity_score,
                        'matched_locations': ', '.join(location_match),
                        'buyer_locations': ', '.join(buyer_locations),
                        'seller_locations': ', '.join(seller_locations),
                        'matched_industries': ', '.join(industry_match),
                        'buyer_nace_codes': ', '.join(buyer_nace_codes),
                        'seller_nace_codes': ', '.join(seller_nace_codes),
                        'buyer_data': buyer_info.to_dict(),
                        'seller_data': seller_info.to_dict()
                    })

# ----------------------------------
# Step 7: Output Results
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
        'buyer_idx', 'seller_idx', 'similarity_score', 'matched_locations', 'matched_industries',
        'buyer_locations', 'seller_locations', 'buyer_nace_codes', 'seller_nace_codes'
    ] + list(buyer_data_df.columns) + list(seller_data_df.columns)
    final_df = final_df[columns_order]
    
    # Save matches to an Excel file
    final_df.to_excel('matches.xlsx', index=False)
    
    print("Matches have been saved to 'matches.xlsx'.")
else:
    print("No matches found.")
