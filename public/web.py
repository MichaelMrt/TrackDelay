from flask import Flask, render_template
import os
import mysql.connector
import sys
import re

# jump up one folder to import the config file
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

current_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(current_dir, 'create_tables.sql')
sql_file = open(sql_file_path,'r')
sql_code = sql_file.read()
sql_file.close()
sql_code = sql_code.split(";")
log_path = os.path.join(os.path.dirname(current_dir), "logs", "logs.log")

log_file = open(log_path, "r")
log_content = log_file.read()

app = Flask(__name__)

@app.route('/')
def index():
    # Connect to Database
    try:
        mydb = mysql.connector.connect(
        host=config.DB_HOSTNAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DATABASE
            )
    except Exception as error:
       return render_template('db_error.html',log_content=log_content)

    mycursor = mydb.cursor()
    for query in sql_code:
     mycursor.execute(query)
     mydb.commit()

    # Anzahl Zuege
    query = "SELECT count(*) AS anzahl_zuege FROM trains"
    mycursor.execute(query)
    results = mycursor.fetchall()
    anzahl_zuege = results[0][0]

    # Durchschnittliche Verspätung in Minuten
    query = "SELECT AVG(TIMESTAMPDIFF(Minute,planned_departure,current_departure)) FROM trains"
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
    # Zeichen entfernen
    bahnhoefe = re.sub('[(\']',"",bahnhoefe)
    bahnhoefe = re.sub('[)]'," ",bahnhoefe)

    # Bahnhof mit meister Verspätung
    query ="SELECT AVG(TIMESTAMPDIFF(Minute,planned_departure,current_departure)) AS delay, train_station FROM trains GROUP BY train_station ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    bahnhof_mit_hoechster_durchschnitt_verspaetung = results[0][1]
    bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten = results[0][0]

    # Zuglinie mit höchster durschnittsverspätung Verspätung
    query ="SELECT AVG(TIMESTAMPDIFF(Minute,planned_departure,current_departure)) AS delay, line, train_id FROM trains GROUP BY line, train_id ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    linie_mit_hoechster_durchschnitt_verspaetung = results[0][1]
    linie_mit_hoechster_durchschnitt_verspaetung_minuten = results[0][0]

    # Höchste Verspätung
    query ="SELECT TIMESTAMPDIFF(Minute,planned_departure,current_departure) AS delay, line FROM trains ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    hoechste_verspaetung = results[0][0]
    hoechste_verspaetung_zug = results[0][1]

    # RB50 Daten
    # Anzahl RB50
    query = "SELECT COUNT(*) FROM trains WHERE line ='RB50'"
    mycursor.execute(query)
    results = mycursor.fetchall()
    rb50_anzahl = results[0][0]

    # Durchschnittliche Verspätung in Minuten RB50
    query = "SELECT AVG(TIMESTAMPDIFF(Minute,planned_departure,current_departure)) FROM trains WHERE line='RB50'"
    mycursor.execute(query)
    results = mycursor.fetchall()
    rb50_verspaetung = results[0][0]
    
    # Ausfallwahrscheinlichkeit RB50
    query = "SELECT ((SELECT COUNT(*) FROM trains WHERE current_departure IS NULL AND line='RB50') /(SELECT COUNT(*) FROM trains WHERE line='RB50'))*100"
    mycursor.execute(query)
    results = mycursor.fetchall()
    rb50_ausfallwahrscheinlichkeit = results[0][0]

    # Wochenstatistik
    # Bahnhof mit meister Verspätung WOCHE
    query ="SELECT AVG(TIMESTAMPDIFF(Minute,planned_departure,current_departure)) AS delay, train_station FROM trains WHERE WEEK(CURRENT_DATE)=WEEK(planned_departure) GROUP BY train_station ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    bahnhof_mit_hoechster_durchschnitt_verspaetung_woche = results[0][1]
    bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten_woche = results[0][0]

    # Zuglinie mit höchster durschnittsverspätung Verspätung WOCHE
    query ="SELECT AVG(TIMESTAMPDIFF(Minute,planned_departure,current_departure)) AS delay, line, train_id FROM trains WHERE WEEK(CURRENT_DATE)=WEEK(planned_departure) GROUP BY line, train_id ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    linie_mit_hoechster_durchschnitt_verspaetung_woche = results[0][1]
    linie_mit_hoechster_durchschnitt_verspaetung_minuten_woche = results[0][0]

    # Höchste Verspätung WOCHE
    query ="SELECT TIMESTAMPDIFF(Minute,planned_departure,current_departure) AS delay, line FROM trains WHERE WEEK(CURRENT_DATE)=WEEK(planned_departure) ORDER BY delay DESC LIMIT 1"
    mycursor.execute(query)
    results = mycursor.fetchall()
    hoechste_verspaetung_woche = results[0][0]
    hoechste_verspaetung_zug_woche = results[0][1]

    # Tagesstatistik
    query ="SELECT * FROM tagesstatistik"
    mycursor.execute(query)
    results = mycursor.fetchall()
    tagesstatistik = results



    return render_template('index.html',
                           anzahl_zuege=anzahl_zuege,
                           verspaetung_in_min=verspaetung_in_min,
                           ausfallwahrscheinlichkeit=ausfallwahrscheinlichkeit, 
                           bahnhoefe=bahnhoefe,
                           rb50_anzahl=rb50_anzahl,
                           rb50_ausfallwahrscheinlichkeit=rb50_ausfallwahrscheinlichkeit,
                           rb50_verspaetung=rb50_verspaetung,
                           bahnhof_mit_hoechster_durchschnitt_verspaetung=bahnhof_mit_hoechster_durchschnitt_verspaetung,
                           bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten=bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten,
                           linie_mit_hoechster_durchschnitt_verspaetung=linie_mit_hoechster_durchschnitt_verspaetung,
                           linie_mit_hoechster_durchschnitt_verspaetung_minuten=linie_mit_hoechster_durchschnitt_verspaetung_minuten,
                           hoechste_verspaetung=hoechste_verspaetung,hoechste_verspaetung_zug=hoechste_verspaetung_zug,
                           bahnhof_mit_hoechster_durchschnitt_verspaetung_woche=bahnhof_mit_hoechster_durchschnitt_verspaetung_woche,
                           bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten_woche=bahnhof_mit_hoechster_durchschnitt_verspaetung_minuten_woche,
                           linie_mit_hoechster_durchschnitt_verspaetung_woche=linie_mit_hoechster_durchschnitt_verspaetung_woche,
                           linie_mit_hoechster_durchschnitt_verspaetung_minuten_woche=linie_mit_hoechster_durchschnitt_verspaetung_minuten_woche,
                           hoechste_verspaetung_woche=hoechste_verspaetung_woche,
                           hoechste_verspaetung_zug_woche=hoechste_verspaetung_zug_woche,
                           tagesstatistik=tagesstatistik,
                           log_content=log_content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
