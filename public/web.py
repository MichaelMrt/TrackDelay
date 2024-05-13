from flask import Flask, render_template
import os
import mysql.connector
import sys

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
print(results[0][0])

mydb.close()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',anzahl_zuege=anzahl_zuege,verspaetung_in_min=verspaetung_in_min)

if __name__ == '__main__':
    app.run(debug=True)
