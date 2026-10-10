@US1
Feature: Angebotsdateien vollständig prüfen und übernehmen
  Fehlerhafte Dateien dürfen auch gültige Zeilen nicht teilweise einspielen.

  Scenario: Eine gültige CSV wird centgenau gespeichert
    Given eine Datei mit folgenden Angebotsdaten
      | offer_id | price_eur |
      | TEST01   | 123.45    |
    When ich die Datei importiere
    Then lautet der Importstatus "accepted"
    And beträgt die Anzahl neuer Angebote mit Änderungshistorie 1
    And ist die Rate von "TEST01" genau 12345 Cent

  Scenario: Dieselben Fachregeln gelten für XLSX
    Given eine Datei mit folgenden Angebotsdaten
      | offer_id | price_eur |
      | TEST01   | 0.01      |
    And die Datei liegt als XLSX vor
    When ich die Datei importiere
    Then lautet der Importstatus "accepted"
    And beträgt die Anzahl neuer Angebote mit Änderungshistorie 1
    And ist die Rate von "TEST01" genau 1 Cent

  Scenario Outline: Ein ungültiges Angebot lehnt die gesamte Datei ab
    Given eine Datei mit folgenden Angebotsdaten
      | offer_id | vehicle_id | price_eur |
      | GOOD01   | V001       | 123.45    |
      | <id>     | <vehicle>  | <price>   |
    When ich die Datei importiere
    Then lautet der Importstatus "rejected"
    And bleiben Bestand und Änderungshistorie unverändert
    And wird der Fehler "<rule>" für Zeile 3 protokolliert

    Examples:
      | id     | vehicle | price | rule        |
      | BAD01  | V001    | -1    | VALUE       |
      | BAD01  | V001    |       | REQUIRED    |
      | GOOD01 | V001    | 10    | DUPLICATE   |
      | BAD01  | UNKNOWN | 10    | FOREIGN_KEY |

  Scenario: Eine Änderung ohne neueren Datenstand wird abgelehnt
    Given eine Datei mit folgenden Angebotsdaten
      | offer_id | price_eur | updated_at |
      | OFF001   | 349.00    | 2026-09-01 |
    When ich die Datei importiere
    Then lautet der Importstatus "rejected"
    And bleiben Bestand und Änderungshistorie unverändert
    And wird der Fehler "STALE_UPDATE" für Zeile 2 protokolliert

  @US2
  Scenario: Ein wiederholter Import erzeugt keine doppelten Änderungen
    Given eine Datei mit folgenden Angebotsdaten
      | offer_id |
      | TEST01   |
    When ich die Datei importiere
    Then lautet der Importstatus "accepted"
    When ich die Datei importiere
    Then lautet der Importstatus "skipped"
    And beträgt die Anzahl protokollierter Imports 1
    And beträgt die Anzahl protokollierter Änderungen 1
    And ist die Rate von "TEST01" genau 12345 Cent
