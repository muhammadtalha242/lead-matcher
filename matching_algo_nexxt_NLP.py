import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("matching_log.log"), logging.StreamHandler(sys.stdout)]
)

# Define file paths (update these to your local file paths)
purchase_file_path = './data/nexxt_change_purchase_listings.csv'
sales_file_path = './data/nexxt_change_sales_listings.csv'

# Load the data with error handling
try:
    purchase_df = pd.read_csv(purchase_file_path)
    sales_df = pd.read_csv(sales_file_path)
    logging.info("Files loaded successfully.")
except Exception as e:
    logging.error(f"Error loading files: {e}")
    sys.exit(1)

# Preprocess and handle missing values
for df, name in [(purchase_df, "purchase_df"), (sales_df, "sales_df")]:
    for col in ['description', 'branchen', 'location', 'long_description', 'date']:
        df[col] = df[col].fillna('')  # Fill NaN values with empty strings
    logging.info(f"NaN values in '{name}' handled by filling empty strings.")

# Convert date columns to datetime format
try:
    purchase_df['date'] = pd.to_datetime(purchase_df['date'], errors='coerce', dayfirst=True)
    sales_df['date'] = pd.to_datetime(sales_df['date'], errors='coerce', dayfirst=True)
    logging.info("Date columns converted to datetime.")
except Exception as e:
    logging.error(f"Error parsing dates: {e}")
    sys.exit(1)

# Combine text fields excluding 'branchen' for combined text matching
purchase_df['combined_text'] = (
    purchase_df['location'] + ' ' + 
    purchase_df['description'] + ' ' +
    purchase_df['long_description']
)
sales_df['combined_text'] = (
    sales_df['location'] + ' ' +
    sales_df['description'] + ' ' +
    sales_df['long_description']
)

# Vectorize combined text and branchen fields separately
try:
    combined_text_vectorizer = TfidfVectorizer()
    branchen_vectorizer = TfidfVectorizer()

    purchase_combined_tfidf = combined_text_vectorizer.fit_transform(purchase_df['combined_text'])
    sales_combined_tfidf = combined_text_vectorizer.transform(sales_df['combined_text'])

    purchase_branchen_tfidf = branchen_vectorizer.fit_transform(purchase_df['branchen'])
    sales_branchen_tfidf = branchen_vectorizer.transform(sales_df['branchen'])

    logging.info("Vectorization completed successfully.")
except Exception as e:
    logging.error(f"Error during vectorization: {e}")
    sys.exit(1)

# Compute similarity matrices
combined_text_similarity = cosine_similarity(purchase_combined_tfidf, sales_combined_tfidf)
branchen_similarity = cosine_similarity(purchase_branchen_tfidf, sales_branchen_tfidf)

# Define thresholds
COMBINED_TEXT_THRESHOLD = 0.5
BRANCHEN_THRESHOLD = 0.5

# Find valid matches based on dual thresholds and date validation
matches = []
for i in range(combined_text_similarity.shape[0]):
    for j in range(combined_text_similarity.shape[1]):
        combined_score = combined_text_similarity[i, j]
        branchen_score = branchen_similarity[i, j]
        
        # Get purchase and sale dates
        purchase_date = purchase_df.loc[i, 'date']
        sale_date = sales_df.loc[j, 'date']
        
        # Check if the sale date is earlier than or equal to the purchase date and apply similarity thresholds
        if combined_score > COMBINED_TEXT_THRESHOLD and branchen_score > BRANCHEN_THRESHOLD:
            if pd.notna(purchase_date) and pd.notna(sale_date) and sale_date <= purchase_date:
                match = {
                    "Purchase Date": purchase_date,
                    "Purchase Title": purchase_df.loc[i, "title"],
                    "Purchase Location": purchase_df.loc[i, "location"],
                    "Purchase Industry": purchase_df.loc[i, "branchen"],
                    "Purchase Long Description": purchase_df.loc[i, "long_description"],
                    "Sale Date": sale_date,
                    "Sale Title": sales_df.loc[j, "title"],
                    "Sale Location": sales_df.loc[j, "location"],
                    "Sale Industry": sales_df.loc[j, "branchen"],
                    "Sale Long Description": sales_df.loc[j, "long_description"],
                    "Combined Text Similarity Score": combined_score,
                    "Industry (Branchen) Similarity Score": branchen_score
                }
                matches.append(match)
            else:
                logging.info(f"Invalid match due to date: Purchase Date {purchase_date}, Sale Date {sale_date}")

# Check the number of matches and log
num_matches = len(matches)
logging.info(f"Number of high-quality matches found: {num_matches}")

# Save matches to Excel
try:
    matches_df = pd.DataFrame(matches)
    matches_df.to_excel("./matches/high_quality_matches.xlsx", index=False)
    logging.info("Matches exported successfully to 'high_quality_matches.xlsx'")
except Exception as e:
    logging.error(f"Error exporting to Excel: {e}")
    sys.exit(1)
