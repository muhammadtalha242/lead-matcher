import pandas as pd
import logging
from typing import List, Dict, Set, Tuple
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedBusinessMatcher:
    def __init__(self):
        """Initialize the matcher with NLP components."""
        self.sellers_df = None
        self.buyers_df = None
        # Define common business type keywords with expanded synonyms
        self.business_types = {
            'shk': {
                'sanitär', 'heizung', 'klima', 'sanitärtechnik', 'heizungstechnik',
                'wasserinstallation', 'klimatechnik', 'lüftung', 'sanitärhandwerk',
                'heizungsbau', 'klimaanlage', 'sanitärinstallation'
            },
            'elektro': {
                'elektro', 'elektriker', 'elektroinstallation', 'elektrotechnik',
                'elektroinstallationsfirma', 'elektronik', 'elektrohandwerk',
                'elektroarbeiten', 'elektrofachbetrieb', 'elektroanlagen',
                'elektroservice', 'elektrosysteme'
            }
        }
        
        # Additional industry-specific keywords
        self.industry_keywords = {
            'services': {
                'installation', 'wartung', 'reparatur', 'beratung', 'planung',
                'modernisierung', 'instandhaltung', 'service', 'montage'
            },
            'certifications': {
                'meisterbetrieb', 'fachbetrieb', 'zertifiziert', 'qualifiziert',
                'ausgezeichnet', 'iso', 'din'
            }
        }
        
        self.german_states = {
            'baden-württemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
            'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
            'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
            'sachsen-anhalt', 'schleswig-holstein', 'thüringen'
        }
        
        try:
            self.sentence_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
            logger.info("Successfully loaded NLP model")
        except Exception as e:
            logger.error(f"Error loading NLP model: {e}")
            raise

    def _get_text_summary(self, row: pd.Series) -> str:
        """Combine relevant text fields into a single summary."""
        return ' '.join(filter(pd.notna, [
            str(row['Titel']) if pd.notna(row['Titel']) else '',
            str(row['summary']) if pd.notna(row['summary']) else '',
            str(row['long description']) if pd.notna(row['long description']) else ''
        ])).lower()

    def _find_matching_keywords(self, text1: str, text2: str) -> Dict[str, Set[str]]:
        """Find matching keywords between two texts across different categories."""
        text1, text2 = text1.lower(), text2.lower()
        matching_keywords = {
            'business_types': {},
            'services': set(),
            'certifications': set()
        }
        
        # Check business type keywords
        for btype, keywords in self.business_types.items():
            matching = {kw for kw in keywords if kw in text1 and kw in text2}
            if matching:
                matching_keywords['business_types'][btype] = matching
        
        # Check industry keywords
        for category, keywords in self.industry_keywords.items():
            matching = {kw for kw in keywords if kw in text1 and kw in text2}
            if matching:
                matching_keywords[category] = matching
                
        return matching_keywords

    def _identify_business_type(self, text: str) -> Set[str]:
        """Identify business types mentioned in the text."""
        text = text.lower()
        found_types = set()
        
        for btype, keywords in self.business_types.items():
            if any(keyword in text for keyword in keywords):
                found_types.add(btype)
                
        return found_types

    def _extract_location_parts(self, location: str) -> Dict[str, Set[str]]:
        """Extract and categorize location parts into states and cities."""
        locations = {
            'states': set(),
            'cities': set()
        }
        
        if pd.isna(location):
            return locations
            
        parts = re.split(r'[,>\n]\s*', str(location).lower())
        for part in parts:
            part = part.strip()
            if part in self.german_states:
                locations['states'].add(part)
            else:
                city = re.sub(r'^region\s+', '', part)
                if city:
                    locations['cities'].add(city)
                    
        return locations

    def _check_location_match(self, buyer_loc: str, seller_loc: str) -> Tuple[bool, Set[str]]:
        """Check if locations match and return matching locations."""
        try:
            buyer_locs = self._extract_location_parts(buyer_loc)
            seller_locs = self._extract_location_parts(seller_loc)
            
            matching_states = buyer_locs['states'].intersection(seller_locs['states'])
            matching_cities = buyer_locs['cities'].intersection(seller_locs['cities'])
            
            has_match = bool(matching_states or matching_cities)
            matching_locations = matching_states.union(matching_cities)
            
            logger.debug(f"Buyer locations: {buyer_locs}")
            logger.debug(f"Seller locations: {seller_locs}")
            logger.debug(f"Matching locations: {matching_locations}")
            
            return has_match, matching_locations
            
        except Exception as e:
            logger.error(f"Error checking location match: {e}")
            return False, set()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        try:
            embedding1 = self.sentence_model.encode(str(text1))
            embedding2 = self.sentence_model.encode(str(text2))
            
            similarity = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    # def find_matches(self, similarity_threshold: float = 0.3) -> List[Dict]:
    #     """Find matches using business type, location matching, and keyword matching with semantic similarity."""
    #     matches = []
        
    #     try:
    #         for _, buyer in self.buyers_df.iterrows():
    #             buyer_text = self._get_text_summary(buyer)
    #             buyer_types = self._identify_business_type(buyer_text)
                
    #             for _, seller in self.sellers_df.iterrows():
    #                 seller_text = self._get_text_summary(seller)
    #                 seller_types = self._identify_business_type(seller_text)
                    
    #                 # Find matching keywords
    #                 matching_keywords = self._find_matching_keywords(buyer_text, seller_text)
                    
    #                 common_types = buyer_types.intersection(seller_types)
    #                 similarity = self._calculate_similarity(buyer_text, seller_text)
                    
    #                 has_location_match, matching_locations = self._check_location_match(
    #                     buyer['location (state + city)'],
    #                     seller['location (state + city)']
    #                 )
                    
    #                 logger.debug(f"Comparing buyer {buyer['contact details']} with seller {seller['source (link)']}")
    #                 logger.debug(f"Business types - Buyer: {buyer_types}, Seller: {seller_types}")
    #                 logger.debug(f"Location match: {has_location_match}")
    #                 logger.debug(f"Similarity score: {similarity}")
    #                 logger.debug(f"Matching keywords: {matching_keywords}")
                    
    #                 if (common_types or similarity >= similarity_threshold) and has_location_match:
    #                     match_info = {
    #                         'buyer_name': buyer['contact details'].split('\n')[0] 
    #                             if pd.notna(buyer['contact details']) else 'Unknown',
    #                         'seller_id': seller['source (link)'].split('=')[-1] 
    #                             if pd.notna(seller['source (link)']) else 'Unknown',
    #                         'semantic_similarity': round(similarity, 3),
    #                         'business_types': sorted(common_types),
    #                         'buyer_location': buyer['location (state + city)'],
    #                         'seller_location': seller['location (state + city)'],
    #                         'matching_locations': sorted(matching_locations),
    #                         'buyer_summary': buyer['summary'],
    #                         'seller_summary': seller['summary'],
    #                         'matching_keywords': matching_keywords
    #                     }
    #                     matches.append(match_info)
            
    #         matches.sort(key=lambda x: x['semantic_similarity'], reverse=True)
            
    #     except Exception as e:
    #         logger.error(f"Error finding matches: {e}")
            
    #     return matches
    def find_matches(self, similarity_threshold: float = 0.4) -> List[Dict]:
        """Find matches and include complete buyer and seller information."""
        matches = []
        
        try:
            for _, buyer in self.buyers_df.iterrows():
                buyer_text = self._get_text_summary(buyer)
                buyer_types = self._identify_business_type(buyer_text)
                
                for _, seller in self.sellers_df.iterrows():
                    seller_text = self._get_text_summary(seller)
                    seller_types = self._identify_business_type(seller_text)
                    
                    matching_keywords = self._find_matching_keywords(buyer_text, seller_text)
                    common_types = buyer_types.intersection(seller_types)
                    similarity = self._calculate_similarity(buyer_text, seller_text)
                    
                    has_location_match, matching_locations = self._check_location_match(
                        buyer['location (state + city)'],
                        seller['location (state + city)']
                    )
                    
                    if (common_types or similarity >= similarity_threshold) and has_location_match:
                        # Create comprehensive match info including all columns
                        match_info = {
                            # Match metrics
                            'semantic_similarity': round(similarity, 3),
                            'business_types': sorted(common_types),
                            'matching_locations': sorted(matching_locations),
                            
                            # Keywords matching information
                            'matching_business_keywords': ', '.join(
                                [f"{k}: {', '.join(v)}" for k, v in matching_keywords['business_types'].items()]
                            ),
                            'matching_service_keywords': ', '.join(sorted(matching_keywords['services'])),
                            'matching_certification_keywords': ', '.join(sorted(matching_keywords['certifications'])),
                            
                            # Buyer information - include all columns with prefix
                            **{f'buyer_{k}': str(v) for k, v in buyer.items()},
                            
                            # Seller information - include all columns with prefix
                            **{f'seller_{k}': str(v) for k, v in seller.items()}
                        }
                        matches.append(match_info)
            
            matches.sort(key=lambda x: x['semantic_similarity'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding matches: {e}")
            
        return matches

    def export_matches_to_excel(self, matches: List[Dict], output_file: str = None) -> None:
        """Export matches to a detailed Excel file with multiple sheets."""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f'business_matches_{timestamp}.xlsx'
            
            # Create Excel writer object
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # Convert matches to DataFrame
                matches_df = pd.DataFrame(matches)
                
                # Create Summary sheet
                summary_columns = [
                    'semantic_similarity',
                    'business_types',
                    'matching_locations',
                    'matching_business_keywords',
                    'matching_service_keywords',
                    'matching_certification_keywords',
                    'buyer_contact details',
                    'buyer_location (state + city)',
                    'buyer_summary',
                    'seller_source (link)',
                    'seller_location (state + city)',
                    'seller_summary'
                ]
                
                summary_df = matches_df[summary_columns].copy()
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Create Detailed Matches sheet with all information
                matches_df.to_excel(writer, sheet_name='Detailed Matches', index=False)
                
                # Format the Excel file
                workbook = writer.book
                
                # Add formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D9D9D9',
                    'border': 1
                })
                
                wrap_format = workbook.add_format({
                    'text_wrap': True,
                    'valign': 'top'
                })
                
                # Apply formats to both sheets
                for sheet_name in ['Summary', 'Detailed Matches']:
                    worksheet = writer.sheets[sheet_name]
                    worksheet.set_row(0, 30, header_format)  # Format header row
                    worksheet.set_column('A:ZZ', 30, wrap_format)  # Format all columns
                
            logger.info(f"Successfully exported matches to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting matches to Excel: {e}")
            raise

def print_matches(matches: List[Dict]) -> None:
    """Print matches with detailed information including matching keywords."""
    print("\n=== BUSINESS MATCHES ===\n")
    for i, match in enumerate(matches, 1):
        print(f"Match {i}:")
        print(f"Semantic Similarity: {match['semantic_similarity']:.3f}")
        if match['business_types']:
            print(f"Business Types: {', '.join(match['business_types'])}")
        
        print("\nMatching Keywords:")
        kw = match['matching_keywords']
        for btype, terms in kw['business_types'].items():
            print(f"- {btype.upper()} terms: {', '.join(sorted(terms))}")
        if kw['services']:
            print(f"- Services: {', '.join(sorted(kw['services']))}")
        if kw['certifications']:
            print(f"- Certifications: {', '.join(sorted(kw['certifications']))}")
            
        print(f"\nBuyer: {match['buyer_name']}")
        print(f"Buyer Summary: {match['buyer_summary']}")
        print(f"\nSeller ID: {match['seller_id']}")
        print(f"Seller Summary: {match['seller_summary']}")
        print(f"\nMatching Locations: {', '.join(match['matching_locations'])}")
        print(f"Buyer Location: {match['buyer_location']}")
        print(f"Seller Location: {match['seller_location']}")
        print("-" * 70)

def main():
    logger.setLevel(logging.DEBUG)
    
    matcher = EnhancedBusinessMatcher()
    
    try:
        matcher.sellers_df = pd.read_csv('nexxt_change_sales_listings_20241027_091323.csv')
        matcher.buyers_df = pd.read_csv('nexxt_change_purchase_listings_20241027_091154.csv')
        
        matches = matcher.find_matches()
        # Export matches to Excel
        matcher.export_matches_to_excel(matches)
        
        # Still print matches to console for immediate feedback
        # print_matches(matches)
        logger.info(f"Found {len(matches)} matches")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()