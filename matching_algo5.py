import pandas as pd 
import logging
from typing import List, Dict, Set, Tuple
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import numpy as np
from rapidfuzz import fuzz
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
german_stop_words = set(stopwords.words('german'))


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BusinessCategory:
    def __init__(self, name: str, keywords: Set[str]):
        self.name = name
        self.keywords = keywords
        self.synonyms = keywords  # For extensibility

class KeywordMatcher:
    def __init__(self):
        # Initialize business categories from the keywords file
        self.categories = {
            'shk': BusinessCategory('Heizung Sanitär', {
                'heizung sanitär', 'heizungsbau', 'shk', 'heizung sanitär klima', 
                'sanitär heizung klima'
            }),
            'elektro': BusinessCategory('Elektrofirma', {
                'elektrofirma', 'elektrobetrieb', 'elektrotechnik', 'elektroinstallation',
                'elektromeister', 'elektrotechnikermeister'
            })
        }
        
        self.german_states = {
            'baden-württemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
            'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
            'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
            'sachsen-anhalt', 'schleswig-holstein', 'thüringen'
        }

    def find_categories(self, text: str) -> Set[str]:
        if pd.isna(text):
            return set()
        text = str(text).lower()
        found_categories = set()

        for category_id, category in self.categories.items():
            for keyword in category.keywords:
                if fuzz.partial_ratio(keyword, text) > 80:
                    found_categories.add(category_id)
                    break
        return found_categories

class EnhancedBusinessMatcher:
    def __init__(self):
        self.keyword_matcher = KeywordMatcher()
        try:
            self.sentence_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
            logger.info("Successfully loaded NLP model")
        except Exception as e:
            logger.error(f"Error loading NLP model: {e}")
            raise

    def _normalize_text(self, text: str) -> str:
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = re.sub(r'\d+', '', text)  # Remove numbers
        tokens = text.split()
        tokens = [word for word in tokens if word not in german_stop_words]
        return ' '.join(tokens)

    def _get_buyer_text_content(self, record: Dict) -> str:
        """Extract and combine relevant text content from a buyer record"""
        fields = ['title', 'description', 'long_description']
                # Include additional business-relevant fields
        text_content = ' '.join(self._normalize_text(record.get(field, '')) for field in fields)
        # Include additional business-relevant fields
        extra_fields = ['Industrie', 'Sub-Industrie']
        text_content += ' ' + ' '.join(self._normalize_text(record.get(field, '')) for field in extra_fields)
        return text_content


    def _get_seller_text_content(self, record: Dict) -> str:
        """Extract and combine relevant text content from a seller record"""
        fields = ['title', 'description', 'long_description']
        text_content = ' '.join(self._normalize_text(record.get(field, '')) for field in fields)
        # Include additional business-relevant fields
        extra_fields = ['branchen']
        text_content += ' ' + ' '.join(self._normalize_text(record.get(field, '')) for field in extra_fields)
        return text_content

    def _parse_location(self, location: str) -> Dict[str, Set[str]]:
        """Parse location string into structured format"""
        if pd.isna(location):
            return {'states': set(), 'cities': set()}
            
        location = str(location).lower()
        locations = {
            'states': set(),
            'cities': set()
        }
        
        # parts = re.split(r'[,>\n]\s*', location)
        parts = re.split(r'[>/,\n]\s*', str(location))
        for part in parts:
            part = part.strip()
            if part in self.keyword_matcher.german_states:
                locations['states'].add(part)
            elif part:  # Any non-empty string that's not a state is considered a city
                city = re.sub(r'^region\s+', '', part)
                locations['cities'].add(city)
                
        return locations

    def _check_location_match(self, buyer_loc: str, seller_loc: Dict[str, str]) -> Tuple[bool, Set[str]]:
        """Check if locations match between buyer and seller"""
        buyer_locations = self._parse_location(buyer_loc)
        seller_locations = self._parse_location(seller_loc.get('location', ''))
        
        # For sellers, also check 'standort' if available
        if 'standort' in seller_loc:
            seller_standort = self._parse_location(seller_loc['standort'])
            seller_locations['states'].update(seller_standort['states'])
            seller_locations['cities'].update(seller_standort['cities'])
        
        matching_states = buyer_locations['states'].intersection(seller_locations['states'])
        matching_cities = buyer_locations['cities'].intersection(seller_locations['cities'])
        
        # Consider a match if either states or cities match
        has_match = bool(matching_states or matching_cities)
        matching_locations = matching_states.union(matching_cities)
        
        return has_match, matching_locations

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        try:
            if not text1.strip() or not text2.strip():
                return 0.0
                
            embedding1 = self.sentence_model.encode(text1)
            embedding2 = self.sentence_model.encode(text2)
            
            similarity = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def find_matches(self, buyers_data: List[Dict], sellers_data: List[Dict], 
                    min_similarity: float = 0.6) -> List[Dict]:
        """Find matches between buyers and sellers"""
        matches = []
        seen_matches = set()  # Track unique matches
        
        for buyer in buyers_data:
            buyer_text = self._get_buyer_text_content(buyer)
            buyer_categories = self.keyword_matcher.find_categories(buyer_text)
            
            for seller in sellers_data:
                seller_text = self._get_seller_text_content(seller)
                seller_categories = self.keyword_matcher.find_categories(seller_text)
                
                # Create unique match identifier using contact/url
                match_id = f"{buyer.get('contact details', '')}-{seller.get('url', '')}"
                if match_id in seen_matches:
                    continue
                
                # Check for category match
                common_categories = buyer_categories.intersection(seller_categories)
                if not common_categories:
                    continue
                
                # Check location match
                has_location_match, matching_locations = self._check_location_match(
                    buyer.get('location', ''),
                    {'location': seller.get('location', ''), 'standort': seller.get('standort', '')}
                )
                
                if not has_location_match:
                    continue
                
                # Calculate semantic similarity
                similarity = self._calculate_semantic_similarity(buyer_text, seller_text)
                if similarity < min_similarity:
                    continue
                
                match_info = {
                    'match_score': round(similarity, 3),
                    'matching_categories': sorted(common_categories),
                    'matching_locations': sorted(matching_locations),
                    'buyer_info': {
                        'date': buyer.get('publishing date', ''),
                        'location': buyer.get('location', ''),
                        'title': buyer.get('title', ''),
                        'summary': buyer.get('description', ''),
                        'description': buyer.get('long_description', ''),
                        'contact': buyer.get('contact details', '')
                    },
                    'seller_info': {
                        'date': seller.get('date', ''),
                        'location': seller.get('location', ''),
                        'standort': seller.get('standort', ''),
                        'title': seller.get('title', ''),
                        'description': seller.get('description', ''),
                        'long_description': seller.get('long_description', ''),
                        'url': seller.get('url', ''),
                        'employees': seller.get('mitarbeiter', ''),
                        'revenue': seller.get('jahresumsatz', ''),
                        'price': seller.get('preisvorstellung', ''),
                        'international': seller.get('international', '')
                    }
                }
                
                matches.append(match_info)
                seen_matches.add(match_id)
        
        # Sort matches by score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches

    def export_matches(self, matches: List[Dict], output_file: str = None) -> None:
        """Export matches to Excel with detailed formatting"""
        if not matches:
            logger.warning("No matches to export")
            return
            
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'./matches/business_matches_{timestamp}.xlsx'
            
        try:
            # Convert matches to DataFrame with proper handling of null values
            df_records = []
            for match in matches:
                record = {
                    'Match Score': match['match_score'],
                    'Matching Categories': ', '.join(match['matching_categories'] or []),
                    'Matching Locations': ', '.join(match['matching_locations'] or []),
                    'Buyer Date': match['buyer_info'].get('date', ''),
                    'Buyer Location': match['buyer_info'].get('location', ''),
                    'Buyer Title': match['buyer_info'].get('title', ''),
                    'Buyer Summary': match['buyer_info'].get('description', ''),
                    'Buyer Description': match['buyer_info'].get('description', ''),
                    'Buyer Contact': match['buyer_info'].get('contact', ''),
                    'Seller Date': match['seller_info'].get('date', ''),
                    'Seller Location': match['seller_info'].get('location', ''),
                    'Seller Standort': match['seller_info'].get('standort', ''),
                    'Seller Title': match['seller_info'].get('title', ''),
                    'Seller Description': match['seller_info'].get('description', ''),
                    'Seller Long Description': match['seller_info'].get('long_description', ''),
                    'Seller URL': match['seller_info'].get('url', ''),
                    'Employees': match['seller_info'].get('employees', ''),
                    'Annual Revenue': match['seller_info'].get('revenue', ''),
                    'Price Expectation': match['seller_info'].get('price', ''),
                    'International': match['seller_info'].get('international', '')
                }
                df_records.append(record)
                
            df = pd.DataFrame(df_records)
            
            # Replace any None/NaN values with empty strings
            df = df.fillna('')
            
            # Export to Excel using the safe ExcelWriter interface
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Matches', index=False)
                
                # Get workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Matches']
                
                # Define formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D9D9D9',
                    'border': 1
                })
                
                # Apply formats safely
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Set column widths safely
                for col_num in range(len(df.columns)):
                    worksheet.set_column(col_num, col_num, 30)
                
                # Add autofilter safely
                worksheet.autofilter(0, 0, len(df_records), len(df.columns) - 1)
                
            logger.info(f"Successfully exported {len(matches)} matches to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting matches: {e}")
            raise

def main():
    try:
        # Read input files with proper error handling
        try:
            buyers_df = pd.read_csv('./data/buyer_dejuna.csv', encoding='utf-8')
            sellers_df = pd.read_csv('./data/nexxt_change_sales_listings.csv', encoding='utf-8')
        except Exception as e:
            logger.error(f"Error reading input files: {e}")
            raise
        
        # Convert DataFrames to list of dictionaries
        buyers_data = buyers_df.to_dict('records')
        sellers_data = sellers_df.to_dict('records')
        
        # Initialize matcher and find matches
        matcher = EnhancedBusinessMatcher()
        matches = matcher.find_matches(buyers_data, sellers_data)
        
        # Export results
        matcher.export_matches(matches)
        # print(matches)
        logger.info(f"Processing complete. Found {len(matches)} matches.")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()