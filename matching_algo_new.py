import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import faiss
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime
import gc
import logging
import json
import spacy

# -------------------------------
# Setup Logging
# -------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------------------------
# Download required NLTK data (if not already downloaded)
# -------------------------------
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# -------------------------------
# Load Spacy model for NER (German)
# -------------------------------
try:
    nlp = spacy.load("de_core_news_sm")
except OSError:
    logging.info("Downloading 'de_core_news_sm' model for SpaCy as it was not found.")
    from spacy.cli import download
    download("de_core_news_sm")
    nlp = spacy.load("de_core_news_sm")

# -------------------------------
# Preprocessing Functions
# -------------------------------
def preprocess_text(text):
    if pd.isnull(text):
        return ''
    text = text.lower()
    # Retain essential characters (&, /) and remove URLs, emails, and long numbers
    text = re.sub(r'http\S+|www\.\S+|\S+@\S+|\b\d{10,}\b', '', text)
    text = re.sub(r'[^a-zA-ZäöüÄÖÜß\s&/]', '', text)
    text = ' '.join(text.split())
    tokens = nltk.word_tokenize(text, language='german')
    stop_words = set(stopwords.words('german'))
    tokens = [t for t in tokens if t not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return ' '.join(tokens)

def extract_entities(text):
    if not text:
        return ''
    doc = nlp(text)
    return ' '.join([ent.text for ent in doc.ents])

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
    combined = ' '.join([
        row.get('title_preprocessed', ''),
        row.get('description_preprocessed', ''),
        row.get('long_description_preprocessed', ''),
        row.get('industrie_preprocessed', ''),
        row.get('sub_industrie_preprocessed', ''),
        row.get('entities', '')
    ])
    return combined

def combine_seller_text(row):
    # Combine seller text fields: title, description, long_description, branchen
    combined = ' '.join([
        row.get('title_preprocessed', ''),
        row.get('description_preprocessed', ''),
        row.get('long_description_preprocessed', ''),
        row.get('branchen_preprocessed', ''),
        row.get('entities', '')
    ])
    return combined

def get_embedding_batch(texts, model, batch_size=64):
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype('float32')  # Use float32 to save memory

# -------------------------------
# Industry Mapping Function (Optional)
# -------------------------------
def map_to_standard_industry(industry_text):
    # Implement a mapping from industry text to standardized codes (e.g., NACE)
    # This is a placeholder function. You need to define actual mappings based on your data.
    # Example:
    industry_mapping = {
        'elektroinstallation': 'NACE Code 43.22',
        'schreinerei': 'NACE Code 16.23',
        'transport und logistik': 'NACE Code 52',
        'physiotherapie': 'NACE Code 86.90',
        # Add more mappings as needed
    }
    words = industry_text.split()
    for word in words:
        if word in industry_mapping:
            return industry_mapping[word]
    return 'Unknown'

# -------------------------------
# Main Matching Function
# -------------------------------
def main():
    # Paths to your pre-merged datasets (after pre-storing coordinates)
    # Ensure your CSV files have the necessary columns as referenced in the script
    buyers_path = './data/buyer_dejuna_geocoded.csv'
    sellers_path = './data/nexxt_change_sales_listings_geocoded.csv'
    
    logging.info('Loading datasets...')
    buyers_df = pd.read_csv(buyers_path)
    sellers_df = pd.read_csv(sellers_path)

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
    buyers_df['entities'] = buyers_df['combined_text'] = buyers_df.apply(lambda row: extract_entities(row['combined_text'] if 'combined_text' in row else ''), axis=1)

    # Preprocess text fields for sellers
    logging.info("Preprocessing seller text fields...")
    sellers_df['title_preprocessed'] = sellers_df['title'].apply(preprocess_text)
    sellers_df['description_preprocessed'] = sellers_df['description'].apply(preprocess_text)
    sellers_df['long_description_preprocessed'] = sellers_df['long_description'].apply(preprocess_text)
    sellers_df['branchen_preprocessed'] = sellers_df['branchen'].apply(preprocess_text) if 'branchen' in sellers_df.columns else ''
    sellers_df['entities'] = sellers_df['combined_text'] = sellers_df.apply(lambda row: extract_entities(row['combined_text'] if 'combined_text' in row else ''), axis=1)

    # Combine text fields
    logging.info("Combining text fields for buyers and sellers...")
    buyers_df['combined_text'] = buyers_df.apply(combine_buyer_text, axis=1)
    sellers_df['combined_text'] = sellers_df.apply(combine_seller_text, axis=1)

    # Optional: Map industries to standardized codes
    logging.info("Mapping industries to standardized codes (if applicable)...")
    buyers_df['standard_industry'] = buyers_df['industrie_preprocessed'].apply(map_to_standard_industry)
    sellers_df['standard_industry'] = sellers_df['branchen_preprocessed'].apply(map_to_standard_industry)

    # Flatten DataFrames with coordinate consolidation
    logging.info("Flattening DataFrames with coordinate consolidation...")
    buyers_flat = flatten_df(buyers_df, 'buyer_id', consolidate_coordinates=True)
    sellers_flat = flatten_df(sellers_df, 'seller_id', consolidate_coordinates=True)
    logging.info(f"Flattened buyers: {len(buyers_flat)} rows")
    logging.info(f"Flattened sellers: {len(sellers_flat)} rows")

    # Load the SentenceTransformer model (German-specific)
    # Choosing a single, efficient, and powerful German-specific model
    # Example: 'distilbert-base-german-cased'
    model_name = 'distilbert-base-german-cased'
    logging.info(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)

    # Generate embeddings
    logging.info("Generating embeddings for buyers...")
    buyer_embeddings = get_embedding_batch(buyers_flat['combined_text'].tolist(), model)

    logging.info("Generating embeddings for sellers...")
    seller_embeddings = get_embedding_batch(sellers_flat['combined_text'].tolist(), model)

    # Optional: Apply PCA for dimensionality reduction (if needed)
    # Here, we skip PCA as it might not be necessary with a single model and manageable embedding size

    # Normalize embeddings (already done via SentenceTransformer's normalize_embeddings=True)
    # buyer_embeddings = normalize(buyer_embeddings, norm='l2')
    # seller_embeddings = normalize(seller_embeddings, norm='l2')

    # Create FAISS index for efficient similarity search
    logging.info("Creating FAISS index for sellers...")
    dimension = buyer_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product is equivalent to cosine similarity since embeddings are normalized
    faiss.normalize_L2(seller_embeddings)  # Ensure normalization
    index.add(seller_embeddings)  # Add seller embeddings to the index

    # Matching Parameters
    similarity_threshold = 0.75     # Adjust as needed
    max_matches_per_buyer = 5        # Limit to top 5 matches per buyer
    search_radius_km = 50.0          # Not directly used with FAISS, but can be incorporated in scoring
    earth_radius_km = 6371.0

    # Prepare geographic data for sellers
    seller_coords = sellers_flat[['latitude', 'longitude']].astype(float).values
    seller_coords_rad = np.radians(seller_coords)

    # Initialize list to store matches
    matches = []
    matched_pairs = set()            # To ensure unique buyer-seller pairs

    total_buyers = len(buyers_flat)
    logging.info("Starting the matching process...")

    batch_size = 1000  # Process in batches to optimize memory and speed
    for start_idx in range(0, total_buyers, batch_size):
        end_idx = min(start_idx + batch_size, total_buyers)
        buyer_batch = buyers_flat.iloc[start_idx:end_idx]
        buyer_embeddings_batch = buyer_embeddings[start_idx:end_idx]

        # Perform FAISS search
        D, I = index.search(buyer_embeddings_batch, max_matches_per_buyer)  # D: similarities, I: indices

        for i, buyer_row in buyer_batch.iterrows():
            buyer_id = buyer_row['buyer_id']
            buyer_lat = buyer_row['latitude']
            buyer_lon = buyer_row['longitude']

            if not is_valid_coordinate(buyer_lat, buyer_lon):
                continue  # Skip invalid buyer coordinates

            buyer_coord = (float(buyer_lat), float(buyer_lon))

            for rank in range(len(I[i])):
                seller_idx = I[i][rank]
                similarity = D[i][rank]

                if similarity < similarity_threshold:
                    continue  # Below similarity threshold

                seller_id = sellers_flat.iloc[seller_idx]['seller_id']

                # Ensure unique buyer-seller pair
                pair_key = (buyer_id, seller_id)
                if pair_key in matched_pairs:
                    continue  # Skip duplicate pair
                matched_pairs.add(pair_key)

                seller_row = sellers_flat.iloc[seller_idx]
                seller_lat = float(seller_row['latitude'])
                seller_lon = float(seller_row['longitude'])
                distance = geodesic(buyer_coord, (seller_lat, seller_lon)).kilometers

                # Optional: Apply search radius constraint
                if distance > search_radius_km:
                    continue  # Skip sellers outside the search radius

                # Industry matching using standardized codes or semantic similarity
                buyer_industry = buyer_row.get('standard_industry', 'Unknown')
                seller_industry = seller_row.get('standard_industry', 'Unknown')

                if buyer_industry != 'Unknown' and seller_industry != 'Unknown':
                    if buyer_industry != seller_industry:
                        continue  # Industries do not match
                # If one of the industries is 'Unknown', consider it a match

                # Composite Score: weighted sum of similarity and inverse distance
                weight_similarity = 0.7
                weight_distance = 0.3
                normalized_distance = 1 - (distance / search_radius_km)  # Closer distances have higher normalized values
                composite_score = (weight_similarity * similarity) + (weight_distance * normalized_distance)

                # Optional: Incorporate additional features like company size and revenue compatibility
                # Example:
                # buyer_size = buyer_row.get('company_size', 0)
                # seller_size = seller_row.get('seller_size', 0)
                # size_diff = abs(buyer_size - seller_size)
                # if size_diff > size_threshold:
                #     continue  # Skip if company sizes are too different

                # Create the match entry
                match = {
                    'buyer_id': buyer_id,
                    'buyer_date': buyer_row.get('date', ''),
                    'buyer_location': buyer_row.get('location', ''),
                    'buyer_title': buyer_row.get('title', ''),
                    'buyer_description': buyer_row.get('description', ''),
                    'buyer_long_description': buyer_row.get('long_description', ''),
                    'buyer_source': buyer_row.get('source', ''),
                    'buyer_contact_details': buyer_row.get('contact_details', ''),
                    'buyer_industrie': buyer_row.get('Industrie', ''),
                    'buyer_sub_industrie': buyer_row.get('Sub-Industrie', ''),
                    'seller_id': seller_id,
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
                    'distance_km': distance,
                    'similarity_score': similarity,
                    'composite_score': composite_score
                }

                matches.append(match)

        # Log progress
        logging.info(f"Processed buyers {start_idx + 1} to {end_idx}/{total_buyers}. Total matches so far: {len(matches)}.")

        # Memory cleanup
        gc.collect()

    # Convert matches to DataFrame
    logging.info("Creating matches DataFrame...")
    matches_df = pd.DataFrame(matches)

    if not matches_df.empty:
        # Select and order the required columns
        required_columns = [
            'buyer_id',
            'buyer_date',
            'buyer_location',
            'buyer_title',
            'buyer_description',
            'buyer_long_description',
            'buyer_source',
            'buyer_contact_details',
            'buyer_industrie',
            'buyer_sub_industrie',
            'seller_id',
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
            'distance_km',
            'similarity_score',
            'composite_score'
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
    del buyer_embeddings, seller_embeddings, buyers_flat, sellers_flat, matches_df
    gc.collect()

if __name__ == '__main__':
    main()
