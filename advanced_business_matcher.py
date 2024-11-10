import pandas as pd
import spacy
from typing import List, Dict, Set, Tuple
import re
from thefuzz import fuzz
from collections import defaultdict
import numpy as np
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedBusinessMatcher:
    def __init__(self):
        """Initialize the matcher with necessary components."""
        self.nlp = None
        self.keywords_df = None
        self.sellers_df = None
        self.buyers_df = None
        self.keyword_synonyms = {}
        
    def initialize_nlp(self):
        """Initialize spaCy NLP model with error handling."""
        try:
            self.nlp = spacy.load('de_core_news_lg')
            logger.info("Successfully loaded German language model")
        except OSError as e:
            logger.error(f"Failed to load German language model: {e}")
            raise
            
        
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
            
            self._preprocess_descriptions()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def _preprocess_descriptions(self):
        """Preprocess all descriptions using NLP."""
        try:
            # Process seller descriptions
            self.buyers_df['processed_description'] = self.buyers_df.apply(
                lambda x: self._process_text(
                    ' '.join(filter(pd.notna, [
                        str(x['Titel']) if pd.notna(x['Titel']) else '',
                        str(x['summary']) if pd.notna(x['summary']) else '',
                        str(x['long description']) if pd.notna(x['long description']) else ''
                    ]))
                ),
                axis=1
            )
            
            # Process buyer descriptions
            self.sellers_df['processed_description'] = self.sellers_df.apply(
                lambda x: self._process_text(
                    ' '.join(filter(pd.notna, [
                        str(x['long_description']) if pd.notna(x['long_description']) else '',
                        str(x['title']) if pd.notna(x['title']) else '',
                        str(x['description']) if pd.notna(x['description']) else ''
                    ]))
                ),
                axis=1
            )
            
            logger.info("Successfully preprocessed descriptions")
            
        except Exception as e:
            logger.error(f"Error preprocessing descriptions: {e}")
            raise

    def _process_text(self, text: str) -> str:
        """Process text using spaCy NLP."""
        if not text or pd.isna(text):
            return ""
        
        try:
            doc = self.nlp(text)
            # Keep relevant tokens and lemmatize
            processed_tokens = [
                token.lemma_.lower() for token in doc
                if not token.is_stop and not token.is_punct and token.is_alpha
            ]
            return ' '.join(processed_tokens)
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return text.lower()  # Fallback to simple lowercase if NLP fails

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        try:
            if not text1 or not text2:
                return 0.0
            
            doc1 = self.nlp(text1[:1000000])  # Limit text length to prevent memory issues
            doc2 = self.nlp(text2[:1000000])
            
            return doc1.similarity(doc2)
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0

    def _extract_location_parts(self, location: str) -> Dict[str, Set[str]]:
        """Extract and categorize location parts."""
        parts = {
            'states': set(),
            'cities': set(),
            'regions': set()
        }
        
        if pd.isna(location):
            return parts
        
        try:
            # German state names for validation
            german_states = {
                'baden-württemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
                'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
                'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
                'sachsen-anhalt', 'schleswig-holstein', 'thüringen'
            }
            
            location_parts = re.split(r'[,>]\s*', str(location))
            for part in location_parts:
                part = part.strip().lower()
                if part in german_states:
                    parts['states'].add(part)
                elif 'region' in part.lower():
                    parts['regions'].add(part)
                else:
                    parts['cities'].add(part)
                    
        except Exception as e:
            logger.error(f"Error extracting location parts: {e}")
            
        return parts

    def _calculate_match_scores(self, buyer: pd.Series, seller: pd.Series) -> Dict[str, float]:
        """Calculate all match scores between a buyer and seller."""
        try:
            # Initialize scores
            scores = {
                'location': 0.0,
                'keyword': 0.0,
                'semantic': 0.0
            }
            
            # Calculate location score
            buyer_loc = self._extract_location_parts(buyer['location (state + city)'])
            seller_loc = self._extract_location_parts(seller['location'])
            
            location_matches = 0
            total_locations = 0
            for category in ['states', 'cities', 'regions']:
                if buyer_loc[category] and seller_loc[category]:
                    matches = len(buyer_loc[category].intersection(seller_loc[category]))
                    location_matches += matches
                    total_locations += len(buyer_loc[category])
            
            scores['location'] = location_matches / max(total_locations, 1)
            
            # Calculate keyword score
            buyer_text = str(buyer['processed_description']).lower()
            seller_text = str(seller['processed_description']).lower()
            
            keyword_matches = 0
            for keyword_data in self.keyword_synonyms.values():
                if any(syn in buyer_text for syn in keyword_data['synonyms']) and \
                   any(syn in seller_text for syn in keyword_data['synonyms']):
                    keyword_matches += 1
            
            scores['keyword'] = keyword_matches / max(len(self.keyword_synonyms), 1)
            
            # Calculate semantic similarity
            scores['semantic'] = self._calculate_semantic_similarity(
                buyer['processed_description'],
                seller['processed_description']
            )
            
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating match scores: {e}")
            return {'location': 0.0, 'keyword': 0.0, 'semantic': 0.0}

    def find_matches(self, threshold: float = 0.3) -> List[Dict]:
        """Find matches using enhanced matching algorithm."""
        matches = []
        
        try:
            for _, buyer in self.buyers_df.iterrows():
                for _, seller in self.sellers_df.iterrows():
                    # Calculate scores
                    scores = self._calculate_match_scores(buyer, seller)
                    
                    # Calculate weighted final score
                    weights = {
                        'location': 0.4,
                        'keyword': 0.4,
                        'semantic': 0.2
                    }
                    
                    final_score = sum(score * weights[metric] 
                                    for metric, score in scores.items())
                    
                    if final_score >= threshold:
                        match_info = {
                            'final_score': final_score,
                            'location_score': scores['location'],
                            'keyword_score': scores['keyword'],
                            'semantic_score': scores['semantic'],
                            'buyer_location': buyer['location (state + city)'],
                            'seller_location': seller['location'],
                            'matching_keywords': self._get_matching_keywords(
                                buyer['processed_description'],
                                seller['processed_description']
                            )
                        }
                        matches.append(match_info)
            
            # Sort matches by final score
            matches.sort(key=lambda x: x['final_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding matches: {e}")
            
        return matches

    def _get_matching_keywords(self, buyer_text: str, seller_text: str) -> List[str]:
        """Get list of matching keywords between buyer and seller."""
        matching_keywords = []
        
        try:
            buyer_text = str(buyer_text).lower()
            seller_text = str(seller_text).lower()
            
            for keyword, data in self.keyword_synonyms.items():
                if any(syn in buyer_text for syn in data['synonyms']) and \
                   any(syn in seller_text for syn in data['synonyms']):
                    matching_keywords.append(data['original'])
                    
        except Exception as e:
            logger.error(f"Error getting matching keywords: {e}")
            
        return matching_keywords

def print_matches(matches: List[Dict]) -> None:
    """Print matches with detailed scores."""
    print("\n=== DETAILED BUSINESS MATCHES ===\n")
    for i, match in enumerate(matches, 1):
        print(f"Match {i}:")
        print(f"Buyer: {match['buyer_name']}")
        print(f"Seller ID: {match['seller_id']}")
        print(f"\nScores:")
        print(f"Overall Match Score: {match['final_score']:.2f}")
        print(f"- Location Match: {match['location_score']:.2f}")
        print(f"- Keyword Match: {match['keyword_score']:.2f}")
        print(f"- Semantic Similarity: {match['semantic_score']:.2f}")
        print(f"\nMatching Keywords: {', '.join(match['matching_keywords'])}")
        print(f"\nLocations:")
        print(f"Buyer: {match['buyer_location']}")
        print(f"Seller: {match['seller_location']}")
        print("-" * 70)

def main():
    # Initialize matcher
    matcher = AdvancedBusinessMatcher()
    
    try:
        # Initialize NLP
        matcher.initialize_nlp()
        
        # Load data
        matcher.load_data(
            keywords_path="Updated_Keywords_and_Synonyms.csv",
            buyers_path="dejuna data feed - buyer dejuna-new.csv",
            sellers_path="nexxt_change_sales_listings_20241101_005703.csv"
        )
        
        # Find matches
        matches = matcher.find_matches(threshold=0.1)
        
        # Print results
        print_matches(matches)
        
        # Log summary
        logger.info(f"Found {len(matches)} matches above threshold")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()