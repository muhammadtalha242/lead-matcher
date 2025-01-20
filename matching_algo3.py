# 'deepset/gbert-base'    

import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import BallTree
import logging
from geopy.distance import geodesic
import re
import nltk
from nltk.corpus import stopwords
from datetime import datetime
from nltk.stem import SnowballStemmer
from joblib import Parallel, delayed
import gc

# Download required NLTK data
nltk.download('stopwords')
nltk.download('punkt')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def preprocess_text(text):
    if pd.isnull(text):
        return ''
    # Lowercase the text
    text = text.lower()
    # Remove URLs, emails, and phone numbers
    text = re.sub(r'http\S+|www.\S+|\S+@\S+|\b\d{10,}\b', '', text)
    # Remove punctuation and special characters
    text = re.sub(r'[^a-zA-ZäöüÄÖÜß\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove stopwords
    stop_words = set(stopwords.words('german'))
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    # Optional: Apply stemming or lemmatization
    stemmer = SnowballStemmer('german')
    tokens = [stemmer.stem(word) for word in tokens]
    # Join tokens back to string
    text = ' '.join(tokens)
    return text

def flatten_df(df, prefix):
    flat_records = []
    for idx, row in df.iterrows():
        latitudes = row['latitude']
        longitudes = row['longitude']
        if isinstance(latitudes, list) and isinstance(longitudes, list):
            for lat, lon in zip(latitudes, longitudes):
                if lat is not None and lon is not None and not pd.isnull(lat) and not pd.isnull(lon):
                    flat_record = row.to_dict()
                    flat_record['latitude'] = lat
                    flat_record['longitude'] = lon
                    flat_records.append(flat_record)
        else:
            # Handle cases where latitude and longitude are single values
            if row['latitude'] is not None and row['longitude'] is not None:
                flat_record = row.to_dict()
                flat_records.append(flat_record)
    return pd.DataFrame(flat_records)

def combine_text_fields(row):
    return ' '.join([
        row.get('title_preprocessed', ''),
        row.get('description_preprocessed', ''),
        row.get('long_description_preprocessed', ''),
        row.get('branchen_preprocessed', '')
    ])

def get_embedding_batch(texts, model, batch_size=64):
    """
    Encode texts in batches to optimize memory usage.
    """
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype('float32')  # Use float32 to save memory

def is_valid_coordinate(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
        else:
            return False
    except:
        return False

def main():
    # Load updated datasets
    logging.info('Loading datasets...')
    buyers_df = pd.read_csv('./data/buyer_dejuna_geocoded_test-.csv')
    sellers_df = pd.read_csv('./data/branche_nexxt_change_sales_listings_nace_geocoded.csv')

    # Parse JSON-encoded latitude and longitude lists
    logging.info('Parsing latitude and longitude...')
    buyers_df['latitude'] = buyers_df['latitude'].apply(lambda x: json.loads(x) if pd.notnull(x) else [])
    buyers_df['longitude'] = buyers_df['longitude'].apply(lambda x: json.loads(x) if pd.notnull(x) else [])

    sellers_df['latitude'] = sellers_df['latitude'].apply(lambda x: json.loads(x) if pd.notnull(x) else [])
    sellers_df['longitude'] = sellers_df['longitude'].apply(lambda x: json.loads(x) if pd.notnull(x) else [])

    # Preprocess buyers' text fields
    logging.info('Preprocessing buyers\' text fields...')
    buyers_df['title_preprocessed'] = buyers_df['title'].apply(preprocess_text)
    buyers_df['description_preprocessed'] = buyers_df['description'].apply(preprocess_text)
    buyers_df['long_description_preprocessed'] = buyers_df['long_description'].apply(preprocess_text)
    # Handle cases where 'Industrie' or 'Sub-Industrie' might be missing
    buyers_df['branchen_preprocessed'] = buyers_df.apply(
        lambda row: (preprocess_text(row['Industrie']) + " " + preprocess_text(row['Sub-Industrie']))
                    if 'Industrie' in row and 'Sub-Industrie' in row else preprocess_text(row.get('branchen', '')),
        axis=1
    )

    # Preprocess sellers' text fields
    logging.info('Preprocessing sellers\' text fields...')
    sellers_df['title_preprocessed'] = sellers_df['title'].apply(preprocess_text)
    sellers_df['description_preprocessed'] = sellers_df['description'].apply(preprocess_text)
    sellers_df['long_description_preprocessed'] = sellers_df['long_description'].apply(preprocess_text)
    sellers_df['branchen_preprocessed'] = sellers_df['branchen'].apply(preprocess_text)

    # Combine text fields
    logging.info('Combining text fields...')
    buyers_df['combined_text'] = buyers_df.apply(combine_text_fields, axis=1)
    sellers_df['combined_text'] = sellers_df.apply(combine_text_fields, axis=1)

    # Flatten buyers and sellers dataframes
    logging.info('Flattening buyers dataframe...')
    buyers_flat = flatten_df(buyers_df, 'buyer')
    logging.info(f'Flattened buyers dataframe: {len(buyers_flat)} records.')

    logging.info('Flattening sellers dataframe...')
    sellers_flat = flatten_df(sellers_df, 'seller')
    logging.info(f'Flattened sellers dataframe: {len(sellers_flat)} records.')

    # Filter out invalid coordinates
    logging.info('Filtering out invalid coordinates...')
    buyers_flat = buyers_flat[buyers_flat.apply(lambda x: is_valid_coordinate(x['latitude'], x['longitude']), axis=1)]
    sellers_flat = sellers_flat[sellers_flat.apply(lambda x: is_valid_coordinate(x['latitude'], x['longitude']), axis=1)]

    # Initialize the models
    logging.info('Loading the Sentence Transformer models...')
    model_names = [
        # 'paraphrase-multilingual-MiniLM-L12-v2' #427 matches
        "paraphrase-multilingual-mpnet-base-v2"
    ]
    models = {}
    for name in model_names:
        try:
            logging.info(f"Loading model: {name}")
            model = SentenceTransformer(name)
            models[name] = model
        except Exception as e:
            logging.error(f"Error loading model {name}: {e}")

    # Encode sellers' combined_text with each model and store in separate arrays
    seller_embeddings = {}
    logging.info('Encoding sellers\' text with each model...')
    for name, model in models.items():
        logging.info(f"Encoding sellers with model: {name}")
        embeddings = get_embedding_batch(sellers_flat['combined_text'].tolist(), model, batch_size=64)
        seller_embeddings[name] = embeddings
        gc.collect()

    # Prepare seller coordinates for BallTree (in radians)
    logging.info('Preparing BallTree for geographic queries...')
    seller_coords = np.radians(sellers_flat[['latitude', 'longitude']].astype(float).values)
    ball_tree = BallTree(seller_coords, metric='haversine')

    similarity_threshold = 0.91

    matches = []

    earth_radius = 6371.0
    radius_km = 50.0
    radius_rad = radius_km / earth_radius

    total_buyers = len(buyers_flat)
    logging.info('Starting matching process...')
    for i, buyer_row in buyers_flat.iterrows():
        if not is_valid_coordinate(buyer_row['latitude'], buyer_row['longitude']):
            continue

        buyer_coord = np.radians([float(buyer_row['latitude']), float(buyer_row['longitude'])]).reshape(1, -1)
        buyer_open_to_foreign = False

        if buyer_open_to_foreign:
            current_radius_rad = np.pi
        else:
            current_radius_rad = radius_rad

        indices = ball_tree.query_radius(buyer_coord, r=current_radius_rad)[0]

        if len(indices) == 0:
            continue

        model_matches = {name: [] for name in models.keys()}

        buyer_embeddings = {}
        for name, model in models.items():
            buyer_embedding = model.encode(buyer_row['combined_text'], convert_to_numpy=True, normalize_embeddings=True)
            buyer_embeddings[name] = buyer_embedding.astype('float32').reshape(1, -1)

        for name in models.keys():
            seller_emb = seller_embeddings[name][indices]
            sim_scores = cosine_similarity(buyer_embeddings[name], seller_emb)[0]
            matching_indices = np.where(sim_scores >= similarity_threshold)[0]
            model_matches[name] = matching_indices

        all_matched_indices = set()
        for name, indices_model in model_matches.items():
            all_matched_indices.update(indices_model)

        for seller_idx in all_matched_indices:
            seller_real_idx = indices[seller_idx]
            seller_row = sellers_flat.iloc[seller_real_idx]

            distance = geodesic(
                (float(buyer_row['latitude']), float(buyer_row['longitude'])),
                (float(seller_row['latitude']), float(seller_row['longitude']))
            ).kilometers

            seller_open_to_foreign = False

            matched_models = []
            for name in models.keys():
                if seller_idx in model_matches[name]:
                    matched_models.append(name)

            model_match_dict = {}
            for name in models.keys():
                model_match_dict[name] = 'Yes' if seller_idx in model_matches[name] else 'No'

            match = {
                'buyer_date': buyer_row.get('date', ''),
                'buyer_title': buyer_row.get('title', ''),
                'buyer_summary': buyer_row.get('description', ''),
                'buyer_long_description': buyer_row.get('long_description', ''),
                'buyer_location': buyer_row.get('location', ''),
                'buyer_latitude': buyer_row['latitude'],
                'buyer_longitude': buyer_row['longitude'],
                'buyer_open_to_foreign': buyer_open_to_foreign,
                'buyer_nace_code': buyer_row.get('nace_code', ''),
                'seller_date': seller_row.get('date', ''),
                'seller_title': seller_row.get('title', ''),
                'seller_summary': seller_row.get('description', ''),
                'seller_long_description': seller_row.get('long_description', ''),
                'seller_location': seller_row.get('location', ''),
                'seller_latitude': seller_row['latitude'],
                'seller_longitude': seller_row['longitude'],
                'seller_open_to_foreign': seller_open_to_foreign,
                'seller_url': seller_row.get('url', ''),
                'seller_nace_code': seller_row.get('nace_code', ''),
                'distance_km': distance
            }

            for name in models.keys():
                match[f'match_{name}'] = model_match_dict[name]

            matches.append(match)

        if (i + 1) % 50 == 0:
            logging.info(f"Processed {i + 1}/{total_buyers} buyers.")

        del buyer_embeddings
        gc.collect()

    logging.info('Creating matches DataFrame...')
    matches_df = pd.DataFrame(matches)

    if not matches_df.empty:
        model_columns = [f'match_{name}' for name in models.keys()]
        other_columns = [col for col in matches_df.columns if col not in model_columns]
        matches_df = matches_df[other_columns + model_columns]

        timestamp = datetime.now().strftime("%d_%H-%M")
        output_path = f'./matches/nlp_business_matches_{timestamp}_similarity_threshold_{similarity_threshold}.csv'
        matches_df.to_csv(output_path, index=False)
        logging.info(f'Done=> length:: {len(matches_df)} filename=> {output_path}')
    else:
        logging.info('No matches found.')

    del seller_embeddings
    del sellers_flat
    del buyers_flat
    gc.collect()

if __name__ == '__main__':
    main()
