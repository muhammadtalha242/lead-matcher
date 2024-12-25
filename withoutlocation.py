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

def analyze_matches(matches_df, buyers_df, sellers_df):
    """Analyze matching results and print key metrics"""
    logging.info("\n=== Matching Analysis ===")
    
    # Basic statistics
    total_buyers = len(buyers_df)
    total_sellers = len(sellers_df)
    total_matches = len(matches_df)
    
    logging.info(f"Total buyers: {total_buyers}")
    logging.info(f"Total sellers: {total_sellers}") 
    logging.info(f"Total matches found: {total_matches}")
    logging.info(f"Average matches per buyer: {total_matches/total_buyers:.2f}")
    
    # Analyze industry matches
    if 'Industrie' in buyers_df.columns and 'branchen' in sellers_df.columns:
        industry_matches = matches_df[matches_df.apply(
            lambda x: any(ind in str(x['seller_summary']).lower() 
                        for ind in str(x['buyer_summary']).lower().split()), axis=1)]
        logging.info(f"Matches with industry overlap: {len(industry_matches)}")

    # Save top matches for manual review
    top_matches = matches_df.head(10)
    top_matches.to_csv('./matches/top_matches_for_review.csv', index=False)
    logging.info("Saved top 10 matches for manual review")
    
    return {
        'total_matches': total_matches,
        'matches_per_buyer': total_matches/total_buyers,
        'buyer_match_rate': len(matches_df['buyer_title'].unique())/total_buyers
    }

def main():
    # Load updated datasets
    logging.info('Loading datasets...')
    buyers_df = pd.read_csv('./data/nexxt_change_purchase_listings_geocoded_nace.csv')
    sellers_df = pd.read_csv('./data/nexxt_change_sales_listings_geocoded_nace.csv')

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
    # buyers_df['branchen_preprocessed'] = buyers_df.apply(
    #     lambda row: (preprocess_text(row['Industrie']) + " " + preprocess_text(row['Sub-Industrie']))
    #                 if 'Industrie' in row and 'Sub-Industrie' in row else preprocess_text(row.get('branchen', '')),
    #     axis=1
    # )
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

    # Flatten buyers and sellers dataframes
    logging.info('Flattening buyers dataframe...')
    # buyers_flat = flatten_df(buyers_df, 'buyer')
    buyers_flat = buyers_df
    logging.info(f'Flattened buyers dataframe: {len(buyers_flat)} records.')

    logging.info('Flattening sellers dataframe...')
    # sellers_flat = flatten_df(sellers_df, 'seller')
    sellers_flat = sellers_df
    logging.info(f'Flattened sellers dataframe: {len(sellers_flat)} records.')

    # Initialize the models with weights - adjust weights to favor the better model
    logging.info('Loading the Sentence Transformer models...')
    model_names = [
        'paraphrase-multilingual-mpnet-base-v2',  # Best for semantic similarity in German
    ]
    
    # Simplified to use single best model instead of ensemble
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
        # Batch encode to optimize memory usage
        embeddings = get_embedding_batch(sellers_flat['combined_text'].tolist(), model, batch_size=64)
        seller_embeddings[name] = embeddings  # Shape: (num_sellers, embedding_dim)
        # Optionally, delete the combined_text column to save memory
        # del sellers_flat['combined_text'] 
        gc.collect()

    # Set even stricter similarity threshold
    similarity_threshold = 0.95  # Increased from 0.92
    
    # Additional filtering based on combined text length
    min_text_length = 50  # Filter out matches with very short descriptions
    
    # Initialize matches list with additional filtering
    matches = []
    confidence_scores = []  # Add this line to store confidence scores

    total_buyers = len(buyers_flat)
    logging.info('Starting matching process...')
    for i, buyer_row in buyers_flat.iterrows():
        # Skip entries with insufficient text
        if len(buyer_row['combined_text']) < min_text_length:
            continue

        # Initialize a dictionary to keep track of matches per model
        model_matches = {name: [] for name in models.keys()}

        # Encode buyer's combined_text with each model
        buyer_embeddings = {}
        for name, model in models.items():
            buyer_embedding = model.encode(buyer_row['combined_text'], convert_to_numpy=True, normalize_embeddings=True)
            buyer_embeddings[name] = buyer_embedding.astype('float32').reshape(1, -1)  # Shape: (1, embedding_dim)

        # Compute weighted average similarity scores across models
        final_sim_scores = np.zeros(len(sellers_flat))
        for name in models.keys():
            sim_scores = cosine_similarity(buyer_embeddings[name], seller_embeddings[name])[0]
            final_sim_scores += sim_scores

        # Find matches using combined score
        matching_indices = np.where(final_sim_scores >= similarity_threshold)[0]
        
        # Create a set of all matched seller indices across all models
        all_matched_indices = set(matching_indices)

        # For each matched seller, determine which models matched
        for seller_idx in all_matched_indices:
            seller_row = sellers_flat.iloc[seller_idx]

            # Skip if seller text is too short
            if len(seller_row['combined_text']) < min_text_length:
                continue
                
            # Only keep very high confidence matches
            confidence_score = final_sim_scores[seller_idx]
            if confidence_score < similarity_threshold:
                continue

            # Store confidence score
            confidence_scores.append(confidence_score)  # Add this line

            # Determine which models matched for this seller
            matched_models = []
            for name in models.keys():
                if seller_idx in model_matches[name]:
                    matched_models.append(name)

            # Create a dictionary indicating 'Yes'/'No' per model
            model_match_dict = {}
            for name in models.keys():
                model_match_dict[name] = 'Yes' if seller_idx in model_matches[name] else 'No'

            # Store the match
            match = {
                'buyer_date': buyer_row.get('date', ''),
                'buyer_title': buyer_row.get('title', ''),
                'buyer_summary': buyer_row.get('description', ''),
                'buyer_long_description': buyer_row.get('long_description', ''),
                'buyer_location': buyer_row.get('location', ''),
                'buyer_latitude': buyer_row['latitude'],
                'buyer_longitude': buyer_row['longitude'],
                'seller_date': seller_row.get('date', ''),
                'seller_title': seller_row.get('title', ''),
                'seller_summary': seller_row.get('description', ''),
                'seller_long_description': seller_row.get('long_description', ''),
                'seller_location': seller_row.get('location', ''),
                'seller_latitude': seller_row['latitude'],
                'seller_longitude': seller_row['longitude'],
                'seller_url': seller_row.get('url', ''),
                'buyer_nace_code': buyer_row.get('assigned_nace_code', ''),
                'seller_nace_code': seller_row.get('nace_code', ''),
                'nace_code_match': 'Yes' if buyer_row.get('assigned_nace_code', '') == seller_row.get('nace_code', '') else 'No'
            }

            # Add model match indicators
            for name in models.keys():
                match[f'match_{name}'] = model_match_dict[name]

            matches.append(match)

        # Log progress every 50 buyers
        if (i + 1) % 50 == 0:
            logging.info(f"Processed {i + 1}/{total_buyers} buyers.")

        # Clear buyer_embeddings to free memory
        del buyer_embeddings
        gc.collect()

    # Create DataFrame from matches
    logging.info('Creating matches DataFrame...')
    matches_df = pd.DataFrame(matches)

    if not matches_df.empty:
        # Analyze results
        metrics = analyze_matches(matches_df, buyers_df, sellers_df)
        
        # Add confidence scores
        matches_df['confidence_score'] = confidence_scores  # Modified this line
        
        # Sort by confidence score
        matches_df = matches_df.sort_values('confidence_score', ascending=False)
        
        # Save only high confidence matches
        high_conf_matches = matches_df[matches_df['confidence_score'] >= 0.95]
        timestamp = datetime.now().strftime("%d_%H-%M")
        output_path = f'./matches/high_confidence_matches_{timestamp}.csv'
        high_conf_matches.to_csv(output_path, index=False)
        logging.info(f'Saved {len(high_conf_matches)} high confidence matches')
        
        # Reorder columns to have model match indicators at the end
        model_columns = [f'match_{name}' for name in models.keys()]
        other_columns = [col for col in matches_df.columns if col not in model_columns]
        matches_df = matches_df[other_columns + model_columns]

        # Save the matches to a CSV file
        timestamp = datetime.now().strftime("%d_%H-%M")
        output_path = f'./matches/nlp_business_matches_{timestamp}_similarity_threshold_{similarity_threshold}.csv'
        matches_df.to_csv(output_path, index=False)
        logging.info(f'Done=> length:: {len(matches_df)} filename=> {output_path}')
    else:
        logging.info('No matches found.')

    # Clean up to free memory
    del seller_embeddings
    del sellers_flat
    del buyers_flat
    gc.collect()

if __name__ == '__main__':
    main()
