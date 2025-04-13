import requests
import json
from typing import Dict, List
import os

# Konfiguration
REDMINE_URL = "localhost:3001"
API_KEY = "bdb603c145309dcc113fba3674726bcf74a6812e"
PROJECT_IDENTIFIER = "mixxx-dj-software"  # Projekt-Identifier statt ID
CONCEPT_FILE = "../mixxx/01_DJ_Session_Konzept.emu"

class RedmineCategoryCreator:
    def __init__(self, redmine_url: str, api_key: str, project_identifier: str):
        """
        Initialisiert den Redmine Category Creator
        
        Args:
            redmine_url (str): Die URL der Redmine-Instanz
            api_key (str): Der API-Key für die Authentifizierung
            project_identifier (str): Der Identifier des Projekts (z.B. 'mixxx-dj-software')
        """
        if not redmine_url.startswith(('http://', 'https://')):
            redmine_url = 'http://' + redmine_url
            
        self.redmine_url = redmine_url.rstrip('/')
        self.api_key = api_key
        self.project_identifier = project_identifier
        self.headers = {
            'X-Redmine-API-Key': api_key,
            'Content-Type': 'application/json'
        }

    def test_connection(self) -> bool:
        """
        Testet die Verbindung zur Redmine-Instanz
        
        Returns:
            bool: True wenn die Verbindung erfolgreich ist
        """
        try:
            response = requests.get(f"{self.redmine_url}/projects/{self.project_identifier}.json", 
                                  headers=self.headers)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Fehler bei der Verbindung zu Redmine: {e}")
            return False

    def create_category(self, name: str) -> Dict:
        """
        Erstellt eine neue Kategorie in Redmine
        
        Args:
            name (str): Der Name der Kategorie
            
        Returns:
            Dict: Die Antwort von Redmine
        """
        url = f"{self.redmine_url}/projects/{self.project_identifier}/issue_categories.json"
        
        data = {
            "issue_category": {
                "name": name
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Erstellen der Kategorie: {e}")
            return {"error": str(e)}

    def extract_categories_from_concept(self, concept_file: str) -> List[str]:
        """
        Extrahiert die Kategorien aus der Konzept-Datei
        
        Args:
            concept_file (str): Pfad zur Konzept-Datei
            
        Returns:
            List[str]: Liste der gefundenen Kategorien
        """
        try:
            with open(concept_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Konzept-Datei nicht gefunden: {concept_file}")
            return []

        # Suche nach ### Überschriften und extrahiere den Namen (ohne Level)
        categories = []
        for line in content.split('\n'):
            if line.startswith('### '):
                # Extrahiere den Namen ohne die Level-Angabe und die Nummerierung
                category_name = line.replace('### ', '')
                # Entferne die Nummerierung (z.B. "1. " oder "10. ")
                category_name = ' '.join(category_name.split(' ')[1:])
                # Entferne den Level
                category_name = category_name.split(' (Level')[0].strip()
                categories.append(category_name)
                
        return categories

    def create_categories_from_concept(self, concept_file: str):
        """
        Erstellt Kategorien basierend auf dem Konzept-Dokument
        
        Args:
            concept_file (str): Pfad zur Konzept-Datei
        """
        if not self.test_connection():
            print("Konnte keine Verbindung zu Redmine herstellen. Bitte überprüfen Sie URL und API-Key.")
            return

        categories = self.extract_categories_from_concept(concept_file)
        
        if not categories:
            print("Keine Kategorien im Konzept gefunden.")
            return
            
        print(f"Gefundene Kategorien: {len(categories)}")
        print("\nGefundene Kategorien:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
            
        print("\nErstelle Kategorien...")
        for category in categories:
            print(f"\nErstelle Kategorie: {category}")
            response = self.create_category(category)
            
            if "error" in response:
                print(f"Fehler beim Erstellen der Kategorie '{category}': {response['error']}")
            else:
                print(f"Kategorie erstellt: {response.get('issue_category', {}).get('name')}")

if __name__ == "__main__":
    # Passe den relativen Pfad an, wenn das Skript aus einem anderen Verzeichnis ausgeführt wird
    script_dir = os.path.dirname(os.path.abspath(__file__))
    concept_file_path = os.path.join(os.path.dirname(script_dir), "mixxx", "01_DJ_Session_Konzept.emu")
    
    creator = RedmineCategoryCreator(REDMINE_URL, API_KEY, PROJECT_IDENTIFIER)
    creator.create_categories_from_concept(concept_file_path) 