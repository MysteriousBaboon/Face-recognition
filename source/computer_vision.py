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


def process_image(file):
    """
    :param file: -- the uploaded picture
    :return: list of all recognised face's id
    """

    ########################################################INIT########################################################
    # Delete the temp file and recreate it
    shutil.rmtree("static/temp")
    os.mkdir("static/temp")
    open("static/temp/.temp", "w").write("")

    # Load the uploaded image desired by the user
    npimg = np.fromfile(file, np.uint8)
    # pass it to CV
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Connect to DB
    con = sqlite3.connect("../db.sqlite")
    cursor = con.cursor()

    known_face_encodings = []
    known_face_names = []
    known_face_ids = []

    face_names = []
    face_ids = []

    # Load our database and load all the faces and their corresponding name
    df = pd.read_sql_query("SELECT * FROM Person", con)
    for row in df.values:
        # Get common path and add row[2] that is the specific url path
        face = face_recognition.load_image_file("../dataset/" + row[2])

        # Encode the face and add the corresponding id and nameà
        known_face_encodings.append(face_recognition.face_encodings(face)[0])
        known_face_names.append(row[1])
        known_face_ids.append(row[0])
    ####################################################################################################################

    ##################################################FACE DETECTIONS###################################################
    # Find all the faces and face encodings in the submitted picture
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    for i, face_encoding in enumerate(face_encodings):
        padding = 10

        # Save the cropped picture of the specific unknown face
        cropped_image = image[face_locations[i][0] - 10:face_locations[i][2] + 10,
                        face_locations[i][3] - padding:face_locations[i][1] + 10]

        # See if the face is a match for the known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        # If there is a match get the name and the id
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            db_id = known_face_ids[best_match_index]
        # Else generate a file name id_time.jpg
        else:
            filename = f"{known_face_ids[best_match_index]}_{time.time_ns()}.jpg"
            # Create the cropped image file
            cv2.imwrite(f"../dataset/{filename}", cropped_image)
            # Create a name to the unknown face
            name = '_' + "".join(random.choice(string.digits) for i in range(7))

            # Insert into DB
            cursor.execute("INSERT INTO Person (name, path) VALUES (? , ?)", (name, filename))
            db_id = cursor.lastrowid
            cursor.execute("INSERT INTO Frequentation (person_ID,seen,violence,incident) VALUES (?, ?, ?,?)", (db_id, 0,
                                                                                                               0, 0))
            con.commit()

        face_names.append(name)
        face_ids.append(db_id)
        # Write to temp folder
        cv2.imwrite(f"static/temp/{name}.jpg", cropped_image)

    ##################################################IMAGE TREATMENT###################################################
    # Process the detected faces
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        padding = 8
        # Draw the box
        cv2.rectangle(image, (left - padding, top - padding), (right + padding, bottom + padding), (242, 112, 31),
                      thickness=3)

        # Draw a label with a name below the face
        font = cv2.FONT_HERSHEY_DUPLEX
        # White with a black outline
        cv2.putText(image, name, (left, bottom + 40), font, 0.5, (00, 00, 00), 2)
        cv2.putText(image, name, (left, bottom + 40), font, 0.5, (255, 255, 255), 1)

    # The uploaded picture processed
    cv2.imwrite("static/temp/main.jpg", image)
    return face_ids
