import pandas as pd
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to load CSV files
def load_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except pd.errors.EmptyDataError:
        logging.error(f"File is empty: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error while loading {file_path}: {e}")
        return None

# Preprocess text function
def preprocess_text(text):
    if pd.isna(text):
        return ""
    return text.lower().replace("\n", " ").strip()

# Strict industry matching using cosine similarity
def strict_match_industry(lead_industry, listing_industry):
    if not lead_industry or not listing_industry:
        return False
    
    # Convert the industries to vectors and calculate similarity
    vectorizer = CountVectorizer().fit_transform([lead_industry, listing_industry])
    vectors = vectorizer.toarray()
    similarity = cosine_similarity(vectors)
    return similarity[0, 1] > 0.6  # Only consider matches with high similarity

# Location matching function
def match_location(lead_location, listing_location):
    lead_parts = set([part.strip() for part in lead_location.split('>')])
    listing_parts = set([part.strip() for part in listing_location.split('>')])
    return len(lead_parts.intersection(listing_parts)) > 0

# Main matching function
def match_leads_to_listings(leads_df, listings_df):
    # Preprocess data
    leads_df['processed_location'] = leads_df['location'].apply(preprocess_text)
    leads_df['processed_industry'] = leads_df['Industrie'].apply(preprocess_text)
    listings_df['processed_location'] = listings_df['standort'].apply(preprocess_text)
    listings_df['processed_industry'] = listings_df['branchen'].apply(preprocess_text)

    # Combine title and long_description for similarity calculation
    leads_df['combined_text'] = leads_df['title'] + " " + leads_df['long_description']
    listings_df['combined_text'] = listings_df['title'] + " " + listings_df['long_description']

    # Compute TF-IDF vectors
    logging.info("Computing TF-IDF vectors for text data.")
    try:
        tfidf_vectorizer = TfidfVectorizer(stop_words=None, max_features=5000)
        leads_tfidf = tfidf_vectorizer.fit_transform(leads_df['combined_text'].fillna(''))
        listings_tfidf = tfidf_vectorizer.transform(listings_df['combined_text'].fillna(''))
    except Exception as e:
        logging.error(f"Error computing TF-IDF vectors: {e}")
        return None

    # Match leads to listings
    matches = []
    for i, lead in leads_df.iterrows():
        best_match = None
        best_match_score = 0

        for j, listing in listings_df.iterrows():
            # Check for strict industry match and location match
            if not strict_match_industry(lead['processed_industry'], listing['processed_industry']):
                continue
            if not match_location(lead['processed_location'], listing['processed_location']):
                continue

            # Compute similarity score using cosine similarity
            try:
                similarity_score = cosine_similarity(leads_tfidf[i], listings_tfidf[j])[0, 0]
            except Exception as e:
                logging.warning(f"Error computing similarity for lead {i} and listing {j}: {e}")
                continue

            if similarity_score > best_match_score:
                best_match = listing
                best_match_score = similarity_score

        if best_match is not None:
            matches.append({
                'lead_title': lead['title'],
                'lead_location': lead['location'],
                'matched_listing_title': best_match['title'],
                'matched_listing_location': best_match['standort'],
                'similarity_score': best_match_score
            })

    return pd.DataFrame(matches)

if __name__ == "__main__":
    # Load data
    leads_file_path = "./data/buyer_dejuna.csv"
    listings_file_path = "./data/nexxt_change_sales_listings_20241101_005703.csv"
    
    leads_df = load_csv(leads_file_path)
    listings_df = load_csv(listings_file_path)
    
    if leads_df is not None and listings_df is not None:
        # Perform matching
        logging.info("Starting lead to listing matching process.")
        matches_df = match_leads_to_listings(leads_df, listings_df)
        
        if matches_df is not None and not matches_df.empty:
            # Save matches to a CSV file
            output_file_path = "./matches/lead_listing_matches.csv"
            matches_df.to_csv(output_file_path, index=False)
            logging.info(f"Matching process completed. Results saved to {output_file_path}")
        else:
            logging.info("No matches found.")
    else:
        logging.error("Unable to load input data. Exiting.")
