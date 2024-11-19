import pandas as pd 
import logging
from typing import List, Dict, Set, Tuple
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import numpy as np
from rapidfuzz import fuzz, process
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BusinessCategory:
    def __init__(self, name: str, keywords: Set[str]):
        self.name = name
        self.keywords = keywords
        self.synonyms = keywords  # For extensibility

class KeywordMatcher:
    def __init__(self):
        # Initialize business categories from the provided list
        self.categories = {
            'tischlerei': BusinessCategory('Tischlerei', {
                'schreinerei', 'tischlermeister'
            }),
            'zimmerei': BusinessCategory('Zimmerei', {
                'zimmerer', 'holzbau', 'dachstuhl'
            }),
            'hausverwaltung': BusinessCategory('Hausverwaltung', {
                'immobilienverwaltung', 'weg-verwaltung'
            }),
            'pension': BusinessCategory('Pension', {
                'frühstückspension', 'gästehaus'
            }),
            'gebaeudereinigung': BusinessCategory('Gebäudereinigung', {
                'reinigungsfirma', 'hausreinigung'
            }),
            'textilreinigung': BusinessCategory('Textilreinigung', {
                'wäscherei', 'chemische reinigung'
            }),
            'heizung_sanitaer': BusinessCategory('Heizung Sanitär', {
                'heizungsbau', 'sanitär-heizung-klima'
            }),
            'elektrofirma': BusinessCategory('Elektrofirma', {
                'elektrobetrieb', 'elektroinstallation'
            }),
            'dachdeckerei': BusinessCategory('Dachdeckerei', {
                'dachdeckerbetrieb', 'dachdeckermeister'
            }),
            'malerfirma': BusinessCategory('Malerfirma', {
                'malerbetrieb', 'malermeister'
            }),
            'metallbau': BusinessCategory('Metallbau', {
                'metallbauer', 'stahlbau'
            }),
            'schlosserei': BusinessCategory('Schlosserei', {
                'schlosser', 'geländerbau'
            }),
            'bauunternehmen': BusinessCategory('Bauunternehmen', {
                'baufirma', 'baumeister'
            }),
            'maschinenbau': BusinessCategory('Maschinenbau', {
                'anlagenbau', 'industrietechnik'
            }),
            'gartenbaubetrieb': BusinessCategory('Gartenbaubetrieb', {
                'gartenbauunternehmen', 'landschaftsbau'
            }),
            'glaserei': BusinessCategory('Glaserei', {
                'glaser', 'glasbau'
            }),
            'behaelterbau': BusinessCategory('Behälterbau', {
                'industriebehälter', 'tankbau'
            }),
            'tankschutz': BusinessCategory('Tankschutz', {
                'tank-wartung', 'tank-reinigung'
            }),
            'oberflaechenbeschichtung': BusinessCategory('Oberflächenbeschichtung', {
                'lackierung', 'pulverbeschichtung'
            }),
            'steinmetzbetrieb': BusinessCategory('Steinmetzbetrieb', {
                'steinmetz', 'grabsteine'
            }),
            'hausmeisterservice': BusinessCategory('Hausmeisterservice', {
                'hausmeisterfirma', 'gebäudemanagement'
            }),
            'pflegedienst': BusinessCategory('Pflegedienst', {
                'ambulanter pflegedienst', 'altenpflege'
            }),
            'sanitaetshaus': BusinessCategory('Sanitätshaus', {
                'orthopädietechnik', 'rehatechnik'
            }),
            'zahnarztpraxis': BusinessCategory('Zahnarztpraxis', {
                'zahnarzt', 'kieferorthopädie'
            }),
            'arztpraxis': BusinessCategory('Arztpraxis', {
                'medizinische praxis', 'allgemeinmedizin'
            }),
            'tierarztpraxis': BusinessCategory('Tierarztpraxis', {
                'tierarzt', 'veterinärpraxis'
            }),
            'rechtsanwaltskanzlei': BusinessCategory('Rechtsanwaltskanzlei', {
                'anwaltskanzlei', 'anwalt'
            }),
            'steuerberatung': BusinessCategory('Steuerberatung', {
                'steuerberater', 'steuerkanzlei'
            }),
            'notariat': BusinessCategory('Notariat', {
                'notar', 'beglaubigung'
            }),
            'architekturbuero': BusinessCategory('Architekturbüro', {
                'architekt', 'bauplanung'
            }),
            'ingenieurbuero': BusinessCategory('Ingenieurbüro', {
                'bauingenieurwesen', 'planungsingenieur'
            }),
            'fotostudio': BusinessCategory('Fotostudio', {
                'fotoatelier', 'portraitfotografie'
            }),
            'kosmetikstudio': BusinessCategory('Kosmetikstudio', {
                'kosmetikerin', 'nagelstudio'
            }),
            'friseursalon': BusinessCategory('Friseursalon', {
                'haarstudio', 'friseurmeister'
            }),
            'reisebuero': BusinessCategory('Reisebüro', {
                'urlaubsplanung', 'reiseberatung'
            }),
            'musikschule': BusinessCategory('Musikschule', {
                'musikunterricht', 'musikpädagogik'
            }),
            'fitnessstudio': BusinessCategory('Fitnessstudio', {
                'fitnesstraining', 'sportstudio'
            }),
            'kunstgalerie': BusinessCategory('Kunstgalerie', {
                'galerie', 'kunsthandel'
            }),
            'landwirtschaft': BusinessCategory('Landwirtschaft', {
                'bauernhof', 'agrarwirtschaft'
            }),
            'baeckerei': BusinessCategory('Bäckerei', {
                'bäcker', 'backwaren'
            }),
            'metzgerei': BusinessCategory('Metzgerei', {
                'fleischerei', 'wurstherstellung'
            }),
            'winzerei': BusinessCategory('Winzerei', {
                'weingut', 'weinherstellung'
            }),
            'brauer': BusinessCategory('Brauer', {
                'brauerei', 'bierherstellung'
            }),
            'hotel': BusinessCategory('Hotel', {
                'beherbergungsbetrieb', 'hotellerie'
            }),
            'verlag': BusinessCategory('Verlag', {
                'buchverlag', 'verlagswesen'
            }),
            'druckerei': BusinessCategory('Druckerei', {
                'druckhaus', 'druckproduktion'
            }),
            'filmproduktion': BusinessCategory('Filmproduktion', {
                'videoproduktion', 'filmherstellung'
            }),
            'apotheke': BusinessCategory('Apotheke', {
                'pharmazie', 'medikamentenverkauf'
            }),
            'supermarkt': BusinessCategory('Supermarkt', {
                'lebensmittelgeschäft', 'einkaufsmarkt'
            }),
            'modegeschaeft': BusinessCategory('Modegeschäft', {
                'textilhandel', 'bekleidungsgeschäft'
            }),
            'blumenladen': BusinessCategory('Blumenladen', {
                'florist', 'blumengeschäft'
            }),
            'robotertechnik': BusinessCategory('Robotertechnik', {
                'robotik', 'industrieroboter'
            }),
            'automatisierung': BusinessCategory('Automatisierung', {
                'automatisierungssysteme', 'prozessautomation'
            }),
            'cnc_fertigung': BusinessCategory('CNC-Fertigung', {
                'cnc-bearbeitung', 'präzisionsfertigung'
            }),
            'pneumatik': BusinessCategory('Pneumatik', {
                'drucklufttechnik', 'pneumatikanlagen'
            }),
            'photovoltaik': BusinessCategory('Photovoltaik', {
                'solaranlagen', 'solarinstallation'
            }),
            'rehatechnik': BusinessCategory('Rehatechnik', {
                'rehabilitationstechnik', 'pflegehilfsmittel'
            }),
            'antriebstechnik': BusinessCategory('Antriebstechnik', {
                'getriebebau', 'antriebssteuerung'
            }),
            'gesundheitstechnik': BusinessCategory('Gesundheitstechnik', {
                'medizinprodukte', 'gesundheitsausrüstung'
            })
        }

        # List of German states for location matching
        self.german_states = {
            'baden-württemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
            'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
            'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
            'sachsen-anhalt', 'schleswig-holstein', 'thüringen'
        }

        # Precompile a list of all keywords and synonyms for fuzzy matching
        self.all_keywords = {}
        for category_id, category in self.categories.items():
            for keyword in category.keywords:
                self.all_keywords[keyword] = category_id

    def find_categories(self, text: str, threshold: int = 80) -> Set[str]:
        if pd.isna(text):
            return set()
        text = str(text).lower()
        found_categories = set()
        
        for keyword, category_id in self.all_keywords.items():
            # Use partial_ratio for flexibility
            if fuzz.partial_ratio(keyword, text) >= threshold:
                found_categories.add(category_id)
        
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
        
        # Initialize German stop words and stemmer
        self.german_stop_words = set(stopwords.words('german'))
        self.stemmer = SnowballStemmer('german')

    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent matching"""
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = re.sub(r'\d+', '', text)      # Remove numbers
        tokens = nltk.word_tokenize(text, language='german')
        tokens = [word for word in tokens if word not in self.german_stop_words]
        tokens = [self.stemmer.stem(word) for word in tokens]
        return ' '.join(tokens)

    def _get_buyer_text_content(self, record: Dict) -> str:
        """Extract and combine relevant text content from a buyer record"""
        fields = ['title', 'description', 'long_description']
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
        
        parts = re.split(r'[>/,\n]\s*', str(location))
        for part in parts:
            part = part.strip()
            if part in self.keyword_matcher.german_states:
                locations['states'].add(part)
            elif part:  # Any non-empty string that's not a state is considered a city
                city = re.sub(r'^region\s+', '', part)
                # Fuzzy match to known cities could be added here
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
                
            embedding1 = self.sentence_model.encode(text1, convert_to_tensor=False)
            embedding2 = self.sentence_model.encode(text2, convert_to_tensor=False)
            
            similarity = cosine_similarity(
                [embedding1],
                [embedding2]
            )[0][0]
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def find_matches(self, buyers_data: List[Dict], sellers_data: List[Dict], 
                    min_similarity: float = 0.75) -> List[Dict]:
        """Find matches between buyers and sellers"""
        matches = []
        seen_matches = set()  # Track unique matches
        
        # Precompute embeddings for all buyers and sellers
        logger.info("Precomputing embeddings for buyers and sellers...")
        buyer_texts = [self._get_buyer_text_content(b) for b in buyers_data]
        seller_texts = [self._get_seller_text_content(s) for s in sellers_data]
        buyer_embeddings = self.sentence_model.encode(buyer_texts, convert_to_tensor=False, show_progress_bar=True)
        seller_embeddings = self.sentence_model.encode(seller_texts, convert_to_tensor=False, show_progress_bar=True)
        logger.info("Embeddings precomputed successfully.")
        
        # Compute cosine similarity matrix
        logger.info("Calculating cosine similarity matrix...")
        similarity_matrix = cosine_similarity(buyer_embeddings, seller_embeddings)
        logger.info("Cosine similarity matrix calculated.")
        
        for buyer_idx, buyer in enumerate(buyers_data):
            buyer_text = buyer_texts[buyer_idx]
            buyer_categories = self.keyword_matcher.find_categories(buyer_text)
            
            for seller_idx, seller in enumerate(sellers_data):
                # Create unique match identifier using indices
                match_id = f"{buyer_idx}-{seller_idx}"
                if match_id in seen_matches:
                    continue
                
                # Check for category match
                seller_text = seller_texts[seller_idx]
                seller_categories = self.keyword_matcher.find_categories(seller_text)
                common_categories = buyer_categories.intersection(seller_categories)

                # Check location match
                has_location_match, matching_locations = self._check_location_match(
                    buyer.get('location', ''),
                    {'location': seller.get('location', ''), 'standort': seller.get('standort', '')}
                )
                
                if not has_location_match:
                    continue
                
                # Retrieve precomputed similarity score
                similarity = similarity_matrix[buyer_idx][seller_idx]
                if similarity < min_similarity:
                    continue
                
                match_info = {
                    'match_score': round(similarity, 3),
                    'matching_categories': sorted(common_categories),
                    'matching_locations': sorted(matching_locations),
                    'buyer_info': {
                        'date': buyer.get('date', ''),
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
                        'summary': seller.get('description', ''),
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
                    'Buyer Summary': match['buyer_info'].get('summary', ''),
                    'Buyer Description': match['buyer_info'].get('description', ''),
                    'Buyer Contact': match['buyer_info'].get('contact', ''),
                    'Seller Date': match['seller_info'].get('date', ''),
                    'Seller Location': match['seller_info'].get('location', ''),
                    'Seller Standort': match['seller_info'].get('standort', ''),
                    'Seller Title': match['seller_info'].get('title', ''),
                    'Seller Summary': match['seller_info'].get('summary', ''),
                    'Seller Description': match['seller_info'].get('long_description', ''),
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
