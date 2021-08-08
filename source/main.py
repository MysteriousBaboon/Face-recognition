from flask import Flask, request, render_template
import ml
import sqlite3
import pandas as pd
import json
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    main function that handle both the image submitting and the response
    :return:
    """
    if request.method == 'POST':
        con = sqlite3.connect("../db.sqlite")
        file = request.files['profile_pic']
        ids = ml.facial_recognition(file)
        string = "("
        for el in ids:
            string += f"{str(el)},"
        string = string[:-1] +")"
        req = f"SELECT * FROM Person WHERE ID in {string}"
        req2 = f"SELECT * FROM Frequentation WHERE person_ID in {string}"
        df = pd.read_sql_query(req, con)
        df2 = pd.read_sql_query(req2, con)
        result = pd.merge(df, df2, left_on='ID',right_on='person_ID').to_json(orient="records")
        parsed = json.loads(result)
        return render_template("response.html", humans=parsed)
    # Return the template for image submitting
    elif request.method == 'GET':
        return render_template("home.html")


@app.route('/test', methods=['GET', 'POST'])
def test():
    con = sqlite3.connect("../db.sqlite")
    cursor = con.cursor()
    sql_id = f"""SELECT ID FROM Person WHERE name = '{request.form["name"]}'"""
    person_id = cursor.execute(sql_id).fetchone()[0]
    sql_update = f"""UPDATE Frequentation SET seen = {request.form["seen"]}, violence = {request.form["violence"]},
            incident = {request.form["incident"]} WHERE person_id ={person_id} """
    cursor.execute(sql_update)
    con.commit()
    return '', 204


app.run(host='127.0.0.1', port=5001)
