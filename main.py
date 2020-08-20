import flask
from database import *
import flask_cors
import json

app = flask.Flask(__name__)
app.secret_key = "jose"

# flask_cors.CORS(app=app)
account_db = UserDatabase()
car_db = CarDatabase()
booking_db = BookingDatabase()


# https://blog.tecladocode.com/how-to-add-user-logins-to-your-flask-website/
@app.route('/login', methods = ["POST", "GET"])
def login(error=False):
    if flask.request.method == "GET":
        if flask.session.get(account_db.USERNAME, None) is None:
            return flask.render_template("login.html", error=error)
        else:
            return flask.redirect(flask.url_for("home"))
    else:
        username, password = flask.request.form.get("username"), flask.request.form.get("password")
        records = account_db.find_user(username, password)
        print(records)
        if len(records) != 1:
            # return flask.redirect(flask.url_for("login", error=True))
            return flask.render_template("login.html", error=True)
        else:
            flask.session[account_db.USERNAME] = username
            flask.session[account_db.ID] = records[0][account_db.ID]

            return flask.redirect(flask.url_for("home"))


@app.route('/sign_up', methods = ["POST", "GET"])
def sign_up():
    if flask.request.method == "GET":
        return flask.render_template("sign_up.html")
    else:
        data = flask.request.form
        username, password, name, address, phone_number = data.get("username"), data.get("password"), data.get("name"), data.get("address"), data.get("phone_number")
        account_db.add_user(username, password, name, address, phone_number)

        record = account_db.get_latest()

        flask.session[account_db.USERNAME] = username
        flask.session[account_db.ID] = record[0][account_db.ID]

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
    
        

if __name__ == "__main__":
    app.run(debug = True)