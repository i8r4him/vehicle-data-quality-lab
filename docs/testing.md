# Tests und Regelpflege

Die Anwendung bleibt ein Python-/SQLite-Projekt mit synthetischen Fahrzeugdaten. Die Erweiterung ergänzt ausführbare Abnahmekriterien und eine zweite CI-Variante.

Der [Prüfbericht](test-report.md) hält den lokalen Test- und Jenkins-Lauf fest.

## Lokal prüfen

Nach dem Anlegen und Aktivieren der virtuellen Umgebung:

```bash
python -m pip install -r requirements-dev.txt
python -m xmlrunner discover -s tests -o reports/unit -v
python -m behave --junit --junit-directory reports/acceptance
```

`unittest` enthält Integrations-, Regressions- und Regeltests. Behave führt die Gherkin-Szenarien gegen dieselbe Anwendung und echte temporäre SQLite-Datenbanken aus. Jedes Szenario bekommt eine frische Datenbank; nachher wird sie entfernt. Die Szenarien verwenden englische Gherkin-Schlüsselwörter und deutsche Fachtexte. Behave ist der Python-Testläufer; Cucumber selbst ist keine Projektabhängigkeit.

## Was wird geprüft?

| Anforderung | Nachweis |
| --- | --- |
| US1: CSV und XLSX korrekt übernehmen | Gherkin-Szenarien mit gespeichertem Centbetrag und Änderungshistorie |
| US1: Eine schlechte Zeile lehnt die ganze Datei ab | Vier Gherkin-Beispiele: VALUE, REQUIRED, DUPLICATE, FOREIGN_KEY; Bestand bleibt unverändert |
| US1: Änderungen brauchen einen neueren Datenstand | STALE_UPDATE-Szenario und `test_update_date_regression` |
| US2: Derselbe Import darf nichts doppelt schreiben | Gherkin-Szenario mit genau einem Import und einer Änderung |
| US3: Auswertungen und Berichte bleiben korrekt | Bestehende SQL-, Excel- und Demo-Integrationstests |
| VALUE: Preis bleibt centgenau und im Wertebereich | 0, 0.001, 0.01, 10.000.000 und 10.000.000,01 EUR |
| VALUE: Laufzeit und Fahrleistung sind begrenzt | Laufzeit 0/1/120/121; Fahrleistung 0/1/200000/200001; zusätzlich Bruchteile, NaN und Infinity |
| VALUE: Angebots-ID und Produkt sind gültig | ID-Länge 1/40/41, ungültige Zeichen und Produktwerte |

## Beispiel für eine Regelpflege

**Anforderung:** US1 erlaubt Laufzeiten von 1 bis 120 Monaten einschließlich. 0 und 121 Monate werden abgelehnt. In einer gemischten Datei darf kein Angebot teilweise übernommen werden.

**Umsetzung:** `validate()` in `vehicle_data_quality/pipeline.py` prüft die Laufzeit. Die neuen Grenzwerttests sichern die bereits vorhandene Regel ab; sie verändern den zulässigen Bereich nicht.

**Abnahme:** `test_term_boundaries` prüft beide Grenzen und deren Nachbarwerte. Das Gherkin-Szenario zur vollständigen Ablehnung und `test_mixed_file_cannot_partially_apply` sichern das Verhalten einer gemischten Datei.

Wenn sich eine Fachregel später ändert: zuerst die neue Erwartung als Test ergänzen, dann die Prüfung anpassen und die gesamte Testsuite laufen lassen. Anforderung, Änderung und Prüfergebnis gehören zusammen in den Commit oder ein Issue. Die Zuordnung ist hier in Markdown dokumentiert; eine Jira-Anbindung wurde nicht eingerichtet.

## Jenkins einrichten

Voraussetzungen: Unix-Agent mit `python3` ab Version 3.10, `venv`, Git und Paketzugriff. Jenkins braucht Pipeline-, Git- und JUnit-Plugins. Java-Version und Jenkins-Version müssen zueinander passen. Die Schritte benötigen weder Docker noch API-Schlüssel.

1. Pipeline-Job anlegen, „Pipeline script from SCM“ wählen.
2. Git-Repository `https://github.com/i8r4him/vehicle-data-quality-lab.git`, Branch `*/main`, Script Path `Jenkinsfile` eintragen.
3. Build starten. Jenkins installiert Testabhängigkeiten in `.venv`, führt Regression und Abnahme aus und erstellt die Demo.
4. Unter „Test Result“ stehen JUnit-Ergebnisse; unter „Artifacts“ liegen XML-, JSON-, CSV- und Excel-Dateien. Fehlgeschlagene Tests stoppen den Build. Die jeweiligen Testberichte werden auch bei Testfehlern veröffentlicht.

Die Pipeline räumt nur `reports/unit`, `reports/acceptance` und `reports/demo` im Job-Workspace auf. Gleichzeitige Builds dieses Jobs sind deaktiviert, und die letzten zehn Builds bleiben erhalten. GitHub Actions führt dieselben Prüfungen auf Python 3.10 und 3.13 aus und lädt Berichte auch bei Fehlern hoch.
