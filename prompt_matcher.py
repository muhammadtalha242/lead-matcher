# # Step 1: Load the Data
# import pandas as pd
# from sentence_transformers import SentenceTransformer, util
# import numpy as np

# # Read buyers.csv and sellers.csv
# buyers = pd.read_csv('./data/buyer_dejuna.csv')
# sellers = pd.read_csv('./data/nexxt_change_sales_listings.csv')

# # Handle missing 'industries' column
# if 'industries' not in buyers.columns:
#     buyers['industries'] = ''
# if 'industries' not in sellers.columns:
#     sellers['industries'] = ''

# # Step 2: Preprocess the Data
# def preprocess_text(text):
#     # Lowercase and strip whitespace
#     if isinstance(text, str):
#         text = text.lower().strip()
#         # Replace German umlauts
#         text = text.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
#     else:
#         text = ''
#     return text

# buyers['title'] = buyers['title'].apply(preprocess_text)
# buyers['description'] = buyers['description'].apply(preprocess_text)
# buyers['long_description'] = buyers['long_description'].apply(preprocess_text)
# buyers['location'] = buyers['location'].apply(preprocess_text)
# buyers['industries'] = buyers['industries'].apply(preprocess_text)

# sellers['title'] = sellers['title'].apply(preprocess_text)
# sellers['description'] = sellers['description'].apply(preprocess_text)
# sellers['long_description'] = sellers['long_description'].apply(preprocess_text)
# sellers['location'] = sellers['location'].apply(preprocess_text)
# sellers['industries'] = sellers['industries'].apply(preprocess_text)

# # Normalize locations
# def normalize_location(loc):
#     # Split hierarchical locations
#     if isinstance(loc, str):
#         loc_list = [l.strip() for l in loc.split('>')]
#         # Remove empty strings
#         loc_list = [l for l in loc_list if l]
#         return loc_list
#     else:
#         return []

# buyers['location_list'] = buyers['location'].apply(normalize_location)
# sellers['location_list'] = sellers['location'].apply(normalize_location)

# # Step 3: Perform Matching

# # Initialize the sentence transformer model
# model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# # Function to compute semantic similarity
# def compute_similarity(buyer_text, seller_text):
#     buyer_emb = model.encode(buyer_text, convert_to_tensor=True)
#     seller_emb = model.encode(seller_text, convert_to_tensor=True)
#     cosine_scores = util.cos_sim(buyer_emb, seller_emb)
#     return cosine_scores.item()

# # We will store matches in a list
# matches = []

# # Set similarity threshold
# SIMILARITY_THRESHOLD = 0.65  # 80%

# # Iterate over buyers and sellers to find matches
# for idx_b, buyer in buyers.iterrows():
#     for idx_s, seller in sellers.iterrows():
#         # Check Location Match
#         location_match = False
#         for loc_b in buyer['location_list']:
#             for loc_s in seller['location_list']:
#                 if loc_b == loc_s:
#                     location_match = True
#                     break
#             if location_match:
#                 break
#         if not location_match:
#             continue  # Skip this seller

#         # Check Industry Match (if industries columns are present and not empty)
#         industry_match = True
#         if buyer['industries'] and seller['industries']:
#             buyer_industries = set(buyer['industries'].split(','))
#             seller_industries = set(seller['industries'].split(','))
#             if not buyer_industries.intersection(seller_industries):
#                 industry_match = False
#                 continue  # Skip this seller

#         # Compute semantic similarity
#         buyer_text = buyer['title'] + ' ' + buyer['description'] + ' ' + buyer['long_description']
#         seller_text = seller['title'] + ' ' + seller['description'] + ' ' + seller['long_description']
#         similarity_score = compute_similarity(buyer_text, seller_text)

#         if similarity_score >= SIMILARITY_THRESHOLD:
#             # Append the match
#             match = {
#                 'buyer_title': buyer['title'],
#                 'buyer_description': buyer['description'],
#                 'buyer_long_description': buyer['long_description'],
#                 'buyer_location': buyer['location'],
#                 'buyer_industries': buyer['industries'],
#                 'seller_title': seller['title'],
#                 'seller_description': seller['description'],
#                 'seller_long_description': seller['long_description'],
#                 'seller_location': seller['location'],
#                 'seller_industries': seller['industries']
#             }
#             matches.append(match)

# # Convert matches to DataFrame
# matches_df = pd.DataFrame(matches)
# print("🚀 ~ matches_df:", len(matches_df))

# # Step 5: Output the Results
# matches_df.to_csv('./matches/matches.csv', index=False)

# import pandas as pd
# import numpy as np
# import nltk
# import re

# # Import NLP libraries
# import spacy
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.preprocessing import normalize

# # Load pre-trained language model
# nlp = spacy.load('de_core_news_md')  # German language model

# # Load industry classification data (Assuming we have NACE codes)
# nace_codes = pd.read_csv('nace_codes.csv')  # Contains 'code', 'description'

# # Load business domain taxonomy (Assuming a predefined taxonomy)
# taxonomy = {
#     'Logistik': ['Spedition', 'Transport', 'Lagerlogistik', 'Fracht', 'Versand', 'Lieferung'],
#     'Gesundheit': ['Pflegedienst', 'Krankenpflege', 'Ambulante Pflege', 'Krankenhaus', 'Apotheke', 'Medizin', 'Gesundheitswesen'],
#     'Immobilien': ['Hausverwaltung', 'Immobilienverwaltung', 'Immobilienmakler', 'Immobilienbewertung', 'Facility Management'],
#     'Handwerk': ['Schreinerei', 'Tischlerei', 'Fensterbau', 'Maler', 'Installateur', 'Elektriker', 'Dachdecker', 'Sanitär', 'Heizung', 'Kfz-Werkstatt'],
#     'Einzelhandel': ['Laden', 'Geschäft', 'Supermarkt', 'Boutique', 'Einzelhandel', 'Handel'],
#     'Großhandel': ['Großhandel', 'Großmarkt', 'Handelsunternehmen'],
#     'Informationstechnologie': ['IT', 'Software', 'Hardware', 'EDV', 'Programmierer', 'Webentwicklung', 'Cybersecurity', 'Informatik', 'Cloud', 'Datenverarbeitung'],
#     'Finanzen': ['Finanzdienstleistungen', 'Bank', 'Kreditinstitut', 'Vermögensverwaltung', 'Finanzberatung', 'Buchhaltung', 'Steuerberatung'],
#     'Versicherung': ['Versicherungsagentur', 'Versicherungsmakler', 'Versicherung', 'Policen'],
#     'Gastronomie': ['Restaurant', 'Café', 'Bar', 'Gastronomie', 'Catering', 'Hotel', 'Gastgewerbe'],
#     'Bildung': ['Schule', 'Bildungsinstitut', 'Nachhilfe', 'Sprachschule', 'Universität', 'Ausbildung', 'Weiterbildung'],
#     'Energie': ['Energieversorgung', 'Strom', 'Gas', 'Erneuerbare Energien', 'Photovoltaik', 'Windkraft', 'Solarenergie'],
#     'Landwirtschaft': ['Landwirtschaft', 'Bauernhof', 'Agrarwirtschaft', 'Forstwirtschaft', 'Gartenbau'],
#     'Automobil': ['Autohandel', 'Autohaus', 'Fahrzeughandel', 'Kfz-Werkstatt', 'Autovermietung', 'Fahrzeugbau'],
#     'Pharma': ['Pharma', 'Arzneimittel', 'Medikamente', 'Pharmaindustrie', 'Biotechnologie'],
#     'Chemie': ['Chemie', 'Chemikalien', 'Chemieindustrie', 'Petrochemie'],
#     'Telekommunikation': ['Telekommunikation', 'Telefonie', 'Internetanbieter', 'Mobilfunk', 'Netzwerkbetreiber'],
#     'Medien': ['Medien', 'Verlag', 'Zeitung', 'Rundfunk', 'Fernsehen', 'Werbung', 'Marketing', 'PR', 'Kommunikation'],
#     'Transport': ['Personenbeförderung', 'Taxi', 'Busunternehmen', 'Schifffahrt', 'Fluggesellschaft', 'Bahnverkehr'],
#     'Bau': ['Bauunternehmen', 'Hochbau', 'Tiefbau', 'Bauträger', 'Baudienstleistungen', 'Architektur', 'Ingenieurbüro'],
#     'Metallverarbeitung': ['Metallbau', 'Schlosserei', 'Stahlbau', 'Maschinenbau', 'Werkzeugbau', 'Gießerei'],
#     'Textil': ['Textilindustrie', 'Bekleidung', 'Mode', 'Schneiderei', 'Textilherstellung'],
#     'Lebensmittel': ['Lebensmittelhandel', 'Bäckerei', 'Metzgerei', 'Lebensmittelproduktion', 'Nahrungsmittel'],
#     'Elektronik': ['Elektronik', 'Elektrogeräte', 'Elektronikhandel', 'Elektrotechnik'],
#     'Consulting': ['Beratung', 'Unternehmensberatung', 'Managementberatung', 'Strategieberatung', 'IT-Beratung'],
#     'Recht': ['Rechtsanwalt', 'Kanzlei', 'Rechtsberatung', 'Notar', 'Anwaltskanzlei'],
#     'Personal': ['Personalvermittlung', 'Zeitarbeit', 'Personaldienstleistungen', 'Headhunter', 'Recruiting'],
#     'Umwelt': ['Umweltdienstleistungen', 'Entsorgung', 'Recycling', 'Abfallwirtschaft', 'Umwelttechnik'],
#     'Sport': ['Fitnessstudio', 'Sportverein', 'Sportgeschäft', 'Freizeit', 'Wellness'],
#     'Kreativwirtschaft': ['Design', 'Grafikdesign', 'Fotografie', 'Kunst', 'Kultur', 'Filmproduktion', 'Musik'],
#     'Event': ['Eventmanagement', 'Veranstaltungen', 'Messe', 'Kongress', 'Eventagentur'],
#     'E-Commerce': ['Onlinehandel', 'Onlineshop', 'E-Commerce', 'Internetversandhandel', 'E-Business'],
#     'FinTech': ['FinTech', 'Finanztechnologie', 'Digital Banking', 'Payment'],
#     'Bildungstechnologie': ['EdTech', 'Bildungstechnologie', 'E-Learning', 'Lernplattform'],
#     'Immobilienentwicklung': ['Projektentwicklung', 'Bauträger', 'Immobilienentwicklung', 'Stadtplanung'],
#     'Sicherheitsdienste': ['Sicherheitsdienst', 'Security', 'Objektschutz', 'Personenschutz', 'Überwachung'],
#     'Reise': ['Reisebüro', 'Tourismus', 'Reiseveranstalter', 'Freizeitindustrie'],
#     'Holzindustrie': ['Holzverarbeitung', 'Sägewerk', 'Möbelbau', 'Holzhandel'],
#     'Papierindustrie': ['Papierherstellung', 'Druckerei', 'Verpackung'],
#     'Glasindustrie': ['Glasherstellung', 'Glasverarbeitung', 'Glashandel'],
#     'Keramik': ['Keramik', 'Töpferei', 'Fliesen'],
#     'Kosmetik': ['Kosmetik', 'Schönheitspflege', 'Parfümerie', 'Friseur'],
#     'Luft- und Raumfahrt': ['Flugzeugbau', 'Luftfahrttechnik', 'Raumfahrt'],
#     'Öffentlicher Sektor': ['Behörde', 'Verwaltung', 'Öffentlicher Dienst', 'Gemeinde'],
#     'Non-Profit': ['Verein', 'Stiftung', 'Gemeinnützige Organisation', 'NGO'],
#     'Sonstige Dienstleistungen': ['Dienstleistungen', 'Service', 'Support']
# }
# # Function to assign taxonomy categories based on description
# def assign_taxonomy_category(description):
#     categories = []
#     for category, keywords in taxonomy.items():
#         for keyword in keywords:
#             if keyword.lower() in description.lower():
#                 categories.append(category)
#                 break
#     return categories

# # Function to preprocess text
# def preprocess_text(text):
#     # Lowercase
#     text = text.lower()
#     # Remove non-alphabetic characters
#     text = re.sub(r'[^a-zäöüß\s]', '', text)
#     # Lemmatization and stopword removal
#     doc = nlp(text)
#     tokens = [token.lemma_ for token in doc if not token.is_stop]
#     return ' '.join(tokens)

# # Load buyer and seller data
# # # Read buyers.csv and sellers.csv
# buyers = pd.read_csv('./data/buyer_dejuna.csv')
# sellers = pd.read_csv('./data/nexxt_change_sales_listings.csv')

# data = pd.DataFrame()


# # Preprocess descriptions
# data['buyer_full_description'] = buyers['title'].astype(str) + ' ' + buyers['description'].astype(str) + ' ' + buyers['long_description'].astype(str)
# data['seller_full_description'] = sellers['title'].astype(str) + ' ' + sellers['description'].astype(str) + ' ' + sellers['long_description'].astype(str)
# data['buyer_location']= buyers['location'].astype(str)
# data['seller_location']= sellers['location'].astype(str)
# data['buyer_processed'] = data['buyer_full_description'].apply(preprocess_text)
# data['seller_processed'] = data['seller_full_description'].apply(preprocess_text)

# # Assign taxonomy categories
# data['buyer_categories'] = data['buyer_full_description'].apply(assign_taxonomy_category)
# data['seller_categories'] = data['seller_full_description'].apply(assign_taxonomy_category)

# # Assign industry codes (Placeholder function)
# def assign_industry_code(description):
#     # This function should match the description to NACE codes
#     # For simplicity, we will assign codes based on keywords
#     for index, row in nace_codes.iterrows():
#         if row['description'].lower() in description.lower():
#             return row['code']
#     return None

# data['buyer_industry_code'] = data['buyer_full_description'].apply(assign_industry_code)
# data['seller_industry_code'] = data['seller_full_description'].apply(assign_industry_code)

# # Calculate semantic similarity using embeddings
# def get_embedding(text):
#     doc = nlp(text)
#     return doc.vector

# data['buyer_embedding'] = data['buyer_processed'].apply(get_embedding)
# data['seller_embedding'] = data['seller_processed'].apply(get_embedding)

# # Function to calculate cosine similarity
# def calculate_cosine_similarity(vec1, vec2):
#     vec1 = vec1.reshape(1, -1)
#     vec2 = vec2.reshape(1, -1)
#     similarity = cosine_similarity(vec1, vec2)
#     return similarity[0][0]

# data['semantic_similarity'] = data.apply(lambda row: calculate_cosine_similarity(row['buyer_embedding'], row['seller_embedding']), axis=1)

# # Calculate category match score
# def category_match_score(buyer_categories, seller_categories):
#     if not buyer_categories or not seller_categories:
#         return 0
#     match_count = len(set(buyer_categories) & set(seller_categories))
#     total_categories = len(set(buyer_categories) | set(seller_categories))
#     return match_count / total_categories

# data['category_similarity'] = data.apply(lambda row: category_match_score(row['buyer_categories'], row['seller_categories']), axis=1)

# # Industry code match score
# def industry_code_match_score(buyer_code, seller_code):
#     if pd.isna(buyer_code) or pd.isna(seller_code):
#         return 0
#     return 1 if buyer_code == seller_code else 0

# data['industry_similarity'] = data.apply(lambda row: industry_code_match_score(row['buyer_industry_code'], row['seller_industry_code']), axis=1)

# # Location match score (Simplified for demonstration)
# def location_match_score(buyer_location, seller_location):
#     # Check if any of the buyer's locations are in the seller's location
#     buyer_locations = [loc.strip().lower() for loc in buyer_location.split('>')]
#     seller_locations = [loc.strip().lower() for loc in seller_location.split('>')]
#     match = any(loc in seller_locations for loc in buyer_locations)
#     return 1 if match else 0

# data['location_similarity'] = data.apply(lambda row: location_match_score(row['buyer_location'], row['seller_location']), axis=1)

# # Calculate overall similarity score with weighted components
# def overall_similarity(row):
#     # Weights can be adjusted based on importance
#     weights = {
#         'semantic': 0.4,
#         'category': 0.3,
#         'industry': 0.2,
#         'location': 0.1
#     }
#     score = (
#         weights['semantic'] * row['semantic_similarity'] +
#         weights['category'] * row['category_similarity'] +
#         weights['industry'] * row['industry_similarity'] +
#         weights['location'] * row['location_similarity']
#     )
#     return score

# data['overall_similarity'] = data.apply(overall_similarity, axis=1)

# # Set similarity threshold
# SIMILARITY_THRESHOLD = 0.60

# # Filter matches based on the threshold
# valid_matches = data[data['overall_similarity'] >= SIMILARITY_THRESHOLD]

# # Save valid matches
# valid_matches.to_csv('./matches/valid_matches.csv', index=False)
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Ensure nltk stopwords are downloaded
nltk.download('stopwords')

# Set up logging
logging.basicConfig(level=logging.INFO)

def preprocess_text(text):
    if pd.isnull(text):
        return ''
    # Lowercase the text
    text = text.lower()
    # Remove numbers and special characters
    text = re.sub(r'[^a-zA-ZäöüÄÖÜß\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove stopwords
    stop_words = set(stopwords.words('german'))
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    # Join tokens back to string
    text = ' '.join(tokens)
    return text

def extract_state_city(location):
    if pd.isnull(location):
        return ''
    parts = location.split('>')
    parts = [part.strip() for part in parts]
    if len(parts) >= 2:
        return ' > '.join(parts[:2])
    else:
        return location.strip()

def combine_text_fields(row):
    return row['title_preprocessed'] + ' ' + row['description_preprocessed'] + ' ' + row['long_description_preprocessed']

def main():
    # Load buyer and seller datasets
    buyers_df = pd.read_csv('./data/buyer_dejuna.csv')
    sellers_df = pd.read_csv('./data/nexxt_change_sales_listings.csv')
    
    # Preprocess buyers' text fields
    logging.info('Preprocessing buyers\' text fields...')
    buyers_df['title_preprocessed'] = buyers_df['title'].apply(preprocess_text)
    buyers_df['description_preprocessed'] = buyers_df['description'].apply(preprocess_text)
    buyers_df['long_description_preprocessed'] = buyers_df['long_description'].apply(preprocess_text)
    
    # Preprocess sellers' text fields
    logging.info('Preprocessing sellers\' text fields...')
    sellers_df['title_preprocessed'] = sellers_df['title'].apply(preprocess_text)
    sellers_df['description_preprocessed'] = sellers_df['description'].apply(preprocess_text)
    sellers_df['long_description_preprocessed'] = sellers_df['long_description'].apply(preprocess_text)
    
    # Combine text fields
    logging.info('Combining text fields...')
    buyers_df['combined_text'] = buyers_df.apply(combine_text_fields, axis=1)
    sellers_df['combined_text'] = sellers_df.apply(combine_text_fields, axis=1)
    
    # Extract state and city from location
    logging.info('Extracting state and city from location...')
    buyers_df['state_city'] = buyers_df['location'].apply(extract_state_city)
    sellers_df['state_city'] = sellers_df['location'].apply(extract_state_city)
    
    # Initialize the model
    logging.info('Loading the Sentence Transformer model...')
    model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
    model = SentenceTransformer(model_name)
    
    # Set similarity threshold
    similarity_threshold = 0.8
    
    # Initialize matches list
    matches = []
    
    # Get unique state_city values
    state_city_list = buyers_df['state_city'].unique()
    
    for state_city in state_city_list:
        logging.info(f'Processing location: {state_city}')
        # Get buyers and sellers with this state_city
        buyers_subset = buyers_df[buyers_df['state_city'] == state_city].reset_index(drop=True)
        sellers_subset = sellers_df[sellers_df['state_city'] == state_city].reset_index(drop=True)
        
        if buyers_subset.empty or sellers_subset.empty:
            logging.info('No matching buyers or sellers for this location.')
            continue  # No matching sellers or buyers for this location
        
        # Encode sellers' combined_text once for this state_city
        logging.info('Encoding sellers\' text...')
        sellers_embeddings_subset = model.encode(sellers_subset['combined_text'].tolist(), convert_to_tensor=True)
        
        for i, buyer_row in buyers_subset.iterrows():
            logging.info(f'Processing buyer {i+1}/{len(buyers_subset)} in location {state_city}')
            buyer_embedding = model.encode(buyer_row['combined_text'], convert_to_tensor=True)
            
            # Compute cosine similarity between buyer and all sellers in this state_city
            similarity_scores = cosine_similarity(buyer_embedding.cpu().numpy().reshape(1, -1), sellers_embeddings_subset.cpu().numpy())[0]
            
            # Find indices where similarity is above threshold
            matching_sellers_indices = np.where(similarity_scores >= similarity_threshold)[0]
            
            for idx in matching_sellers_indices:
                seller_row = sellers_subset.iloc[idx]
                similarity = similarity_scores[idx]
                # Store the match
                match = {
                    'buyer_title': buyer_row['title'],
                    'buyer_summary': buyer_row['description'],
                    'buyer_long_description': buyer_row['long_description'],
                    'seller_title': seller_row['title'],
                    'seller_summary': seller_row['description'],
                    'seller_long_description': seller_row['long_description'],
                    # 'similarity': similarity  # Optional
                }
                matches.append(match)
    
    # Create DataFrame from matches
    matches_df = pd.DataFrame(matches)
    
    # Save to CSV
    logging.info('Saving valid matches to CSV...', len(matches_df))
    matches_df.to_csv('./matches/valid_matches.csv', index=False)
    logging.info('Done.')

if __name__ == '__main__':
    main()
