import pandas as pd
import numpy as np
import logging
import nltk
from nltk.corpus import stopwords
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import gc
import re

# Ensure NLTK data is available (stopwords, punkt, etc.)
nltk.download('stopwords')
nltk.download('punkt')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

###############################################################################
# 1. HELPER FUNCTIONS
###############################################################################

def combine_buyer_text_fields(row):
    """
    Combines relevant text columns into one for embedding:
      - title
      - description
      - long_description
      - preprocessed_branchen
    """
    # Any missing or NaN text becomes empty string
    title = str(row.get('title', '')) or ''
    desc = str(row.get('description', '')) or ''
    long_desc = str(row.get('long_description', '')) or ''
    branchen = str(row.get('preprocessed_branchen', '')) or ''

    # Combine them with spaces
    combined = ' '.join([
        title.strip(),
        desc.strip(),
        long_desc.strip(),
        branchen.strip()
    ])
    return combined.strip()

def combine_seller_text_fields(row):
    """
    Combines relevant text columns into one for embedding:
      - title
      - description
      - long_description
      - preprocessed_branchen
    """
    # Title,Region,Branchen,Anforderungen an den Käufer,Beschreibung des Verkaufsangebots,Detail URL,Latitude,Longitude

    # Any missing or NaN text becomes empty string
    title = str(row.get('Title', '')) or ''
    desc = str(row.get('Anforderungen an den Käufer', '')) or ''
    long_desc = str(row.get('Beschreibung des Verkaufsangebots', '')) or ''
    branchen = str(row.get('preprocessed_branchen', '')) or ''

    # Combine them with spaces
    combined = ' '.join([
        title.strip(),
        desc.strip(),
        long_desc.strip(),
        branchen.strip()
    ])
    return combined.strip()

def get_embedding_batch(texts, model, batch_size=64):
    """
    Encode texts in batches to optimize memory usage.
    - normalize_embeddings=True to use cosine similarity effectively
    """
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embeddings.astype('float32')  # use float32 to save memory

def analyze_matches(matches_df, buyers_df, sellers_df):
    """
    Analyze matching results and print key metrics.
    Saves top 10 matches for manual review.
    """
    logging.info("\n=== Matching Analysis ===")

    total_buyers = len(buyers_df)
    total_sellers = len(sellers_df)
    total_matches = len(matches_df)
    
    logging.info(f"Total buyers: {total_buyers}")
    logging.info(f"Total sellers: {total_sellers}")
    logging.info(f"Total matches found: {total_matches}")
    
    if total_buyers > 0:
        logging.info(f"Average matches per buyer: {total_matches / total_buyers:.2f}")
    else:
        logging.info("No buyers to match against.")

    if not matches_df.empty:
        top_matches = matches_df.head(10)
        top_matches.to_csv('./matches/top_matches_for_review.csv', index=False)
        logging.info("Saved top 10 matches for manual review")

    return {
        'total_matches': total_matches,
        'matches_per_buyer': total_matches / total_buyers if total_buyers else 0,
        'buyer_match_rate': len(matches_df['buyer_title'].unique()) / total_buyers if total_buyers else 0
    }

###############################################################################
# 2. MAIN SCRIPT
###############################################################################

def main():
    # ---------------------------
    # A) LOAD DATA
    # ---------------------------
    logging.info('Loading datasets...')

    # Adjust paths as needed:
    buyers_file = './data/buyer_dejuna_geocoded_test-.csv'                # Buyer data
    sellers_file = './data/dub_listings_geo_nace.csv'    # Seller data

    # Load CSVs (each has the specified columns)
    buyers_df = pd.read_csv(buyers_file)
    sellers_df = pd.read_csv(sellers_file)

    logging.info(f"Buyers loaded: {len(buyers_df)} records")
    logging.info(f"Sellers loaded: {len(sellers_df)} records")

    # ---------------------------
    # B) COMBINE TEXT FIELDS
    # ---------------------------
    logging.info('Combining text fields (title, description, long_description, preprocessed_branchen)...')

    buyers_df['combined_text'] = buyers_df.apply(combine_buyer_text_fields, axis=1)
    sellers_df['combined_text'] = sellers_df.apply(combine_seller_text_fields, axis=1)

    # ---------------------------
    # C) LOAD MODEL
    # ---------------------------
    logging.info('Loading the Sentence Transformer model...')
    model_name = 'paraphrase-multilingual-mpnet-base-v2'
    # model_name = 'all-MiniLM-L6-v2'
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        logging.error(f"Error loading model {model_name}: {e}")
        return

    # ---------------------------
    # D) ENCODE SELLERS
    # ---------------------------
    logging.info("Encoding sellers' text...")
    seller_texts = sellers_df['combined_text'].tolist()
    seller_embeddings = get_embedding_batch(seller_texts, model, batch_size=64)
    logging.info("Sellers' embeddings generated.")

    # ---------------------------
    # E) MATCHING BUYERS -> SELLERS
    # ---------------------------
    similarity_threshold = 0.8 
    min_text_length = 50  # skip if buyer text is too short

    matches = []
    confidence_scores = []

    total_buyers = len(buyers_df)
    logging.info('Starting matching process...')

    for i, buyer_row in buyers_df.iterrows():
        buyer_text = buyer_row['combined_text'] or ''
        
        # (1) Check text length
        # if len(buyer_text) < min_text_length:
        #     continue

        # (2) Buyer NACE
        buyer_nace = buyer_row.get('nace_code', '')
        # if not buyer_nace:
        #     # If there's no assigned NACE for buyer, skip
        #     continue

        # (3) Encode buyer text
        buyer_embedding = model.encode(
            buyer_text,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).reshape(1, -1)

        # (4) Calculate similarity to all sellers
        sim_scores = cosine_similarity(buyer_embedding, seller_embeddings)[0]

        # (5) Indices where sim >= threshold
        matching_indices = np.where(sim_scores >= similarity_threshold)[0]

        for seller_idx in matching_indices:
            seller_row = sellers_df.iloc[seller_idx]

            # # Check text length for seller
            # if len(seller_row['combined_text']) < min_text_length:
            #     continue

            seller_nace = seller_row.get('nace_code', '')

            # (6) Ensure buyer's NACE code matches seller's NACE
            # if buyer_nace != seller_nace:
            #     continue

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
                'buyer_latitude': buyer_row.get('latitude', ''),
                'buyer_longitude': buyer_row.get('longitude', ''),
                'buyer_nace_code': buyer_nace,

                'seller_date': seller_row.get('date', ''),
                'seller_title': seller_row.get('title', ''),
                'seller_description': seller_row.get('description', ''),
                'seller_long_description': seller_row.get('long_description', ''),
                'seller_location': seller_row.get('location', ''),
                'seller_latitude': seller_row.get('latitude', ''),
                'seller_longitude': seller_row.get('longitude', ''),
                'seller_nace_code': seller_nace,
                
                'similarity_score': confidence_score
            }
            matches.append(match)

        # Progress logging every 50 buyers
        if (i + 1) % 50 == 0:
            logging.info(f"Processed {i + 1}/{total_buyers} buyers...")

    logging.info('Creating matches DataFrame...')
    matches_df = pd.DataFrame(matches)

    if not matches_df.empty:
        matches_df['confidence_score'] = confidence_scores

        # Sort by confidence score desc
        matches_df = matches_df.sort_values('confidence_score', ascending=False)

        # Save all matches
        timestamp = datetime.now().strftime("%d_%H-%M")
        output_all = f'./matches/dub_dejuna_nlp_business_all_matches_{timestamp}.csv'
        matches_df.to_csv(output_all, index=False)
        logging.info(f'Saved all matches: {len(matches_df)} records => {output_all}')

        # Analyze results
        analyze_matches(matches_df, buyers_df, sellers_df)

        # Optionally filter for higher confidence
        high_conf_df = matches_df[matches_df['confidence_score'] >= 0.95]
        output_high_conf = f'./matches/nlp_business_high_conf_{timestamp}.csv'
        high_conf_df.to_csv(output_high_conf, index=False)
        logging.info(f'Saved high confidence matches: {len(high_conf_df)} records => {output_high_conf}')
    else:
        logging.info('No matches found.')

    # Cleanup
    del seller_embeddings
    gc.collect()

if __name__ == '__main__':
    main()
