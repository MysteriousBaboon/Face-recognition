from flask import Flask, request, render_template
import ml
import sqlite3
import pandas as pd
import json
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['profile_pic']
        ids = ml.facial_recognition(file)
        con = sqlite3.connect("../db.sqlite")
        string = "("
        for el in ids:
            string += f"{str(el)},"
        string = string[:-1] +")"
        req = f"SELECT * FROM Person WHERE ID in {string}"
        req2 = f"SELECT * FROM Frequentation WHERE person_ID in {string}"
        df = pd.read_sql_query(req, con)
        df2 = pd.read_sql_query(req2, con)
        result = pd.merge(df,df2, left_on='ID',right_on='person_ID').to_json(orient="records")
        parsed = json.loads(result)
        print(parsed)
        return render_template("response.html", humans=parsed)
    elif request.method == 'GET':
        return render_template("home.html")


app.run(host='127.0.0.1', port=5000)
