import sqlite3

# Create database
con = sqlite3.connect("../db.sqlite")
cursor = con.cursor()

cursor.execute("""CREATE TABLE Person (ID INTEGER PRIMARY KEY, name, path)""")
cursor.execute("""CREATE TABLE Frequentation (person_ID, seen, violence, incident)""")

# EXAMPLES of instances creations
cursor.execute("""INSERT INTO Person (name,path) values ("Chris Hemsworth", "train/chris_hemsworth.jpg")""")
cursor.execute("""INSERT INTO Person (name,path) values ("Jeremy Renner", "train/test_jeremy_renner.jpg")""")

cursor.execute("""INSERT INTO Frequentation (person_ID,seen,violence,incident) values (1, 3, 0,0)""")
cursor.execute("""INSERT INTO Frequentation (person_ID,seen,violence,incident) values (2, 6, 2, 4)""")
con.commit()


