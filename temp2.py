import pandas as pd

# Creating a dictionary to simulate the structure of the provided CSV data with additional keywords and synonyms.
data = {
    "Keyword": ["Tischlerei", "Zimmerei", "Hausverwaltung", "Pension", "Gebäudereinigung", "Textilreinigung", "Heizung Sanitär", "Elektrofirma", 
                "Dachdeckerei", "Malerfirma", "Metallbau", "Schlosserei", "Bauunternehmen", "Maschinenbau", "Gartenbaubetrieb", "Glaserei", 
                "Behälterbau", "Tankschutz", "Oberflächenbeschichtung", "Steinmetzbetrieb", "Hausmeisterservice", "Pflegedienst", 
                "Sanitätshaus", "Zahnarztpraxis", "Arztpraxis", "Tierarztpraxis", "Rechtsanwaltskanzlei", "Steuerberatung", 
                "Notariat", "Architekturbüro", "Ingenieurbüro", "Fotostudio", "Kosmetikstudio", "Friseursalon", "Reisebüro", 
                "Musikschule", "Fitnessstudio", "Kunstgalerie", "Landwirtschaft", "Bäckerei", "Metzgerei", "Winzerei", "Brauer", 
                "Hotel", "Verlag", "Druckerei", "Filmproduktion", "Apotheke", "Supermarkt", "Modegeschäft", "Blumenladen"],
    "Synonym 1": ["Schreinerei", "Zimmerer", "Immobilienverwaltung", "Frühstückspension", "Reinigungsfirma", "Wäscherei", "Heizungsbau", "Elektrobetrieb", 
                  "Dachdeckerbetrieb", "Malerbetrieb", "Metallbaufirma", "Schlosser", "Baufirma", "Maschinenbaufirma", "Gartenbaufirma", "Glaser", 
                  "Behälteranlagen", "Tank-Wartung", "Oberflächenschutz", "Steinmetz", "Hausmeisterfirma", "Ambulanter Pflegedienst", 
                  "Orthopädietechnik", "Zahnarzt", "Arzt", "Tierarzt", "Anwaltskanzlei", "Steuerberater", 
                  "Notar", "Architekt", "Engineering", "Fotograf", "Beauty Salon", "Haarstudio", "Reisedienstleistungen", 
                  "Musikunterricht", "Gym", "Galerie", "Bauernhof", "Bäcker", "Fleischerei", "Weingut", "Brauerei", 
                  "Unterkunft", "Buchverlag", "Druckhaus", "Videoproduktion", "Pharmazie", "Lebensmittelgeschäft", "Boutique", "Florist"],
    "Synonym 2": ["Möbelbau", "Holzbau", "Mietsverwaltung", "Herberge", "Facility Management", "Chemische Reinigung", "SHK", "Elektrotechnik", 
                  "Dachdeckerfirma", "Maler", "Metallbaubetrieb", "Metallverarbeitung", "Bauträger", "Maschinenbauer", "Gartenbauunternehmen", "Glasbau", 
                  "Industriebehälter", "Tank-Reinigung", "Lackierung", "Natursteinbetrieb", "Hausmeister", "Krankenpflege", 
                  "Rehatechnik", "Dentalpraxis", "Medizinische Praxis", "Veterinärmedizin", "Rechtsberatung", "Fiscalberatung", 
                  "Beurkundung", "Planungsbüro", "Baustatik", "Fotoatelier", "Schönheitspflege", "Coiffeur", "Urlaubsplanung", 
                  "Instrumentalunterricht", "Fitnesstraining", "Kunsthandel", "Agrarbetrieb", "Brotproduktion", "Fleischwaren", "Weinbau", "Bierherstellung", 
                  "Beherbergungsbetrieb", "Zeitschriftenverlag", "Printservice", "Filmstudio", "Medikamentenverkauf", "Einkaufsmarkt", "Fashion Store", "Blumengeschäft"],
    "Synonym 3": ["Tischlermeister", "Dachstuhl", "WEG Verwaltung", "Boutique Hotel", "Putzdienst", "Bügelservice", "Heizung Sanitär Klima", "Elektroinstallation", 
                  "Dachdeckermeister", "Malermeister", "Metallbauer", "Stahlbau", "Baumeister", "Anlagenbau", "Garten- und Landschaftsbau", "Fensterbau", 
                  "Behälterbeschichtung", "Tank-Instandhaltung", "Beschichtungstechnik", "Grabsteine", "Gebäudeservice", "Altenpflege", 
                  "Medizintechnik", "Mundhygiene", "Allgemeinmedizin", "Tierklinik", "Juridische Dienste", "Buchprüfung", 
                  "Beglaubigung", "Bauplanung", "Bauingenieurwesen", "Portraitfotografie", "Kosmetikerin", "Haarpflege", "Travel Agency", 
                  "Musikakademie", "Sportstudio", "Kunstverkauf", "Agrarwirtschaft", "Konditorei", "Wurstherstellung", "Weinherstellung", "Bierbrauerei", 
                  "Gastgewerbe", "Verlagswesen", "Druckservice", "Filmgesellschaft", "Pharmazeutika", "Konsum", "Textilhandel", "Blumenhandel"],
    "Synonym 4": ["Schreinermeister", "Zimmermann", "Property Management", "Gästehaus", "Hausreinigung", "Laundry Service", "Sanitär Heizung Klima", "Elektromeister", 
                  "Dacharbeiten", "Anstrich", "Metallbauunternehmen", "Geländerbau", "Bauhandwerk", "Engineering", "Gärtnerei", "Spiegelherstellung", 
                  "Tankbau", "Tank-Reparatur", "Galvanik", "Marmorarbeiten", "Facility Service", "Pflegeheim", 
                  "Homecare", "Kieferorthopädie", "Facharztpraxis", "Veterinärpraxis", "Anwalt", "Steuerkanzlei", 
                  "Notariatskanzlei", "Architekturdesign", "Technisches Büro", "Werbefotografie", "Wellnessstudio", "Friseurmeister", "Reisevermittlung", 
                  "Musikpädagogik", "Wellnesscenter", "Ausstellungsraum", "Landwirt", "Backwaren", "Schlachterei", "Kellerei", "Braukunst", 
                  "Hotellerie", "Publikationshaus", "Druckproduktion", "Filmherstellung", "Drogerie", "Biomarkt", "Bekleidungsgeschäft", "Gärtnerei"],
    "Synonym 5": ["Möbelwerkstatt", "Dachdecker", "Immobilienmanagement", "Ferienhaus", "Reinigungsservice", "Kleiderreinigung", "Installateur", "elektrotechnikermeister", 
                  "Dachsanierung", "Renovierung", "Metallbaumeister", "Schlossermeister", "Baugeschäft", "Industrietechnik", "Landschaftsbau", "Glasbauunternehmen", 
                  "Tankherstellung", "Tank-Installation", "Beschichtungsservice", "Steinbildhauer", "Gebäudemanagement", "Betreuung", 
                  "Gesundheitstechnik", "Zahnmedizin", "Mediziner", "Tiermedizin", "Rechtsanwalt", "Tax Consulting", 
                  "Notariatsservice", "Bauzeichner", "Planungsingenieur", "Bildbearbeitung", "Nagelstudio", "Haarmode", "Reiseberatung", 
                  "Musikzentrum", "Fitnessclub", "Kunstvermittlung", "Ackerbau", "Bäckereibetrieb", "Metzger", "Weinproduktion", "Bierproduktion", 
                  "Hospiz", "Medienhaus", "Druckbetrieb", "Medienproduktion", "Apothekenbetrieb", "Einkaufszentrum", "Modegeschäft", "Blumenfachgeschäft"]
}

# Convert the dictionary to a DataFrame
df = pd.DataFrame(data)

# Save DataFrame as CSV file
file_path = "Updated_Keywords_and_Synonyms.csv"
df.to_csv(file_path, index=False)

file_path
