import requests
import json
from typing import Dict, List, Optional
import argparse

class RedmineTicketCreator:
    def __init__(self, redmine_url: str, api_key: str, project_id: int):
        """
        Initialisiert den Redmine Ticket Creator
        
        Args:
            redmine_url (str): Die URL der Redmine-Instanz
            api_key (str): Der API-Key für die Authentifizierung
            project_id (int): Die ID des Projekts
        """
        # Stelle sicher, dass die URL mit http:// oder https:// beginnt
        if not redmine_url.startswith(('http://', 'https://')):
            redmine_url = 'http://' + redmine_url
            
        self.redmine_url = redmine_url.rstrip('/')
        self.api_key = api_key
        self.project_id = project_id
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
            response = requests.get(f"{self.redmine_url}/projects/{self.project_id}.json", 
                                  headers=self.headers)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Fehler bei der Verbindung zu Redmine: {e}")
            return False

    def create_ticket(self, subject: str, description: str, tracker_id: int, 
                     priority_id: int = 2, status_id: int = 1) -> Dict:
        """
        Erstellt ein neues Ticket in Redmine
        
        Args:
            subject (str): Der Titel des Tickets
            description (str): Die Beschreibung des Tickets
            tracker_id (int): Die ID des Trackers (z.B. Feature, Bug, etc.)
            priority_id (int): Die Priorität (Standard: 2 = Normal)
            status_id (int): Der Status (Standard: 1 = Neu)
            
        Returns:
            Dict: Die Antwort von Redmine
        """
        url = f"{self.redmine_url}/issues.json"
        
        data = {
            "issue": {
                "project_id": self.project_id,
                "subject": subject,
                "description": description,
                "tracker_id": tracker_id,
                "priority_id": priority_id,
                "status_id": status_id
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Erstellen des Tickets: {e}")
            return {"error": str(e)}

    def create_tickets_from_concept(self, concept_file: str, tracker_id: int = 1):
        """
        Erstellt Tickets basierend auf dem Konzept-Dokument
        
        Args:
            concept_file (str): Pfad zur Konzept-Datei
            tracker_id (int): Die ID des Trackers für die Tickets
        """
        # Teste zuerst die Verbindung
        if not self.test_connection():
            print("Konnte keine Verbindung zu Redmine herstellen. Bitte überprüfen Sie URL und API-Key.")
            return

        try:
            with open(concept_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Konzept-Datei nicht gefunden: {concept_file}")
            return
            
        # Teile den Inhalt in Abschnitte
        sections = content.split('###')
        
        for section in sections[1:]:  # Überspringe die erste leere Sektion
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            # Extrahiere den Titel und das Level
            title_line = lines[0]
            title = title_line.split('(')[0].strip()
            try:
                level = int(title_line.split('Level ')[1].split(')')[0])
            except (IndexError, ValueError):
                print(f"Konnte Level nicht aus Zeile extrahieren: {title_line}")
                continue
            
            # Erstelle das Ticket
            description = f"Level: {level}\n\n"
            description += "Unterpunkte:\n"
            
            for line in lines[1:]:
                if line.strip() and not line.startswith('  - **'):
                    description += f"- {line.strip()}\n"
            
            print(f"Erstelle Ticket: {title}")
            response = self.create_ticket(
                subject=title,
                description=description,
                tracker_id=tracker_id,
                priority_id=self._get_priority_from_level(level)
            )
            
            if "error" in response:
                print(f"Fehler beim Erstellen des Tickets '{title}': {response['error']}")
            else:
                print(f"Ticket erstellt: {response.get('issue', {}).get('id')}")

    def _get_priority_from_level(self, level: int) -> int:
        """
        Konvertiert das Level in eine Redmine-Priorität
        
        Args:
            level (int): Das Level aus dem Konzept
            
        Returns:
            int: Die entsprechende Redmine-Prioritäts-ID
        """
        if level >= 18:
            return 5  # Sofort
        elif level >= 15:
            return 4  # Hoch
        elif level >= 12:
            return 3  # Normal
        elif level >= 9:
            return 2  # Niedrig
        else:
            return 1  # Sehr niedrig

def main():
    parser = argparse.ArgumentParser(description='Erstellt Redmine-Tickets aus einem Konzept-Dokument')
    parser.add_argument('--url', required=True, help='Redmine URL')
    parser.add_argument('--api-key', required=True, help='Redmine API Key')
    parser.add_argument('--project-id', required=True, type=int, help='Redmine Projekt ID')
    parser.add_argument('--concept-file', required=True, help='Pfad zur Konzept-Datei')
    parser.add_argument('--tracker-id', type=int, default=1, help='Tracker ID (Standard: 1)')
    
    args = parser.parse_args()
    
    creator = RedmineTicketCreator(args.url, args.api_key, args.project_id)
    creator.create_tickets_from_concept(args.concept_file, args.tracker_id)

if __name__ == "__main__":
    main() 