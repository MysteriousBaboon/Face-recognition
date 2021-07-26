import cv2
import face_recognition

import numpy as np
import pandas as pd
import sqlite3

import time
import random
import string
import os
import shutil


def facial_recognition(file):
    shutil.rmtree("static/temp")
    # Clean temp folder
    os.mkdir("static/temp")

    con = sqlite3.connect("../db.sqlite")
    cursor = con.cursor()

    # Load our database and load all the faces and their corresponding name
    df = pd.read_sql_query("SELECT * FROM Person", con)
    known_face_encodings = []
    known_face_names = []
    known_face_ids = []

    for index, row in df.iterrows():
        path = "../dataset/" + row["path"]
        face = face_recognition.load_image_file(path)
        known_face_encodings.append(face_recognition.face_encodings(face)[0])
        known_face_names.append(row["name"])
        known_face_ids.append(row["ID"])

    # Load the uploaded image desired by the user
    npimg = np.fromfile(file, np.uint8)
    # pass it to CV
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Find all the faces and face encodings in the submitted picture
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    face_names = []
    face_ids = []

    for i, face_encoding in enumerate(face_encodings):
        padding = 10

        # Save the cropped picture of the specific unknown face
        cropped_image = image[face_locations[i][0] - 10:face_locations[i][2] + 10,
                              face_locations[i][3] - padding:face_locations[i][1] + 10]

        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            db_id = known_face_ids[best_match_index]
        else:
            filename = str(time.time_ns() * (i + 1))
            filename += random.choice(string.ascii_letters)
            filename += random.choice(string.ascii_letters)
            filename += ".jpg"

            # Write to big DB
            cv2.imwrite(f"../dataset/{filename}", cropped_image)
            result_str = ''.join(random.choice(string.digits) for i in range(5))
            name = f"_{result_str}"

            cursor.execute("""INSERT INTO Person (name, path) VALUES (? , ?)""", (name, filename))
            db_id = cursor.lastrowid
            cursor.execute("INSERT INTO Frequentation (person_ID,seen,violence,incident) VALUES (?, ?, ?,?)", (db_id, 3,
                                                                                                               0, 0))
            con.commit()

        face_names.append(name)
        face_ids.append(db_id)
        # Write to temp folder
        cv2.imwrite(f"static/temp/{name}.jpg", cropped_image)

    # Display the results

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Draw a box around the face
        padding = 10
        cv2.rectangle(image, (left - padding, top - padding), (right + padding, bottom + padding), (0, 255, 200),
                      thickness=5)

        # Draw a label with a name below the face
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(image, name, (left, bottom + 40), font, 1.0, (00, 00, 00), 5)
        cv2.putText(image, name, (left, bottom + 40), font, 1.0, (255, 255, 255), 2)

    cv2.imwrite("static/temp/main.jpg", image)

    return face_ids
