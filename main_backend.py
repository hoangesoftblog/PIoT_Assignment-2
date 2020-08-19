import flask
from database import AccountDatabase, CarDatabase
import flask_cors
import json

app = flask.Flask(__name__)
flask_cors.CORS(app=app)
account_db = AccountDatabase()
car_db = CarDatabase()


@app.route('/login', methods = ["POST"])
def login():
    # if flask.request.method == "GET":
    #     return flask.render_template("login.html")
    # else:
    #     username, password = flask.request.form.get("username"), flask.request.form.get("password")
    #     records = db.find_user(username, password)
    #     if len(records) != 1:
    #         return "Incorrect"
    #     else:
    #         return "Correct"
    data = flask.request.get_json()
    print(data)
    username, password = data.get("username"), data.get("password")
    records = account_db.find_user(username, password)
    if len(records) != 1:
        return "Incorrect"
    else:
        return "Correct"

@app.route('/sign_up', methods = ["POST"])
def sign_up():
    # if flask.request.method == "GET":
    #     return flask.render_template("sign_up.html")
    # else:
    #     username, password = flask.request.form.get("username"), flask.request.form.get("password")
    #     db.add_user(username, password)
    #     return "Successful"

    username, password = flask.request.form.get("username"), flask.request.form.get("password")
    account_db.add_user(username, password)
    return "Successful"

@app.route('/car/get', methods = ["GET"])
def get_cars():
    records = car_db.get_all_car()
    return flask.jsonify(records)


@app.route('/car/find', methods = ["POST"])
def find_cars():
    data = flask.request.get_json()
    search_features = data["search_features"]
    records = car_db.find_car(search_features)
    return flask.jsonify(records)

@app.route('/forget_password', methods = ["GET", "POST"])
def forget_password():
    if flask.request.method == "GET":
        flask.render_template("forget_password.html")
        

if __name__ == "__main__":
    app.run(debug = True)