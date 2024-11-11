import pandas as pd
import logging
from typing import List, Dict, Set, Tuple
import re
from datetime import datetime
from difflib import SequenceMatcher

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
        
    def load_data(self, keywords_path: str, buyers_path: str, sellers_path: str) -> None:
        """Load and prepare the data with error handling."""
        try:
            # Load keywords and create enhanced synonym dictionary
            path_dir = './data/'
            filePath = f"{path_dir}{keywords_path}"
            self.keywords_df = pd.read_csv(filePath)
            logger.info(f"Successfully loaded keywords from {keywords_path}")
            
            # Create keyword dictionary with synonyms
            for _, row in self.keywords_df.iterrows():
                if pd.notna(row['Keyword']):
                    synonyms = set()
                    synonyms.add(row['Keyword'].lower())
                    
                    for col in [f'Synonym {i}' for i in range(1, 6)]:
                        if pd.notna(row[col]):
                            synonyms.add(row[col].lower())
                            
                    self.keyword_synonyms[row['Keyword'].lower()] = {
                        'synonyms': synonyms,
                        'original': row['Keyword']
                    }
            
            # Load buyers data
            self.buyers_df = pd.read_csv(f"{path_dir}{buyers_path}")
            logger.info(f"Successfully loaded buyer data from {buyers_path}")
            
            # Load sellers data
            self.sellers_df = pd.read_csv(f"{path_dir}{sellers_path}")
            logger.info(f"Successfully loaded seller data from {sellers_path}")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

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
            parts = re.split(r'[>/,\n]\s*', str(location))
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

    def _find_matching_keywords(self, text1: str, text2: str) -> List[str]:
        """Find matching keywords between two texts."""
        matching_keywords = []
        
        if pd.isna(text1) or pd.isna(text2):
            return matching_keywords
            
        text1 = str(text1).lower()
        text2 = str(text2).lower()
        
        try:
            for keyword, data in self.keyword_synonyms.items():
                # Check if any synonyms appear in both texts
                if any(syn in text1 for syn in data['synonyms']) and \
                   any(syn in text2 for syn in data['synonyms']):
                    matching_keywords.append(data['original'])
                    
        except Exception as e:
            logger.error(f"Error finding matching keywords: {e}")

        return matching_keywords

    def _check_keyword_match(self, buyer: pd.Series, seller: pd.Series) -> Tuple[bool, List[str]]:
        """Check if there are matching keywords and return them."""
        try:
            # Use the correct column names for buyer and seller
            buyer_text = ' '.join(filter(pd.notna, [
                str(buyer.get('Titel', '')),
                str(buyer.get('summary', '')),
                str(buyer.get('long description', '')),
                str(buyer.get('Industrie', '')),
                str(buyer.get('Sub-Industrie', ''))
            ])).lower()
            
            seller_text = ' '.join(filter(pd.notna, [
                str(seller.get('title', '')),
                str(seller.get('description', '')),
                str(seller.get('long_description', '')),
                str(seller.get('branchen', ''))
            ])).lower()
            
            matching_keywords = self._find_matching_keywords(buyer_text, seller_text)
            industry_match = self._industry_match(buyer, seller)

            has_match = bool(matching_keywords) and industry_match
            
            return has_match, matching_keywords
                
        except Exception as e:
            logger.error(f"Error checking keyword match: {str(e)}")
            return False, []
        
    def _industry_match(self, buyer: pd.Series, seller: pd.Series) -> bool:
        """Check if the buyer and seller industries match using fuzzy matching."""
        buyer_industry = ' '.join(filter(pd.notna, [
            str(buyer.get('Industrie', '')),
            str(buyer.get('Sub-Industrie', ''))
        ])).lower()
        
        seller_industry = str(seller.get('branchen', '')).lower()

        if not buyer_industry or not seller_industry:
            return False

        # Use SequenceMatcher to calculate similarity ratio
        ratio = SequenceMatcher(None, buyer_industry, seller_industry).ratio()
        return ratio >= 0.4  # Lowered threshold to 0.4

    def find_matches(self) -> List[Dict]:
        """Find matches requiring both location and keyword matches."""
        matches = []
        
        try:
            for _, buyer in self.buyers_df.iterrows():
                for _, seller in self.sellers_df.iterrows():
                    try:
                        # Check keyword matches
                        has_keyword_match, matching_keywords = self._check_keyword_match(buyer, seller)
                        if not has_keyword_match:
                            continue
                        # Check location matches using correct column names
                        has_location_match, matching_locations = self._check_location_match(
                            buyer.get('location (state + city)', ''),
                            seller.get('location', '')
                        )
                        if not has_location_match:
                            continue
                        
                        # Create a match
                        match_info = {
                            # Buyer information
                            'buyer_name': buyer.get('Titel', ''),
                            'buyer_location': buyer.get('location (state + city)', ''),
                            'buyer_summary': buyer.get('summary', ''),
                            'buyer_title': buyer.get('Titel', ''),
                            'buyer_long_description': buyer.get('long description', ''),
                            'buyer_industry': buyer.get('Sub-Industrie', ''),
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
                        logger.error(f"Error processing match for buyer {buyer.get('Titel', 'Unknown')}: {str(e)}")
                        continue
            
        except Exception as e:
            logger.error(f"Error finding matches: {str(e)}")
            
        return matches

    def export_matches_to_excel(self, matches: List[Dict], output_path: str = None) -> None:
        """Export matches to an Excel file with formatted sheets."""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f'./matches/business_matches_{timestamp}.xlsx'

            # Create a Pandas Excel writer
            writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
            
            # Convert matches to DataFrame
            matches_df = pd.DataFrame(matches)
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
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Matches']
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Format the header
            for col_num, value in enumerate(matches_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Adjust column widths
            for i, col in enumerate(matches_df.columns):
                max_length = max(
                    matches_df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.set_column(i, i, min(max_length + 2, 50))
            
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
            keywords_path="Updated_Keywords_and_Synonyms.csv",
            buyers_path="dejuna_data_feed_updated_detailed.csv",
            sellers_path="nexxt_change_sales_listings_20241101_005703.csv"
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
