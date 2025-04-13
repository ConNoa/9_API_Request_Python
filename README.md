API Key 
bdb603c145309dcc113fba3674726bcf74a6812e


Projektlink
http://localhost:3001/projects/mixxx-dj-software



# Redmine Ticket Creator

Dieses Python-Skript erstellt automatisch Tickets in Redmine basierend auf einem Konzept-Dokument.

## Voraussetzungen

- Python 3.6 oder höher
- Die `requests` Bibliothek (`pip install requests`)

## Verwendung

Das Skript kann wie folgt ausgeführt werden:

```bash
python create_redmine_tickets.py --url "http://localhost:3001/" \
                                --api-key "IHR_API_KEY" \
                                --project-id 123 \
                                --concept-file "pfad/zur/konzept-datei.emu" \
                                --tracker-id 1
```

### Parameter

- `--url`: Die URL Ihrer Redmine-Instanz
- `--api-key`: Ihr Redmine API-Key
- `--project-id`: Die ID des Projekts, in dem die Tickets erstellt werden sollen
- `--concept-file`: Der Pfad zur Konzept-Datei
- `--tracker-id`: Die ID des Trackers für die Tickets (optional, Standard: 1)

## Funktionsweise

Das Skript:
1. Liest die Konzept-Datei ein
2. Extrahiert die Hauptabschnitte und deren Level
3. Erstellt für jeden Abschnitt ein Ticket
4. Setzt die Priorität basierend auf dem Level
5. Fügt die Unterpunkte als Beschreibung hinzu

## Prioritätszuordnung

- Level ≥ 18: Sofort (5)
- Level ≥ 15: Hoch (4)
- Level ≥ 12: Normal (3)
- Level ≥ 9: Niedrig (2)
- Level < 9: Sehr niedrig (1)

## Beispiel

```bash
python create_redmine_tickets.py --url "http://localhost:3000" \
                                --api-key "1234567890abcdef" \
                                --project-id 1 \
                                --concept-file "../mixxx/01_DJ_Session_Konzept.emu" \
                                --tracker-id 1
```

## Fehlerbehandlung

Das Skript gibt Fehlermeldungen aus, wenn:
- Die Redmine-URL nicht erreichbar ist
- Der API-Key ungültig ist
- Die Projekt-ID nicht existiert
- Die Konzept-Datei nicht gefunden werden kann 