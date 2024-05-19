from flask import Flask, render_template
import os
import mysql.connector
import sys
import re

# jump up one folder to import the config file
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Connect to Database
mydb = mysql.connector.connect(
    host=config.DB_HOSTNAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DATABASE
        )
mycursor = mydb.cursor()

app = Flask(__name__)

@app.route('/')
def index():
    # Anzahl Zuege
    query = "SELECT count(*) AS anzahl_zuege FROM trains"
    mycursor.execute(query)
    results = mycursor.fetchall()
    anzahl_zuege = results[0][0]

    # Durchschnittliche Verspätung in Minuten
    query = "SELECT AVG(DISTINCT(TIMESTAMPDIFF(Minute,planned_departure,current_departure))) FROM trains"
    mycursor.execute(query)
    results = mycursor.fetchall()
    verspaetung_in_min = results[0][0]

    # Durchschnittliche Ausfallwahrscheinlichkeit in %
    query = "SELECT ((SELECT COUNT(*) FROM trains WHERE current_departure IS NULL) /(SELECT COUNT(*) FROM trains))*100"
    mycursor.execute(query)
    results = mycursor.fetchall()
    ausfallwahrscheinlichkeit = results[0][0]

    # Bahnhöfe Liste
    query = "SELECT DISTINCT train_station FROM trains"
    mycursor.execute(query)
    results = mycursor.fetchall()
    bahnhoefe=""
    for bahnhof in results:
     bahnhoefe += str(bahnhof)
    # Zeichen entferenn
    bahnhoefe = re.sub('[(\']',"",bahnhoefe)
    bahnhoefe = re.sub('[)]'," ",bahnhoefe)

    # Bahnhof mit meister Verspätung
    query ="SELECT AVG(DISTINCT(TIMESTAMPDIFF(Minute,planned_departure,current_departure))) AS delay, train_station FROM trains GROUP BY train_station ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    bahnhof_mit_hoechster_durchschnitt_verspaetung = results[0][1]
    bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten = results[0][0]

    # Zuglinie mit meister Verspätung
    query ="SELECT AVG(DISTINCT(TIMESTAMPDIFF(Minute,planned_departure,current_departure))) AS delay, line, train_id FROM trains GROUP BY line, train_id ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    linie_mit_hoechster_durchschnitt_verspaetung = results[0][1]
    linie_mit_hoechster_durchschnitt_verspaetung_minuten = results[0][0]

    # Höchste Verspätung
    query ="SELECT DISTINCT(TIMESTAMPDIFF(Minute,planned_departure,current_departure)) AS delay FROM trains ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    höchste_verspaetung = results[0][0]

    # RB50 Daten
    # Anzahl RB50
    query = "SELECT COUNT(*) FROM trains WHERE line ='RB50'"
    mycursor.execute(query)
    results = mycursor.fetchall()
    rb50_anzahl = results[0][0]
    # Durchschnittliche Verspätung in Minuten RB50
    query = "SELECT AVG(DISTINCT(TIMESTAMPDIFF(Minute,planned_departure,current_departure))) FROM trains WHERE line='RB50'"
    mycursor.execute(query)
    results = mycursor.fetchall()
    rb50_verspaetung = results[0][0]
    # Ausfallwahrscheinlichkeit RB50
    query = "SELECT ((SELECT COUNT(*) FROM trains WHERE current_departure IS NULL AND line='RB50') /(SELECT COUNT(*) FROM trains WHERE line='RB50'))*100"
    mycursor.execute(query)
    results = mycursor.fetchall()
    rb50_ausfallwahrscheinlichkeit = results[0][0]



    return render_template('index.html',anzahl_zuege=anzahl_zuege,verspaetung_in_min=verspaetung_in_min,
                           ausfallwahrscheinlichkeit=ausfallwahrscheinlichkeit, bahnhoefe=bahnhoefe,
                           rb50_anzahl=rb50_anzahl,rb50_ausfallwahrscheinlichkeit=rb50_ausfallwahrscheinlichkeit,rb50_verspaetung=rb50_verspaetung,
                           bahnhof_mit_hoechster_durchschnitt_verspaetung=bahnhof_mit_hoechster_durchschnitt_verspaetung,
                           bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten=bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten,
                           linie_mit_hoechster_durchschnitt_verspaetung=linie_mit_hoechster_durchschnitt_verspaetung,
                           linie_mit_hoechster_durchschnitt_verspaetung_minuten=linie_mit_hoechster_durchschnitt_verspaetung_minuten,
                           höchste_verspaetung=höchste_verspaetung)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
