import pandas as pd
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import csv

def parse_seller_data(text):
    """Parse the raw seller data text into a structured format."""
    sellers = []
    current_seller = {}
    
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('**'):  # Date line
            if current_seller:
                sellers.append(current_seller)
            current_seller = {'date': line.strip('*')}
        elif ':' in line and not line.startswith('http'):
            key, value = line.split(':', 1)
            current_seller[key.strip()] = value.strip()
        elif line:  # Additional information
            if 'description' not in current_seller:
                current_seller['description'] = line
            else:
                current_seller['description'] += ' ' + line
    
    if current_seller:
        sellers.append(current_seller)
    
    return pd.DataFrame(sellers)

def parse_buyer_data(text):
    """Parse the raw buyer data text into a structured format."""
    buyers = []
    lines = text.strip().split('\n')
    
    for line in lines:
        if line.startswith('**'):
            # Parse header line to get column names
            headers = line.strip('*').split()
            continue
            
        if not line.strip():
            continue
            
        # Split the line by probable delimiters
        parts = re.split(r'(?<=[A-Za-z])\s+(?=[0-9])|(?<=[0-9])\s+(?=[A-Za-z])', line)
        if len(parts) >= 6:  # Ensure we have all required fields
            buyer = {
                'date': parts[0],
                'location': parts[1],
                'title': parts[2],
                'summary': parts[3],
                'description': parts[4],
                'source': parts[5] if len(parts) > 5 else '',
                'contact': parts[6] if len(parts) > 6 else ''
            }
            buyers.append(buyer)
    
    return pd.DataFrame(buyers)

class BusinessMatcher:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        # Get German stopwords
        self.stop_words = set(stopwords.words('german'))
        
        # Define state mappings for partial matches
        self.state_mappings = {
            'baden-württemberg': ['baden-württemberg', 'baden württemberg', 'baden-wuerttemberg', 'baden'],
            'bayern': ['bayern', 'bavaria'],
        }

    def preprocess_text(self, text):
        """Preprocesses text by converting to lowercase, removing special characters."""
        if pd.isna(text):
            return ""
        text = str(text).lower()
        # Preserve German umlauts and ß while removing other special characters
        text = re.sub(r'[^a-zäöüß\s]', ' ', text)
        tokens = word_tokenize(text)
        tokens = [w for w in tokens if w not in self.stop_words]
        return ' '.join(tokens)

    def normalize_state(self, state):
        """Normalizes state names to handle different writings."""
        if pd.isna(state):
            return ""
        state = str(state).lower()
        for standard, variants in self.state_mappings.items():
            if state in variants:
                return standard
        return state

    def calculate_location_match(self, seller_location, buyer_location):
        """Calculate location match score."""
        try:
            seller_states = set(self.normalize_state(s.strip()) 
                              for s in str(seller_location).split())
            buyer_states = set(self.normalize_state(s.strip()) 
                             for s in str(buyer_location).split())
            
            if not seller_states or not buyer_states:
                return 0.0
                
            matching_states = seller_states.intersection(buyer_states)
            return len(matching_states) / max(len(seller_states), len(buyer_states))
        except Exception as e:
            print(f"Error in location matching: {e}")
            return 0.0

    def calculate_keyword_match(self, seller_text, buyer_text):
        """Calculate keyword matching score using text similarity."""
        try:
            seller_processed = set(self.preprocess_text(seller_text).split())
            buyer_processed = set(self.preprocess_text(buyer_text).split())
            
            if not seller_processed or not buyer_processed:
                return 0.0
                
            common_words = seller_processed.intersection(buyer_processed)
            return len(common_words) / max(len(seller_processed), len(buyer_processed))
        except Exception as e:
            print(f"Error in keyword matching: {e}")
            return 0.0

    def match_businesses(self, sellers_df, buyers_df, min_score=0.1):
        """Match sellers with potential buyers based on location and keywords."""
        matches = []
        
        for _, seller in sellers_df.iterrows():
            seller_description = ' '.join(filter(None, [
                str(seller.get('description', '')),
                str(seller.get('Erste Infos', '')),
                str(seller.get('Besonderheiten', ''))
            ]))
            seller_location = seller.get('location', '')
            
            for _, buyer in buyers_df.iterrows():
                buyer_description = ' '.join(filter(None, [
                    str(buyer.get('title', '')),
                    str(buyer.get('summary', '')),
                    str(buyer.get('description', ''))
                ]))
                buyer_location = buyer.get('location', '')
                
                location_score = self.calculate_location_match(seller_location, buyer_location)
                keyword_score = self.calculate_keyword_match(seller_description, buyer_description)
                
                total_score = (location_score * 0.6) + (keyword_score * 0.4)
                
                if total_score >= min_score:
                    matches.append({
                        'match_score': total_score,
                        'seller_date': seller.get('date', ''),
                        'buyer_date': buyer.get('date', ''),
                        'seller_description': seller_description[:100] + '...',
                        'buyer_description': buyer_description[:100] + '...',
                        'location_score': location_score,
                        'keyword_score': keyword_score,
                        'buyer_contact': buyer.get('contact', '')
                    })
        
        matches_df = pd.DataFrame(matches)
        if not matches_df.empty:
            matches_df = matches_df.sort_values('match_score', ascending=False)
        
        return matches_df

def main():
    # Example seller data
    seller_text = """**25.10.2024**
Roboter- & Antriebstechnik, Sondermaschinenbau - GmbH zu verkaufen
Das Unternehmen bietet seit ca. 35 Jahren individuelle Lösungen rund um Antriebstechnik, Robotertechnik, Sondermaschinenbau, Schaltschrankbau, Softwaresteuerung und Wartung + Instandhaltung.
location: Baden-Württemberg"""  # Your actual seller data here

    # Example buyer data
    buyer_text = """**26.9.2024**Baden-Württemberg Bayern**Matthias ist Sachverständiger für Gebäudetechnik und sucht in Baden Württemberg oder Bayern eine Elektroinstallationsfirma oder ein Ingeunierbüro für Gebäudetechnik.**Ich bin Sachverständiger für Gebäudetechnik und Vorbeugender Brandschutz, SiGe, Sicherheitsbeauftragter, Gefahrgutbeauftragter, SiFa und Suche ein geeignetes Unternehmen in der Region Baden - Württemberg und Bayern zu übernehmen. Ingenieurbüro oder Elektroinstallationsfirma. Beteiligung oder Übernahme. Bis 1 Mio €**dejuna**Matthias Haamann 0176-41552292 haamann-matthias@mail.de"""  # Your actual buyer data here

    # Parse the data
    sellers_df = parse_seller_data(seller_text)
    buyers_df = parse_buyer_data(buyer_text)
    
    # Create matcher and find matches
    matcher = BusinessMatcher()
    matches = matcher.match_businesses(sellers_df, buyers_df, min_score=0.2)
    
    # Print results
    if not matches.empty:
        print("\nMatches found:")
        for _, match in matches.iterrows():
            print(f"\nMatch Score: {match['match_score']:.2f}")
            print(f"Location Score: {match['location_score']:.2f}")
            print(f"Keyword Score: {match['keyword_score']:.2f}")
            print(f"Seller Description: {match['seller_description']}")
            print(f"Buyer Description: {match['buyer_description']}")
            print(f"Buyer Contact: {match['buyer_contact']}")
    else:
        print("No matches found.")

if __name__ == "__main__":
    main()