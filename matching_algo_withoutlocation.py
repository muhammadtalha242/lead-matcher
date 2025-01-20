import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime
import gc
import logging
import json
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download required NLTK data (if not already downloaded)
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nlp = spacy.load('de_core_news_md')  # German model

# Define stopwords
stop_words = set(stopwords.words('german'))

def preprocess_text(text):
    # Lowercase
    
    if pd.isnull(text):
        print("🚀 ~ text:", text)
        return ''
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize
    tokens = word_tokenize(text, language='german')
    # Remove stopwords and lemmatize
    tokens = [nlp(token)[0].lemma_ for token in tokens if token not in stop_words]
    return ' '.join(tokens)
# def preprocess_text(text):
#     if pd.isnull(text):
#         return ''
#     text = text.lower()
#     text = re.sub(r'http\S+|www.\S+|\S+@\S+|\b\d{10,}\b', '', text)
#     text = re.sub(r'[^a-zA-ZäöüÄÖÜß\s]', '', text)
#     text = ' '.join(text.split())
#     tokens = nltk.word_tokenize(text, language='german')
#     stop_words = set(stopwords.words('german'))
#     tokens = [t for t in tokens if t not in stop_words]
#     lemmatizer = WordNetLemmatizer()
#     tokens = [lemmatizer.lemmatize(t) for t in tokens]
#     return ' '.join(tokens)

def is_valid_coordinate(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
        return False
    except:
        return False

def flatten_df(df, id_column, consolidate_coordinates=False):
    flat_records = []
    for idx, row in df.iterrows():
        lat_vals = row['latitude']
        lon_vals = row['longitude']
        
        # Ensure lat_vals and lon_vals are lists
        if isinstance(lat_vals, str):
            try:
                lat_vals = json.loads(lat_vals)
            except json.JSONDecodeError:
                logging.warning(f"Invalid latitude format for index {idx}: {lat_vals}")
                lat_vals = []
        
        if isinstance(lon_vals, str):
            try:
                lon_vals = json.loads(lon_vals)
            except json.JSONDecodeError:
                logging.warning(f"Invalid longitude format for index {idx}: {lon_vals}")
                lon_vals = []
        
        # If lat_vals or lon_vals are not lists, convert them to single-element lists
        if not isinstance(lat_vals, list):
            lat_vals = [lat_vals]
        if not isinstance(lon_vals, list):
            lon_vals = [lon_vals]
        
        # Ensure both lists have the same length
        if len(lat_vals) != len(lon_vals):
            logging.warning(f"Mismatch in latitude and longitude list lengths for index {idx}. Skipping this row.")
            continue
        
        if consolidate_coordinates and len(lat_vals) > 1:
            # Option: Use the first coordinate
            lat_vals = [lat_vals[0]]
            lon_vals = [lon_vals[0]]
            logging.info(f"Consolidated coordinates for index {idx} to first entry.")
            # Alternatively, compute centroid
            # avg_lat = np.mean([lat for lat in lat_vals if lat is not None])
            # avg_lon = np.mean([lon for lon in lon_vals if lon is not None])
            # lat_vals = [avg_lat]
            # lon_vals = [avg_lon]
        
        for lat, lon in zip(lat_vals, lon_vals):
            if lat is None or lon is None:
                continue  # Skip if either latitude or longitude is None
            if is_valid_coordinate(lat, lon):
                record = row.to_dict()
                record['latitude'] = lat
                record['longitude'] = lon
                record[id_column] = idx  # Assign unique ID
                flat_records.append(record)
    return pd.DataFrame(flat_records)

def combine_buyer_text(row):
    # Combine buyer text fields: title, description, long_description, Industrie, Sub-Industrie
    industrie = row.get('Industrie', '')
    sub_industrie = row.get('Sub-Industrie', '')
    
    combined = ' '.join([
        row.get('title_preprocessed', ''),
        row.get('description_preprocessed', ''),
        row.get('long_description_preprocessed', ''),
        row.get('industrie_preprocessed', ''),
        row.get('sub_industrie_preprocessed', '')
    ])
    return combined

def combine_seller_text(row):
    # Combine seller text fields: title, description, long_description, branchen
    return ' '.join([
        row.get('title_preprocessed', ''),
        row.get('description_preprocessed', ''),
        row.get('long_description_preprocessed', ''),
        row.get('branchen_preprocessed', '')
    ])

def get_embedding_batch(texts, model, batch_size=64):
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype('float32')  # Use float32 to save memory

def main():
    # Paths to your pre-merged datasets (after pre-storing coordinates)
    # Assume you have buyers_with_coords.csv & sellers_with_coords.csv with updated columns

    logging.info('Loading datasets...')
    buyers_df = pd.read_csv('./data/buyer_dejuna_geocoded.csv')
    sellers_df = pd.read_csv('./data/nexxt_change_sales_listings_geocoded_short.csv')

    # Assign unique IDs if not present
    if 'buyer_id' not in buyers_df.columns:
        buyers_df['buyer_id'] = buyers_df.index
    if 'seller_id' not in sellers_df.columns:
        sellers_df['seller_id'] = sellers_df.index

    # Preprocess text fields for buyers
    logging.info("Preprocessing buyer text fields...")
    buyers_df['title_preprocessed'] = buyers_df['title'].apply(preprocess_text)
    buyers_df['description_preprocessed'] = buyers_df['description'].apply(preprocess_text)
    buyers_df['long_description_preprocessed'] = buyers_df['long_description'].apply(preprocess_text)
    buyers_df['industrie_preprocessed'] = buyers_df['Industrie'].apply(preprocess_text) if 'Industrie' in buyers_df.columns else ''
    buyers_df['sub_industrie_preprocessed'] = buyers_df['Sub-Industrie'].apply(preprocess_text) if 'Sub-Industrie' in buyers_df.columns else ''

    # Preprocess text fields for sellers
    logging.info("Preprocessing seller text fields...")
    sellers_df['title_preprocessed'] = sellers_df['title'].apply(preprocess_text)
    sellers_df['description_preprocessed'] = sellers_df['description'].apply(preprocess_text)
    sellers_df['long_description_preprocessed'] = sellers_df['long_description'].apply(preprocess_text)
    sellers_df['branchen_preprocessed'] = sellers_df['branchen'].apply(preprocess_text) if 'branchen' in sellers_df.columns else ''

    # Combine text fields
    logging.info("Combining text fields for buyers and sellers...")
    buyers_df['combined_text'] = buyers_df.apply(combine_buyer_text, axis=1)
    sellers_df['combined_text'] = sellers_df.apply(combine_seller_text, axis=1)

    # Flatten DataFrames with coordinate consolidation
    logging.info("Flattening DataFrames with coordinate consolidation...")
    # buyers_flat = flatten_df(buyers_df, 'buyer_id', consolidate_coordinates=True)
    # sellers_flat = flatten_df(sellers_df, 'seller_id', consolidate_coordinates=True)
    buyers_flat = buyers_df
    sellers_flat = sellers_df
    logging.info(f"Flattened buyers: {len(buyers_flat)} rows")
    logging.info(f"Flattened sellers: {len(sellers_flat)} rows")

    # Load the SentenceTransformer model (German-specific)
    # model_name = 'bert-base-german-cased'  # Updated to a valid German-specific model
    # model_name = 'all-mpnet-base-v2'  # Updated to a valid German-specific model
    # Initialize both models
    model_mpnet = SentenceTransformer('all-mpnet-base-v2')
    model_bert = SentenceTransformer('bert-base-german-cased')
    # logging.info(f"Loading model: {model_name}")
    # try:
    #     model = SentenceTransformer(model_name)
    # except Exception as e:
    #     logging.error(f"Error loading model {model_name}: {e}")
    #     return

    # # Generate embeddings
    # logging.info("Generating embeddings for buyers...")
    # buyer_embeddings = get_embedding_batch(buyers_flat['combined_text'].tolist(), model)

    # logging.info("Generating embeddings for sellers...")
    # seller_embeddings = get_embedding_batch(sellers_flat['combined_text'].tolist(), model)

    # Generate embeddings using both models
    logging.info("Generating embeddings for buyers using all-mpnet-base-v2...")
    buyer_embeddings_mpnet = get_embedding_batch(buyers_flat['combined_text'].tolist(), model_mpnet)

    logging.info("Generating embeddings for buyers using bert-base-german-cased...")
    buyer_embeddings_bert = get_embedding_batch(buyers_flat['combined_text'].tolist(), model_bert)

    logging.info("Generating embeddings for sellers using all-mpnet-base-v2...")
    seller_embeddings_mpnet = get_embedding_batch(sellers_flat['combined_text'].tolist(), model_mpnet)

    logging.info("Generating embeddings for sellers using bert-base-german-cased...")
    seller_embeddings_bert = get_embedding_batch(sellers_flat['combined_text'].tolist(), model_bert)

    # Combine embeddings (Method A: Concatenation)
    logging.info("Concatenating buyer embeddings from both models...")
    buyer_embeddings_combined = np.concatenate((buyer_embeddings_mpnet, buyer_embeddings_bert), axis=1)

    logging.info("Concatenating seller embeddings from both models...")
    seller_embeddings_combined = np.concatenate((seller_embeddings_mpnet, seller_embeddings_bert), axis=1)


    # Create BallTree for geographic queries
    # logging.info("Creating BallTree for sellers...")
    # seller_coords = np.radians(sellers_flat[['latitude', 'longitude']].astype(float).values)
    # ball_tree = BallTree(seller_coords, metric='haversine')

    # Optimized Matching Parameters
    similarity_threshold = 0.80     # Increased from 0.8 to 0.85
    # max_matches_per_buyer = 5        # Limit to top 5 matches per buyer
    # search_radius_km = 50.0          # Can be adjusted as needed
    # search_radius_rad = search_radius_km / 6371.0  # Earth's radius in km

    matches = []
    matched_pairs = set()            # To ensure unique buyer-seller pairs

    total_buyers = len(buyers_flat)
    logging.info("Starting the matching process...")
    for i, buyer_row in buyers_flat.iterrows():
        buyer_id = buyer_row['buyer_id']
        # buyer_lat = buyer_row['latitude']
        # buyer_lon = buyer_row['longitude']

        # if not is_valid_coordinate(buyer_lat, buyer_lon):
        #     continue  # Skip invalid buyer coordinates

        # Convert buyer coordinates to radians
        # buyer_coord = np.radians([float(buyer_lat), float(buyer_lon)]).reshape(1, -1)

        # Query BallTree for sellers within the search radius
        # seller_indices = ball_tree.query_radius(buyer_coord, r=search_radius_rad)[0]

        # if len(seller_indices) == 0:
        #     continue  # No sellers within the search radius

        # Extract relevant seller embeddings
        # relevant_seller_embeddings = seller_embeddings_combined[seller_indices]
        relevant_seller_embeddings = seller_embeddings_combined

        # Calculate cosine similarity between buyer and relevant sellers
        similarities = cosine_similarity([buyer_embeddings_combined[i]], relevant_seller_embeddings)[0]

        # Find sellers exceeding the similarity threshold
        matching_sellers = np.where(similarities >= similarity_threshold)[0]

        # If no sellers meet the new threshold, skip
        if len(matching_sellers) == 0:
            continue

        # Sort matching sellers by similarity score in descending order
        sorted_indices = matching_sellers[np.argsort(-similarities[matching_sellers])]

        # Limit the number of matches per buyer
        # sorted_indices = sorted_indices[:max_matches_per_buyer]

        # Initialize count of matches for this buyer
        match_count = 0

        for match_idx in sorted_indices:
            # seller_real_idx = seller_indices[match_idx]
            # seller_real_idx = sellers_df[match_idx]
            seller_id = sellers_flat.iloc[match_idx]['seller_id']

            # Ensure unique buyer-seller pair
            pair_key = (buyer_id, seller_id)
            if pair_key in matched_pairs:
                continue  # Skip duplicate pair
            matched_pairs.add(pair_key)

            seller_row = sellers_flat.iloc[match_idx]

            # # Calculate actual distance
            # distance = geodesic(
            #     (float(buyer_lat), float(buyer_lon)),
            #     (float(seller_row['latitude']), float(seller_row['longitude']))
            # ).kilometers

            # Check industry match
            # Buyer industries: from industrie_preprocessed and sub_industrie_preprocessed
            # buyer_industries = (buyer_row.get('industrie_preprocessed', '') + ' ' + 
            #                     buyer_row.get('sub_industrie_preprocessed', '')).strip()
            # seller_industries = seller_row.get('branchen_preprocessed', '')

            # if buyer_industries and seller_industries:
            #     buyer_ind_set = set(buyer_industries.split())
            #     seller_ind_set = set(seller_industries.split())
            #     industries_overlap = buyer_ind_set.intersection(seller_ind_set)
            #     if not industries_overlap:
            #         continue  # No industry match
            # If one of the industries is missing, consider it a match

            # Optional: Compute composite score (similarity + inverse distance)
            weight_similarity = 0.7
            weight_distance = 0.3
            # normalized_distance = 1 - (distance / search_radius_km)  # Closer distances have higher normalized values
            # composite_score = (weight_similarity * similarities[match_idx]) + (weight_distance * normalized_distance)

            # Create the match entry
            match = {
                'buyer_date': buyer_row.get('date', ''),
                'buyer_location': buyer_row.get('location', ''),
                'buyer_title': buyer_row.get('title', ''),
                'buyer_description': buyer_row.get('description', ''),
                'buyer_long_description': buyer_row.get('long_description', ''),
                'buyer_source': buyer_row.get('source', ''),
                'buyer_contact_details': buyer_row.get('contact details', ''),
                'buyer_Industrie': buyer_row.get('Industrie', ''),
                'buyer_Sub-Industrie': buyer_row.get('Sub-Industrie', ''),

                'seller_date': seller_row.get('date', ''),
                'seller_title': seller_row.get('title', ''),
                'seller_description': seller_row.get('description', ''),
                'seller_long_description': seller_row.get('long_description', ''),
                'seller_location': seller_row.get('location', ''),
                'seller_url': seller_row.get('url', ''),
                'seller_standort': seller_row.get('standort', ''),
                'seller_branchen': seller_row.get('branchen', ''),
                'seller_mitarbeiter': seller_row.get('mitarbeiter', ''),
                'seller_jahresumsatz': seller_row.get('jahresumsatz', ''),
                'seller_preisvorstellung': seller_row.get('preisvorstellung', ''),
                'seller_international': seller_row.get('international', ''),
                # 'distance_km': distance,
                'similarity_score': similarities[match_idx],
                # 'composite_score': composite_score
            }

            matches.append(match)
            match_count += 1

            # if match_count >= max_matches_per_buyer:
            #     break  # Reached the maximum number of matches for this buyer

        # Log progress every 100 buyers
        if (i + 1) % 100 == 0:
            logging.info(f"Processed {i+1}/{total_buyers} buyers, {len(matches)} total matches so far.")

        # Memory cleanup every 1000 buyers
        if (i + 1) % 1000 == 0:
            gc.collect()

    logging.info("Creating matches DataFrame...")
    matches_df = pd.DataFrame(matches)

    if not matches_df.empty:
        # Select and order the required columns
        required_columns = [
            'buyer_date',
            'buyer_location',
            'buyer_title',
            'buyer_description',
            'buyer_long_description',
            'buyer_source',
            'buyer_contact_details',
            'buyer_Industrie',
            'buyer_Sub-Industrie',
            'seller_date',
            'seller_title',
            'seller_description',
            'seller_long_description',
            'seller_location',
            'seller_url',
            'seller_standort',
            'seller_branchen',
            'seller_mitarbeiter',
            'seller_jahresumsatz',
            'seller_preisvorstellung',
            'seller_international',
            # 'distance_km',
            'similarity_score',
            # 'composite_score'
        ]
        # Ensure all required columns are present
        for col in required_columns:
            if col not in matches_df.columns:
                matches_df[col] = ''

        matches_df = matches_df[required_columns]

        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f'./matches/matches_{timestamp}.csv'
        matches_df.to_csv(output_path, index=False, encoding='utf-8')
        logging.info(f"Completed. {len(matches_df)} matches saved to {output_path}.")
    else:
        logging.info("No valid matches found.")

    # Final memory cleanup
    del buyer_embeddings_combined, seller_embeddings_combined, buyers_flat, sellers_flat
    gc.collect()

if __name__ == '__main__':
    main()
