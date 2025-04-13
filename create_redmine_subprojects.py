import requests
import json
from typing import Dict, List
import os

# Konfiguration
REDMINE_URL = "localhost:3001"
API_KEY = "bdb603c145309dcc113fba3674726bcf74a6812e"
PARENT_PROJECT_IDENTIFIER = "mixxx-dj-software"
CONCEPT_FILE = "../mixxx/01_DJ_Session_Konzept.emu"

class RedmineSubprojectCreator:
    def __init__(self, redmine_url: str, api_key: str, parent_project_identifier: str):
        """
        Initialisiert den Redmine Subproject Creator
        
        Args:
            redmine_url (str): Die URL der Redmine-Instanz
            api_key (str): Der API-Key für die Authentifizierung
            parent_project_identifier (str): Der Identifier des Elternprojekts
        """
        if not redmine_url.startswith(('http://', 'https://')):
            redmine_url = 'http://' + redmine_url
            
        self.redmine_url = redmine_url.rstrip('/')
        self.api_key = api_key
        self.parent_project_identifier = parent_project_identifier
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
            response = requests.get(f"{self.redmine_url}/projects/{self.parent_project_identifier}.json", 
                                  headers=self.headers)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Fehler bei der Verbindung zu Redmine: {e}")
            return False

    def create_subproject(self, name: str, level: int) -> Dict:
        """
        Erstellt ein neues Unterprojekt in Redmine
        
        Args:
            name (str): Der Name des Unterprojekts
            level (int): Das Level aus dem Konzept (für die Beschreibung)
            
        Returns:
            Dict: Die Antwort von Redmine
        """
        # Erstelle einen gültigen Identifier aus dem Namen
        identifier = name.lower().replace(' ', '-').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
        identifier = ''.join(c for c in identifier if c.isalnum() or c == '-')
        identifier = f"{self.parent_project_identifier}-{identifier}"
        
        url = f"{self.redmine_url}/projects.json"
        
        data = {
            "project": {
                "name": name,
                "identifier": identifier[:100],  # Redmine limitiert Identifier auf 100 Zeichen
                "description": f"Prioritätslevel: {level}\nTeilprojekt von: {self.parent_project_identifier}",
                "parent_id": self.parent_project_identifier,
                "inherit_members": True,
                "is_public": False
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Erstellen des Unterprojekts: {e}")
            return {"error": str(e)}

    def extract_sections_from_concept(self, concept_file: str) -> List[Dict[str, int]]:
        """
        Extrahiert die Abschnitte und deren Level aus der Konzept-Datei
        
        Args:
            concept_file (str): Pfad zur Konzept-Datei
            
        Returns:
            List[Dict[str, int]]: Liste der gefundenen Abschnitte mit Namen und Level
        """
        try:
            with open(concept_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Konzept-Datei nicht gefunden: {concept_file}")
            return []

        sections = []
        for line in content.split('\n'):
            if line.startswith('### '):
                # Extrahiere den Namen ohne die Nummerierung
                name = line.replace('### ', '')
                name = ' '.join(name.split(' ')[1:])  # Entferne die Nummerierung
                
                # Extrahiere das Level
                level = int(name.split('(Level ')[1].split(')')[0])
                
                # Entferne den Level-Teil vom Namen
                name = name.split(' (Level')[0].strip()
                
                sections.append({"name": name, "level": level})
                
        return sections

    def create_subprojects_from_concept(self, concept_file: str):
        """
        Erstellt Unterprojekte basierend auf dem Konzept-Dokument
        
        Args:
            concept_file (str): Pfad zur Konzept-Datei
        """
        if not self.test_connection():
            print("Konnte keine Verbindung zu Redmine herstellen. Bitte überprüfen Sie URL und API-Key.")
            return

        sections = self.extract_sections_from_concept(concept_file)
        
        if not sections:
            print("Keine Abschnitte im Konzept gefunden.")
            return
            
        print(f"Gefundene Abschnitte: {len(sections)}")
        print("\nGefundene Abschnitte:")
        for i, section in enumerate(sections, 1):
            print(f"{i}. {section['name']} (Level {section['level']})")
            
        print("\nErstelle Unterprojekte...")
        for section in sections:
            print(f"\nErstelle Unterprojekt: {section['name']} (Level {section['level']})")
            response = self.create_subproject(section['name'], section['level'])
            
            if "error" in response:
                print(f"Fehler beim Erstellen des Unterprojekts '{section['name']}': {response['error']}")
            else:
                print(f"Unterprojekt erstellt: {response.get('project', {}).get('name')}")

if __name__ == "__main__":
    # Passe den relativen Pfad an, wenn das Skript aus einem anderen Verzeichnis ausgeführt wird
    script_dir = os.path.dirname(os.path.abspath(__file__))
    concept_file_path = os.path.join(os.path.dirname(script_dir), "mixxx", "01_DJ_Session_Konzept.emu")
    
    creator = RedmineSubprojectCreator(REDMINE_URL, API_KEY, PARENT_PROJECT_IDENTIFIER)
    creator.create_subprojects_from_concept(concept_file_path) 