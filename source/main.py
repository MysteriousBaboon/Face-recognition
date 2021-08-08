from flask import Flask, request, render_template
import computer_vision
import sqlite3
import pandas as pd
import json
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    main function that handle both the image submitting and the response
    """

    # Image submission
    if request.method == 'GET':
        return render_template("home.html")

    # Processed response
    elif request.method == 'POST':
        # Connect to DB
        con = sqlite3.connect("../db.sqlite")

        # Check if the uploaded file is not empty
        if request.files['profile_pic']:
            file = request.files['profile_pic']
        else:
            return render_template("home.html")

        # Main function that creates files, and update DB. Return the id of all recognised faces
        ids = computer_vision.process_image(file)
        # Convert list of int to a string adapted for SQL request
        all_ids = str(ids).replace("[", "(").replace("]", ")")

        # Get all the information about all recognised faces in an unified json and pass it to the template
        req = f"SELECT * FROM Person WHERE ID in {all_ids}"
        req2 = f"SELECT * FROM Frequentation WHERE person_ID in {all_ids}"
        df = pd.read_sql_query(req, con)
        df2 = pd.read_sql_query(req2, con)
        result = pd.merge(df, df2, left_on='ID', right_on='person_ID').to_json(orient="records")
        parsed = json.loads(result)
        return render_template("response.html", humans=parsed)


@app.route('/update', methods=['GET', 'POST'])
def test():
    """
    Function that handles the update request from the processed page
    """
    con = sqlite3.connect("../db.sqlite")
    cursor = con.cursor()
    sql_update = f"""UPDATE Frequentation SET seen = {request.form["seen"]}, violence = {request.form["violence"]},
            incident = {request.form["incident"]} WHERE person_id ={request.form["id"]} """
    cursor.execute(sql_update)
    sql_update = f"""UPDATE Person SET name = "{request.form["name"]}"  WHERE ID ={request.form["id"]}"""
    cursor.execute(sql_update)

    con.commit()
    # Don't redirect
    return '', 204


app.run(host='127.0.0.1', port=5001)
