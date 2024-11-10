import pandas as pd
import logging
from typing import List, Dict, Set, Tuple
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedBusinessMatcher:
    def __init__(self):
        """Initialize the matcher with NLP components."""
        self.sellers_df = None
        self.buyers_df = None
        # Define common business type keywords
        self.business_types = {
            'shk': {'shk', 'sanitär', 'heizung', 'klima', 'sanitärtechnik', 'heizungstechnik'},
            'elektro': {'elektro', 'elektriker', 'elektroinstallation', 'elektrotechnik', 'elektroinstallationsfirma'}
        }
        
        self.german_states = {
            'baden-württemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
            'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
            'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
            'sachsen-anhalt', 'schleswig-holstein', 'thüringen'
        }
        
        # Load NLP model
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
                # Clean city names
                city = re.sub(r'^region\s+', '', part)
                if city:
                    locations['cities'].add(city)
                    
        return locations

    def _check_location_match(self, buyer_loc: str, seller_loc: str) -> Tuple[bool, Set[str]]:
        """Check if locations match and return matching locations."""
        try:
            buyer_locs = self._extract_location_parts(buyer_loc)
            seller_locs = self._extract_location_parts(seller_loc)
            
            # Check for matches in states or cities
            matching_states = buyer_locs['states'].intersection(seller_locs['states'])
            matching_cities = buyer_locs['cities'].intersection(seller_locs['cities'])
            
            # Location matches if either states or cities match
            has_match = bool(matching_states or matching_cities)
            matching_locations = matching_states.union(matching_cities)
            
            # Debug logging
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
            # Encode texts
            embedding1 = self.sentence_model.encode(str(text1))
            embedding2 = self.sentence_model.encode(str(text2))
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def find_matches(self, similarity_threshold: float = 0.3) -> List[Dict]:
        """Find matches using business type and location matching with semantic similarity."""
        matches = []
        
        try:
            for _, buyer in self.buyers_df.iterrows():
                buyer_text = self._get_text_summary(buyer)
                buyer_types = self._identify_business_type(buyer_text)
                
                for _, seller in self.sellers_df.iterrows():
                    seller_text = self._get_text_summary(seller)
                    seller_types = self._identify_business_type(seller_text)
                    
                    # Check for business type overlap
                    common_types = buyer_types.intersection(seller_types)
                    
                    # Calculate semantic similarity
                    similarity = self._calculate_similarity(buyer_text, seller_text)
                    
                    # Check location matches
                    has_location_match, matching_locations = self._check_location_match(
                        buyer['location (state + city)'],
                        seller['location (state + city)']
                    )
                    
                    # Debug logging
                    logger.debug(f"Comparing buyer {buyer['contact details']} with seller {seller['source (link)']}")
                    logger.debug(f"Business types - Buyer: {buyer_types}, Seller: {seller_types}")
                    logger.debug(f"Location match: {has_location_match}")
                    logger.debug(f"Similarity score: {similarity}")
                    
                    # Create match if criteria are met
                    if (common_types or similarity >= similarity_threshold) and has_location_match:
                        match_info = {
                            'buyer_name': buyer['contact details'].split('\n')[0] 
                                if pd.notna(buyer['contact details']) else 'Unknown',
                            'seller_id': seller['source (link)'].split('=')[-1] 
                                if pd.notna(seller['source (link)']) else 'Unknown',
                            'semantic_similarity': round(similarity, 3),
                            'business_types': sorted(common_types),
                            'buyer_location': buyer['location (state + city)'],
                            'seller_location': seller['location (state + city)'],
                            'matching_locations': sorted(matching_locations),
                            'buyer_summary': buyer['summary'],
                            'seller_summary': seller['summary']
                        }
                        matches.append(match_info)
            
            # Sort matches by similarity score
            matches.sort(key=lambda x: x['semantic_similarity'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding matches: {e}")
            
        return matches

def print_matches(matches: List[Dict]) -> None:
    """Print matches with detailed information."""
    print("\n=== BUSINESS MATCHES ===\n")
    for i, match in enumerate(matches, 1):
        print(f"Match {i}:")
        print(f"Semantic Similarity: {match['semantic_similarity']:.3f}")
        if match['business_types']:
            print(f"Business Types: {', '.join(match['business_types'])}")
        print(f"\nBuyer: {match['buyer_name']}")
        print(f"Buyer Summary: {match['buyer_summary']}")
        print(f"\nSeller ID: {match['seller_id']}")
        print(f"Seller Summary: {match['seller_summary']}")
        print(f"\nMatching Locations: {', '.join(match['matching_locations'])}")
        print(f"Buyer Location: {match['buyer_location']}")
        print(f"Seller Location: {match['seller_location']}")
        print("-" * 70)

def main():
    # Set debug logging
    logger.setLevel(logging.DEBUG)
    
    matcher = EnhancedBusinessMatcher()
    
    try:
        # Load data
        matcher.sellers_df = pd.read_csv('100_Sample_Seller_Data.csv')
        matcher.buyers_df = pd.read_csv('100_Sample_Buyer_Data.csv')
        
        # Find matches
        matches = matcher.find_matches()
        
        # Print results
        print_matches("PRINT: ",matches)
        
        logger.info(f"Found {len(matches)} matches")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()