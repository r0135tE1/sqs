# SQS
- Spaß mit Flaggen
  - Flaggen werden angezeigt und man muss das entsprechende Land erraten
  - Bei korrektem Erraten bekommt man punkte für seine Streak
  - Falsche antwort setzt die streak zurück
  - speichern der streak für einen nutzer in der Datenbank
  - Einsehen der Streak eines Nutzers

# MVP Voraussetzungen
- mindestens ein öffentlich erreichbarer Endpunkt: https: //restcountries.com/
- mindestens ein abgesicherter Endpunkt (Login-Kontext etc.): Endpunkt für Highscore einsicht, geht nur für eingeloggte User, die ihn gespeichert haben.
- mindestens 3 Schichten:
- Frontend: Headless, nimmt nur Daten entgegen. Typescript, evtl Vue3
- Backend: Stellt API bereit, um restcountries API anzusprechen und Frontend Daten zu liefern. Python
- Persistenzschicht (bspw. Datenbank): evtl PostGres, speichert userdaten und highscores
- Das Backend muss außerdem mit mindestens einem externen Service
sprechen (bspw. Google-APIs etc.).
