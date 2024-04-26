from flask import Flask
from datetime import datetime
import time

time.sleep(10)

app = Flask(__name__)

@app.route("/")
def hello_world():
    now = datetime.now()
    day = now.strftime("%d")
    month = now.strftime("%m")
    year = now.strftime("%y")
    con = open(f"logs/{day}_{month}_{year}log.txt", encoding="UTF-8").readlines()
    status = open("status.txt", "r").read()
    text = f"<p>{status}</p>"
    for i in con:
        text += "<p>" + i + "</p>"
    return text

app.run(host="127.0.0.1", port="5000")