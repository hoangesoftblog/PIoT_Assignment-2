import flask
from database import *
import flask_cors
import json

import cv2
from flask import Flask, render_template, Response

app = flask.Flask(__name__)
app.secret_key = "jose"


# flask_cors.CORS(app=app)
login_db = LoginDatabase()
user_db = UserDatabase()
car_db = CarDatabase()
booking_db = BookingDatabase()
employee_db = EmployeesDatabase()
issues_db = IssuesDatabase()


# https://blog.tecladocode.com/how-to-add-user-logins-to-your-flask-website/
@app.route('/login', methods = ["POST", "GET"])
def login(error=False):
    if flask.request.method == "GET":
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.render_template("login.html", error=error)
        else:
            return flask.redirect(flask.url_for("home"))
    else:
        username, password = flask.request.form.get("email"), flask.request.form.get("passWord")
        records = login_db.find_login(username, password)
        print(records)
        if len(records) != 1:
            # return flask.redirect(flask.url_for("login", error=True))
            return flask.render_template("login.html", error=True)
        else:
            flask.session[login_db.USERNAME] = username
            flask.session[login_db.ID] = records[0][login_db.ID]
            role = records[0][login_db.ROLES]
            if role == 0:
                return flask.redirect(flask.url_for("home"))
            elif role == 1:
                # Redirect for Engineer
                pass
            elif role == 2:
                # Redirect for Manager
                pass
            elif role == 3:
                # Redirect for Admin
                pass


@app.route('/sign_up', methods = ["POST", "GET"])
def sign_up():
    if flask.request.method == "GET":
        return flask.render_template("sign_up.html")
    else:
        data = flask.request.form
        username, password, name, address, phone_number = data.get("username"), data.get("password"), data.get("name"), data.get("address"), data.get("phone_number")
        user_id = login_db.add_user(username, password)

        flask.session[login_db.USERNAME] = username
        flask.session[login_db.ID] = user_id

        return flask.redirect(flask.url_for("home"))


@app.route('/forget_password', methods = ["GET", "POST"])
def forget_password():
    if flask.request.method == "GET":
        flask.render_template("forget_password.html")


@app.route('/logout', methods = ["GET"])
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for("login"))


@app.route('/home', methods = ["GET"])
def home(cars=None):
    if flask.session.get("username", None) is None:
        return flask.redirect(flask.url_for("login"))
    else:
        return flask.render_template("index.html", cars = cars if cars else car_db.get_all_car())


@app.route('/car/get', methods = ["GET"])
def get_cars():
    records = car_db.get_all_car()
    return flask.jsonify(records)


@app.route('/car/find', methods = ["POST"])
def find_cars():
    data = flask.request.form
    search_features = data["search_features"]
    records = car_db.find_car(search_features)
    return flask.redirect(flask.url_for("home", cars = records))


@app.route('/car/book/', methods = ["GET", "POST"])
def book_car():
    pass

camera = cv2.VideoCapture(0)  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/')
def index():
    return render_template('QR_code.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen():
    camera = cv2.VideoCapture(0)

    while True:
        ret, img = camera.read()

        if ret:
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break
        

if __name__ == "__main__":
    app.run(debug = True)