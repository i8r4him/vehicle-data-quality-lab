# User Stories und Abnahmekriterien

## 1. Angebotsupdates zuverlässig einspielen

**Als Mitarbeiterin der Datenpflege möchte ich Updates aus CSV oder Excel geprüft einlesen, damit nur vollständige und fachlich gültige Angebote im Bestand erscheinen.**

- Eine gültige Datei legt neue Angebote an und aktualisiert bestehende Angebote mit neuerem Datenstand.
- Ein fehlender Pflichtwert, eine doppelte ID, ein unbekanntes Fahrzeug, ein ungültiger Wert oder ein veraltetes Update lehnt die ganze Datei ab.
- Die Meldung enthält Import-ID, Zeile, Regel und Fehlerbeschreibung.
- Preise bleiben centgenau; Referenzen auf Fahrzeuge sind durch Fremdschlüssel gesichert.

**Nachweis:** `test_valid_import_counts_and_audit`, `test_five_quality_rules_reject_entire_file`, `test_mixed_file_cannot_partially_apply`, `test_same_version_conflict_is_rejected`.

**Ausführbare Abnahme:** `features/import.feature`, Tag `@US1`: CSV/XLSX, centgenaue Preise, vollständige Ablehnung und Versionskonflikt. `tests/test_rule_boundaries.py` prüft zusätzlich erlaubte Grenzwerte und unmittelbar benachbarte ungültige Werte.

## 2. Wiederkehrende Abläufe überwachen und Fehler beheben

**Als Teammitglied möchte ich neue Update-Dateien automatisch prüfen und fehlerhafte Dateien nach der Korrektur erneut verarbeiten, damit manuelle Wiederholungen und unbemerkte Fehler reduziert werden.**

- Der Monitor prüft den Ordner in einem einstellbaren Intervall und gibt JSON-Ereignisse aus.
- Identische Dateiinhalte erzeugen keinen weiteren Import und keine doppelten Änderungen, auch bei zwei gleichzeitigen Importversuchen.
- Eine korrigierte Datei wird als neuer Import geprüft.
- Ein beschädigtes XLSX blockiert die Verarbeitung der nächsten Datei nicht.
- Quelldateien bleiben erhalten; die Fehlerhistorie ist im Bericht sichtbar.

**Nachweis:** `test_scan_is_idempotent`, `test_corrected_file_can_be_retried_and_duplicates_are_skipped`, `test_concurrent_identical_import_is_applied_once`, `test_malformed_xlsx_does_not_stop_inbox_processing`.

**Ausführbare Abnahme:** Szenario „Ein wiederholter Import erzeugt keine doppelten Änderungen“, Tag `@US2`: derselbe Inhalt erzeugt genau einen Import und eine Änderung.

## 3. Änderungen und Arbeitsabläufe nachvollziehen

**Als fachlicher Ansprechpartner möchte ich Bestand, Fehler und Änderungen in SQL-Auswertungen und Excel sehen, damit ich Rückfragen beantworten und Verbesserungsmöglichkeiten untersuchen kann.**

- Jede tatsächliche Angebotsänderung speichert alten und neuen Datensatz, Import-ID und UTC-Zeitstempel.
- Acht SQL-Abfragen sind separat lesbar und als CSV exportierbar.
- Ein neu erzeugter Excel-Bericht enthält sechs Blätter, filterbare Tabellen und zwei Diagramme, sofern Fehler vorliegen.
- Die Serviceanalyse kennzeichnet ihre Beispieldaten ausdrücklich als synthetisch und behauptet keine gemessene Zeitersparnis.
- Nach einem Import kann der Bericht wiederholt aus dem aktuellen Bestand erstellt werden.

**Nachweis:** `test_valid_import_counts_and_audit`, `test_eight_queries_and_service_aggregates`, `test_report_has_expected_values_tables_and_charts`, `test_full_demo`.
