# Facial-recognition
## **Summary** 
This is a little web API/site written in [Flask](https://flask.palletsprojects.com/en/2.0.x/) and using [Facial Recognition](https://github.com/ageitgey/face_recognition) that you can run to recognize faces and add them to a database. It supports re-identification and update of the person's data. **It only supports Linux**

## **Getting Started**
- Install [dlib](https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf)
- Install requirements with ```pip install -r requirements.txt```
- Run the python script ```db.py``` in source to create the sqlite DB
- Run the ```main.py script``` in source to launch the Flask app
- Go to http://127.0.0.1:5000/ and upload a picture
