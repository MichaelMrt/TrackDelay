# TrackDelay
## Züge über die Deutsche Bahn Api erfassen und die Daten in eine Datenbank laden, um anschließend Auswertungen mit den Daten durchführen zu können wie etwa die durchschnittliche Verspätung.

## Installation:
### Python muss auf dem System installiert sein.

## API
1. Ein Account muss bei den Entwicklern der Deutschen Bahn erstellt werden: https://developers.deutschebahn.com
2. Eine neue Anwendung muss erstellt werden mit dem Namen eurer wahl: https://developers.deutschebahn.com/db-api-marketplace/apis/application/new 
3. Sichert eure Client Id und Client secret.
4. Navigiert zu der Seite mit verfügbaren Api's und wählt die 'Timetables' Api aus: https://developers.deutschebahn.com/db-api-marketplace/apis/product 
5. Anschließend müsst ihr den roten Abonnieren Knopf drücken und eure Anwendung wählen. 

### Abhängigkeiten
1. Repository clonen
2. Mit _pip install deutsche_bahn_api_ die benötigte Python Bibliothek installieren.
3. Mit _pip install mysql-connector_ die Python Bibliothek zur Datenbankverbindung installieren
4. Erstelle einen Ordner /logs im Repository und darin die Dateien _logs.log_ und _error.log_
5. Nun muss eine config.py Datei im Repository angelegt werden. Darin werden wir unsere Api Daten als auch Datenbankverbindungsdaten eingeben, damit das Skript diese von selbst auslesen kann.
Hier ein Muster:
CLIENT_ID=    "deine_Client_ID"
CLIENT_SECRET="dein_Client_Secret"
DB_HOSTNAME = "dein_db_hostname"
DB_USER = "dein_db_user"
DB_PASSWORD = "dein_db_passwort"
DATABASE = "dein_datenbankname"

6. Erstelle in deiner Datenbank die Tabelle **trains** mit folgenden Spalten.
![image](https://github.com/MichaelMrt/TrackDelay/assets/116624593/2973109e-3ef1-4210-832b-f3b94435ff5c)

7. Nun sollte das Skript ausführbar sein. 

## Anpassungen vornehmen:
In der main.py können in der Methode repeat_task(): die Bahnhöfe angepasst werden. Standartmäßg sind es folgende Bahnhöfe:
+ api_wrapper.start("Bonn")
+ api_wrapper.start("Köln")
+ api_wrapper.start("Münster")
+ api_wrapper.start("Düsseldorf Hbf")
+ api_wrapper.start("Duisburg")
+ api_wrapper.start("Essen")
+ api_wrapper.start("Wuppertal")
+ api_wrapper.start("Bochum")
+ api_wrapper.start("Berlin Hbf")
+ api_wrapper.start("Lünen")
+ api_wrapper.start("Ennepetal")
+ Um sicher zu gehen, dass es sich um den gewünschten Bahnhof handelt, kann in der Datenbank in der Spalte _train_station_ geschaut werden, ob der Bahnhof der richtige ist.
+ Gibt man etwa api_wrapper.start("Berlin") an, könnte es passieren dass nicht der Hbf sondern ein andere Bahnhof in Berlin erfasst wird. Der Bahnhofsname wird auch zusätzlich vom Skript geprintet.

Sollten Fehler im Skript auftreten, werden diese in logs/error.log vermerkt.
In logs/logs.log wird die letze Abfrage des Skripts gespeichert: _End of script 2024-05-12 13:54:48.811615_

Skript kann auch auf einer Remote Maschine laufen gelassen werden, damit rund um die Uhr Daten erfasst werden

