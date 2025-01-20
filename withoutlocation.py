import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging
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
    # Remove URLs, emails, phone numbers
    text = re.sub(r'http\S+|www.\S+|\S+@\S+|\b\d{10,}\b', '', text)
    # Remove punctuation/special characters
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
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True, 
                              convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype('float32')  # Use float32 to save memory

def analyze_matches(matches_df, buyers_df, sellers_df):
    """Analyze matching results and print key metrics."""
    logging.info("\n=== Matching Analysis ===")
    
    total_buyers = len(buyers_df)
    total_sellers = len(sellers_df)
    total_matches = len(matches_df)
    
    logging.info(f"Total buyers: {total_buyers}")
    logging.info(f"Total sellers: {total_sellers}") 
    logging.info(f"Total matches found: {total_matches}")
    if total_buyers > 0:
        logging.info(f"Average matches per buyer: {total_matches/total_buyers:.2f}")
    else:
        logging.info("No buyers to match against.")

    # Save top matches for manual review
    top_matches = matches_df.head(10)
    top_matches.to_csv('./matches/top_matches_for_review.csv', index=False)
    logging.info("Saved top 10 matches for manual review")
    
    return {
        'total_matches': total_matches,
        'matches_per_buyer': total_matches/total_buyers if total_buyers else 0,
        'buyer_match_rate': len(matches_df['buyer_title'].unique())/total_buyers if total_buyers else 0
    }

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
    buyers_df['branchen_preprocessed'] = buyers_df['branchen'].apply(preprocess_text)

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

    # Flatten if needed (or skip if lat/lon are already handled)
    logging.info('Flattening buyers dataframe...')
    buyers_flat = buyers_df  # or flatten_df(buyers_df, 'buyer')
    logging.info(f'Flattened buyers dataframe: {len(buyers_flat)} records.')

    logging.info('Flattening sellers dataframe...')
    sellers_flat = sellers_df  # or flatten_df(sellers_df, 'seller')
    logging.info(f'Flattened sellers dataframe: {len(sellers_flat)} records.')

    # Load the Sentence Transformer model
    logging.info('Loading the Sentence Transformer model...')
    model_name = 'paraphrase-multilingual-mpnet-base-v2'
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        logging.error(f"Error loading model {model_name}: {e}")
        return

    # Encode sellers' combined_text
    logging.info("Encoding sellers' text...")
    seller_texts = sellers_flat['combined_text'].tolist()
    seller_embeddings = get_embedding_batch(seller_texts, model, batch_size=64)
    logging.info("Sellers' embeddings generated.")

    # Set similarity threshold
    similarity_threshold = 0.95  
    # Optional text length filter
    min_text_length = 50

    matches = []
    confidence_scores = []

    total_buyers = len(buyers_flat)
    logging.info('Starting matching process...')
    for i, buyer_row in buyers_flat.iterrows():
        buyer_text = buyer_row['combined_text']
        
        # Check text length filter
        if len(buyer_text) < min_text_length:
            continue

        # NACE code for buyer
        buyer_nace = buyer_row.get('assigned_nace_code', '')

        # Only proceed if buyer has a valid NACE code
        if not buyer_nace:
            continue

        # Encode buyer text
        buyer_embedding = model.encode(buyer_text, convert_to_numpy=True, normalize_embeddings=True).reshape(1, -1)

        # Calculate similarity scores to all sellers
        sim_scores = cosine_similarity(buyer_embedding, seller_embeddings)[0]

        # Indices above threshold
        matching_indices = np.where(sim_scores >= similarity_threshold)[0]

        for seller_idx in matching_indices:
            seller_row = sellers_flat.iloc[seller_idx]
            
            # Check text length
            if len(seller_row['combined_text']) < min_text_length:
                continue

            # NACE code for seller
            seller_nace = seller_row.get('nace_code', '')

            # =======================
            # NACE CODE MUST MATCH
            # =======================
            if buyer_nace != seller_nace:
                continue  # Skip if NACE codes differ

            confidence_score = sim_scores[seller_idx]
            if confidence_score < similarity_threshold:
                continue

            confidence_scores.append(confidence_score)

            match = {
                'buyer_date': buyer_row.get('date', ''),
                'buyer_title': buyer_row.get('title', ''),
                'buyer_description': buyer_row.get('description', ''),
                'buyer_long_description': buyer_row.get('long_description', ''),
                'buyer_location': buyer_row.get('location', ''),
                'buyer_latitude': buyer_row['latitude'],
                'buyer_longitude': buyer_row['longitude'],
                'buyer_nace_code': buyer_nace,

                'seller_date': seller_row.get('date', ''),
                'seller_title': seller_row.get('title', ''),
                'seller_description': seller_row.get('description', ''),
                'seller_long_description': seller_row.get('long_description', ''),
                'seller_location': seller_row.get('location', ''),
                'seller_latitude': seller_row['latitude'],
                'seller_longitude': seller_row['longitude'],
                'seller_nace_code': seller_nace,
                
                'similarity_score': confidence_score
            }
            matches.append(match)

        # Progress logging
        if (i + 1) % 50 == 0:
            logging.info(f"Processed {i+1}/{total_buyers} buyers.")

    logging.info('Creating matches DataFrame...')
    matches_df = pd.DataFrame(matches)

    if not matches_df.empty:
        matches_df['confidence_score'] = confidence_scores

        # Sort by confidence score
        matches_df = matches_df.sort_values('confidence_score', ascending=False)

        # Save all matches
        timestamp = datetime.now().strftime("%d_%H-%M")
        output_all = f'./matches/nlp_business_all_matches_{timestamp}.csv'
        matches_df.to_csv(output_all, index=False)
        logging.info(f'Saved all matches: {len(matches_df)} records => {output_all}')

        # Analyze results
        metrics = analyze_matches(matches_df, buyers_df, sellers_df)
        
        # Optionally filter for high confidence
        high_conf_df = matches_df[matches_df['confidence_score'] >= 0.95]
        output_high_conf = f'./matches/nlp_business_high_conf_{timestamp}.csv'
        high_conf_df.to_csv(output_high_conf, index=False)
        logging.info(f'Saved high confidence matches: {len(high_conf_df)} records => {output_high_conf}')
    else:
        logging.info('No matches found.')

    # Final memory cleanup
    del seller_embeddings, buyers_flat, sellers_flat
    gc.collect()

if __name__ == '__main__':
    main()
