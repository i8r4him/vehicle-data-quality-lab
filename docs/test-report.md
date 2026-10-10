# Prüfbericht – Testautomatisierung

Stand: 10.10.2026, Europe/Berlin.

## Ergänzungen

- Acht ausführbare Gherkin-Abnahmeszenarien mit Behave: CSV, XLSX, vier Fehlerarten, Versionskonflikt und Wiederholungsschutz.
- Sechs zusätzliche Regeltests mit 32 Varianten für Preise, Laufzeiten, Fahrleistung, IDs, Produkte und Datenstände.
- Jenkins-Pipeline mit virtueller Python-Umgebung, JUnit-Auswertung und archivierten Demoergebnissen.
- GitHub Actions um Abnahmetests und herunterladbare Ergebnisartefakte ergänzt.
- User Stories mit ausführbaren Szenarien verknüpft; Ablauf einer Regelpflege in `testing.md` beschrieben.

## Lokale Ergebnisse

Python 3.12.14, Behave 1.3.3, unittest-xml-reporting 3.2.0, openpyxl 3.1.5.

| Prüfung | Ergebnis |
| --- | --- |
| Bestehende und neue Python-Tests | 30 erfolgreich, keine Fehler |
| Gherkin-Abnahme | 8 Szenarien / 44 Schritte erfolgreich, nichts übersprungen |
| Demo | Fehlerhafte Datei abgelehnt; korrigierte CSV angenommen; XLSX ohne weitere Änderung; identische CSV übersprungen |
| Manuelle KI-Review-Demo | Gespeicherte Beispielantwort strukturell gültig; menschliche Prüfung weiterhin offen |
| Abhängigkeiten (`pip check`) | Keine Konflikte |

## Jenkins-Nachweis

Die Pipeline wurde auf einer temporären lokalen Jenkins-Instanz **ausgeführt**, aus einem lokalen Git-Prüfstand ausgecheckt und als Build `vehicle-data-checks #1` mit **SUCCESS** abgeschlossen. Umgebung: Jenkins 2.580.1, Temurin Java 21.0.10, Python 3.12.14. JUnit hat 38 Testfälle erfasst. XML-Ergebnisse, Excel-Bericht, SQL-CSV-Auswertungen und JSON-Demoergebnisse wurden als Build-Artefakte gespeichert.

Die Instanz dient nur diesem Prüflauf und ist kein dauerhaft eingerichteter CI-Server. Der `Jenkinsfile` kann über einen eigenen Jenkins-Pipeline-Job verwendet werden; Einrichtung siehe `testing.md`.

## GitHub

Die Workflow-Matrix prüft Python 3.10 und 3.13. Die Ergebnisse des gepushten Commits und die zugehörigen Artefakte sind unter [GitHub Actions](https://github.com/i8r4him/vehicle-data-quality-lab/actions/workflows/tests.yml) abrufbar. Der obige Jenkins-Nachweis bezieht sich auf den lokalen Prüflauf.

Die Erweiterung betrifft Testautomatisierung und Dokumentation. Fachregeln und Produktionscode wurden nicht geändert. Es wurde keine Jira-Anbindung, medizinische Bewertung oder Java-Implementierung hinzugefügt.
