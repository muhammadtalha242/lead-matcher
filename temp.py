import pandas as pd
import logging
from typing import List, Dict, Set, Tuple
import re
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('wordnet')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BusinessMatcher:
    def __init__(self):
        """Initialize the matcher with necessary components."""
        self.keywords_df = None
        self.buyers_df = None
        self.sellers_df = None
        self.keyword_synonyms = {}
        self.german_states = {
            'baden-württemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
            'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
            'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
            'sachsen-anhalt', 'schleswig-holstein', 'thüringen'
        }
        self.lemmatizer = WordNetLemmatizer()

    def load_data(self, keywords_path: str, buyers_path: str, sellers_path: str) -> None:
        """Load and prepare the data with error handling."""
        try:
            # Load keywords and create enhanced synonym dictionary
            self.keywords_df = pd.read_csv(keywords_path)
            logger.info(f"Successfully loaded keywords from {keywords_path}")
            
            # Validate required columns in keywords
            required_keyword_columns = {'Keyword'}
            if not required_keyword_columns.issubset(self.keywords_df.columns):
                logger.error("Keywords CSV is missing required columns.")
                raise ValueError("Keywords CSV is missing required columns.")
            
            # Create keyword dictionary with synonyms
            for _, row in self.keywords_df.iterrows():
                keyword = row['Keyword']
                if pd.notna(keyword):
                    synonyms = set()
                    synonyms.add(keyword.lower())
                    
                    # Iterate through possible synonym columns
                    for i in range(1, 7):  # Adjusted to handle up to 6 synonyms based on sample data
                        synonym = row.get(f'Synonym {i}', None)
                        if pd.notna(synonym):
                            synonyms.add(synonym.lower())
                    
                    # Assign synonyms to the keyword
                    self.keyword_synonyms[keyword.lower()] = {
                        'synonyms': synonyms,
                        'original': keyword
                    }
            
            # Load and validate buyers data
            self.buyers_df = pd.read_csv(buyers_path)
            required_buyer_columns = {
                'publishing date', 'location (state + city)', 'Titel',
                'summary', 'long description', 'source',
                'contact details', 'Branche'
            }
            if not required_buyer_columns.issubset(self.buyers_df.columns):
                logger.error("Buyer CSV is missing required columns.")
                raise ValueError("Buyer CSV is missing required columns.")
            logger.info(f"Successfully loaded buyer data from {buyers_path}")
            
            # Load and validate sellers data
            self.sellers_df = pd.read_csv(sellers_path)
            required_seller_columns = {
                'date', 'title', 'description', 'location', 'url',
                'long_description', 'standort', 'branchen',
                'mitarbeiter', 'jahresumsatz', 'preisvorstellung', 'international'
            }
            if not required_seller_columns.issubset(self.sellers_df.columns):
                logger.error("Seller CSV is missing required columns.")
                raise ValueError("Seller CSV is missing required columns.")
            logger.info(f"Successfully loaded seller data from {sellers_path}")
            
            # Deduplicate buyers and sellers
            self.deduplicate_dataframes()
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def deduplicate_dataframes(self):
        """Remove duplicate entries from buyers and sellers dataframes based on unique identifiers."""
        initial_buyer_count = len(self.buyers_df)
        self.buyers_df.drop_duplicates(subset=['Titel', 'contact details'], inplace=True)
        logger.info(f"Removed {initial_buyer_count - len(self.buyers_df)} duplicate buyers.")
        
        initial_seller_count = len(self.sellers_df)
        self.sellers_df.drop_duplicates(subset=['title', 'location'], inplace=True)
        logger.info(f"Removed {initial_seller_count - len(self.sellers_df)} duplicate sellers.")

    def preprocess_text(self, text: str) -> List[str]:
        """Tokenize and lemmatize the input text."""
        tokens = word_tokenize(text.lower())
        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def _extract_location_parts(self, location: str) -> Dict[str, Set[str]]:
        """Extract and categorize location parts into states and cities."""
        locations = {
            'states': set(),
            'cities': set()
        }
        
        if pd.isna(location):
            return locations
        
        try:
            # Split on common delimiters and clean up
            parts = re.split(r'[,>\n]\s*', str(location))
            for part in parts:
                part = part.strip().lower()
                if part:
                    # Check if it's a state
                    if part in self.german_states:
                        locations['states'].add(part)
                    else:
                        # Remove "region" and other common prefixes
                        clean_part = re.sub(r'^region\s+', '', part)
                        if clean_part:
                            locations['cities'].add(clean_part)
                    
        except Exception as e:
            logger.error(f"Error extracting location parts: {e}")
            
        return locations

    def _check_location_match(self, buyer_loc: str, seller_loc: str) -> Tuple[bool, Set[str]]:
        """Check if locations match and return matching locations."""
        try:
            buyer_locations = self._extract_location_parts(buyer_loc)
            seller_locations = self._extract_location_parts(seller_loc)
            
            # Check state matches
            matching_states = buyer_locations['states'].intersection(seller_locations['states'])
            
            # Check city matches
            matching_cities = buyer_locations['cities'].intersection(seller_locations['cities'])
            
            # Location matches if either:
            # 1. They have at least one matching state
            # 2. They have at least one matching city
            has_match = bool(matching_states or matching_cities)
            
            # Combine matching locations for reporting
            matching_locations = matching_states.union(matching_cities)
            
            return has_match, matching_locations
                
        except Exception as e:
            logger.error(f"Error checking location match: {e}")
            return False, set()

    def _find_matching_keywords(self, buyer_tokens: Set[str], seller_tokens: Set[str]) -> List[str]:
        """Find matching keywords between two sets of tokens."""
        matching_keywords = []
        
        for keyword, data in self.keyword_synonyms.items():
            if data['synonyms'].intersection(buyer_tokens) and data['synonyms'].intersection(seller_tokens):
                matching_keywords.append(data['original'])
                
        return matching_keywords

    def _check_keyword_match(self, buyer: pd.Series, seller: pd.Series) -> Tuple[bool, List[str]]:
        """Check if there are matching keywords and return them."""
        try:
            # Combine relevant text fields from buyer
            buyer_text = ' '.join(filter(pd.notna, [
                str(buyer.get('Titel', '')),
                str(buyer.get('summary', '')),
                str(buyer.get('long description', ''))
            ])).lower()
            
            # Combine relevant text fields from seller
            seller_text = ' '.join(filter(pd.notna, [
                str(seller.get('title', '')),
                str(seller.get('description', '')),
                str(seller.get('long_description', '')),
                str(seller.get('branchen', ''))
            ])).lower()
            
            # Preprocess texts
            buyer_tokens = set(self.preprocess_text(buyer_text))
            seller_tokens = set(self.preprocess_text(seller_text))
            
            # Find matching keywords
            matching_keywords = self._find_matching_keywords(buyer_tokens, seller_tokens)
            has_match = len(matching_keywords) > 0
            
            return has_match, matching_keywords
                
        except Exception as e:
            logger.error(f"Error checking keyword match: {str(e)}")
            return False, []

    def find_matches(self) -> List[Dict]:
        """Find matches requiring both location and keyword matches."""
        matches = []
        
        try:
            # Preprocess all sellers to improve performance
            preprocessed_sellers = []
            for _, seller in self.sellers_df.iterrows():
                seller_text = ' '.join(filter(pd.notna, [
                    str(seller.get('title', '')),
                    str(seller.get('description', '')),
                    str(seller.get('long_description', '')),
                    str(seller.get('branchen', ''))
                ])).lower()
                seller_tokens = set(self.preprocess_text(seller_text))
                preprocessed_sellers.append({
                    'seller': seller,
                    'tokens': seller_tokens
                })
            
            for _, buyer in self.buyers_df.iterrows():
                # Combine buyer text fields and preprocess
                buyer_text = ' '.join(filter(pd.notna, [
                    str(buyer.get('Titel', '')),
                    str(buyer.get('summary', '')),
                    str(buyer.get('long description', ''))
                ])).lower()
                buyer_tokens = set(self.preprocess_text(buyer_text))
                
                # Extract buyer locations
                buyer_locations = self._extract_location_parts(buyer.get('location (state + city)', ''))
                
                for seller_info in preprocessed_sellers:
                    seller = seller_info['seller']
                    seller_tokens = seller_info['tokens']
                    
                    # Find matching keywords
                    matching_keywords = self._find_matching_keywords(buyer_tokens, seller_tokens)
                    if not matching_keywords:
                        continue  # Skip if no keyword match
                    
                    # Check location match
                    has_location_match, matching_locations = self._check_location_match(
                        buyer.get('location (state + city)', ''),
                        seller.get('location', '')
                    )
                    
                    if not has_location_match:
                        continue  # Skip if no location match
                    
                    # Compile match information
                    match_info = {
                        # Buyer information
                        'buyer_name': buyer.get('Titel', ''),
                        'buyer_location': buyer.get('location (state + city)', ''),
                        'buyer_summary': buyer.get('summary', ''),
                        'buyer_title': buyer.get('Titel', ''),
                        'buyer_long_description': buyer.get('long description', ''),
                        'buyer_industry': buyer.get('Branche', ''),
                        'buyer_contact': buyer.get('contact details', ''),
                        
                        # Seller information
                        'seller_id': seller.get('source', 'Unknown').split('=')[-1] 
                            if pd.notna(seller.get('source')) else 'Unknown',
                        'seller_location': seller.get('location', ''),
                        'seller_summary': seller.get('description', ''),
                        'seller_title': seller.get('title', ''),
                        'seller_long_description': seller.get('long_description', ''),
                        'seller_industry': seller.get('branchen', ''),
                        'seller_contact': seller.get('url', ''),
                        
                        # Match details
                        'matching_locations': sorted(matching_locations),
                        'matching_keywords': matching_keywords
                    }
                    matches.append(match_info)
                    
        except Exception as e:
            logger.error(f"Error finding matches: {e}")
            
        return matches

    def export_matches_to_excel(self, matches: List[Dict], output_path: str = None) -> None:
        """Export matches to an Excel file with formatted sheets and summary statistics."""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f'business_matches_{timestamp}.xlsx'
    
            # Create a Pandas Excel writer
            writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
            
            # Convert matches to DataFrame
            matches_df = pd.DataFrame(matches)
            
            if matches_df.empty:
                logger.info("No matches found to export.")
                return
            
            # Convert list columns to strings
            matches_df['matching_keywords'] = matches_df['matching_keywords'].apply(lambda x: ', '.join(x))
            matches_df['matching_locations'] = matches_df['matching_locations'].apply(lambda x: ', '.join(x))
            
            # Reorder columns for better readability
            column_order = [
                # Match Information
                'matching_keywords',
                'matching_locations',
                
                # Buyer Information
                'buyer_name',
                'buyer_title',
                'buyer_summary',
                'buyer_long_description',
                'buyer_location',
                'buyer_industry',
                'buyer_contact',
                
                # Seller Information
                'seller_id',
                'seller_title',
                'seller_summary',
                'seller_long_description',
                'seller_location',
                'seller_industry',
                'seller_contact'
            ]
            
            # Reorder and write to Excel
            matches_df = matches_df[column_order]
            matches_df.to_excel(writer, sheet_name='Matches', index=False)
            
            # Create a summary sheet
            summary = {
                'Total Matches': [len(matches)],
                'Unique Buyers': [matches_df['buyer_name'].nunique()],
                'Unique Sellers': [matches_df['seller_id'].nunique()],
                'Top Matching Keywords': [', '.join(matches_df['matching_keywords'].str.split(', ').explode().value_counts().head(5).index)],
                'Top Matching States/Cities': [', '.join(matches_df['matching_locations'].str.split(', ').explode().value_counts().head(5).index)]
            }
            summary_df = pd.DataFrame(summary)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            matches_worksheet = writer.sheets['Matches']
            summary_worksheet = writer.sheets['Summary']
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Format the Matches header
            for col_num, value in enumerate(matches_df.columns.values):
                matches_worksheet.write(0, col_num, value, header_format)
            
            # Adjust column widths for Matches
            for i, col in enumerate(matches_df.columns):
                max_length = matches_df[col].astype(str).map(len).max()
                max_length = max(max_length, len(col)) + 2
                matches_worksheet.set_column(i, i, min(max_length, 50))
            
            # Format the Summary header
            for col_num, value in enumerate(summary_df.columns.values):
                summary_worksheet.write(0, col_num, value, header_format)
            
            # Adjust column widths for Summary
            for i, col in enumerate(summary_df.columns):
                max_length = summary_df[col].astype(str).map(len).max()
                max_length = max(max_length, len(col)) + 2
                summary_worksheet.set_column(i, i, min(max_length, 50))
            
            # Save the file
            writer.close()
            logger.info(f"Successfully exported matches to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting matches to Excel: {e}")
            raise

def main():
    # Initialize matcher
    matcher = BusinessMatcher()
    
    try:
        # Load data
        matcher.load_data(
            keywords_path='dejuna data feed - keywords.csv',
            buyers_path='dejuna data feed - buyer dejuna-new.csv',
            sellers_path='nexxt_change_sales_listings_20241031_000417.csv'
        )
        
        # Find matches
        matches = matcher.find_matches()
        logger.info(f"Found {len(matches)} matches")
        
        # Export matches to Excel
        matcher.export_matches_to_excel(matches)
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
