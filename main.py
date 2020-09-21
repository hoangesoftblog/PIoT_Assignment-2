import flask
from database import *
import json
import time

app = flask.Flask(__name__)
app.secret_key = "jose"

# Config upload files
UPLOAD_FOLDER = ""
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# flask_cors.CORS(app=app)
login_db = LoginDatabase()
user_db = UserDatabase()
car_db = CarDatabase()
booking_db = BookingDatabase(calendar=GoogleCalendar())
employee_db = EmployeesDatabase()
issues_db = IssuesDatabase()
statistics_db = StatisticsDatabase()

cloud_storage = google_cloud_storage.GoogleCloudStorage()




# MASTER PI
@app.route('/login', methods=["POST", "GET"])
def login(error=False):
    """Log the user into the system
    
    Parameters
    ----------
    error
        The modes to render the html page
    """
    if flask.request.method == "GET":
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.render_template("login.html", error=error)
        else:
            return flask.redirect(flask.url_for("home"))
    else:
        username, password = flask.request.form.get(
            "email"), flask.request.form.get("password")
        records = login_db.find_login(username, password)
        print(records)
        if len(records) != 1:
            # return flask.redirect(flask.url_for("login", error=True))
            return flask.render_template("login.html", error=True)
        else:
            flask.session[login_db.USERNAME] = username
            flask.session[login_db.ID] = records[0][login_db.ID]
            role = records[0][login_db.ROLES]
            flask.session[login_db.ROLES] = role

            return flask.redirect(flask.url_for("home"))


@app.route('/register', methods=["POST", "GET"])
def sign_up():
    """Register the user
    
    """
    attributes = {"error": False, "email_existed": False}
    if flask.request.method == "GET":
        return flask.render_template("register.html", **attributes)
    else:
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}

        username, password, password_confirmed, name, address, phone_number = data.get("email"), data.get(
            "password"), data.get("password2"), data.get("name"), data.get("address"), data.get("phone_number")
        # user_db.add_user(user_id, name, address, phone_number)

        # Checking for error
        if password != password_confirmed:
            attributes["error"] = True
            return flask.render_template("register.html", **attributes)

        try:
            user_id = login_db.add_login(username, password)
        except Exception:
            attributes["email_existed"] = True
            return flask.render_template("register.html", **attributes)

        # If reach here, means no error
        flask.session[login_db.USERNAME] = username
        flask.session[login_db.ID] = user_id
        flask.session[login_db.ROLES] = "user"

        return flask.redirect(flask.url_for("home"))


@app.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    """Render the forget password page

    """
    if flask.request.method == "GET":
        return flask.render_template("forget_password.html")
    else:
        return "Not done yet"


@app.route('/logout', methods=["GET"])
def logout():
    """Logout of the system
    
    """
    flask.session.clear()
    return flask.redirect(flask.url_for("login"))


@app.route('/home', methods=["GET", "POST"])
def home():
    """Render the home page for the user/admin/manager/engineer
    
    """
    role = flask.session.get(login_db.ROLES)
    if role == "user":
        return cars()
    elif role == "manager":
        return dashboard()
    elif role == "admin":
        return booking()
    elif role == "engineer":
        return issues()
    else:
        return "Not correct roles"


# Booking
@app.route('/booking/<int:car_id>', methods=["GET", "POST"])
def booking_info(car_id):
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}

        # Process attributes
        from_time, to_time = data["from_date"] + " " + data["from_time"] + \
            ":00", data["to_date"] + " " + data["to_time"] + ":00"

        # Perform action
        booking_db.add_booking(car_id, flask.session.get(login_db.ID), data.get(
            booking_db.BOOKING_DETAIL), from_time, to_time)
        return flask.redirect(flask.url_for("home"))
    else:
        if flask.session.get("username", None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            return flask.render_template("booking_infos.html", car_id=car_id)


@app.route('/booking_history', methods=["GET", "POST"])
def booking():
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print(data)

        role = flask.session.get(login_db.ROLES)
        if role == "user":
            data[BookingDatabase.USER_ID] = flask.session.get(login_db.ID)
            records = booking_db.find_booking(**data)
            return flask.render_template("booking_history.html", history=records, type=car_db.get_values_of_col(car_db.BODY_TYPE), colours=car_db.get_values_of_col(car_db.COLOUR), brands=car_db.get_values_of_col(car_db.BRAND), seats=car_db.get_values_of_col(car_db.SEATS))
        elif role == "admin":
            records = booking_db.find_booking(**data)
            return flask.render_template("rental_history.html", history=records, type=car_db.get_values_of_col(car_db.BODY_TYPE), colours=car_db.get_values_of_col(car_db.COLOUR), brands=car_db.get_values_of_col(car_db.BRAND), seats=car_db.get_values_of_col(car_db.SEATS))
        else:
            return flask.redirect(flask.url_for("forbidden"))
    else:
        if flask.session.get("username", None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            role = flask.session.get(login_db.ROLES)
            if role == "user":
                params = {
                    BookingDatabase.USER_ID: flask.session.get(login_db.ID)}
                booking_records = booking_db.find_booking(**params)
                return flask.render_template("booking_history.html", history=booking_records, property_list=booking_db.property_list, type=car_db.get_values_of_col(car_db.BODY_TYPE), colours=car_db.get_values_of_col(car_db.COLOUR), brands=car_db.get_values_of_col(car_db.BRAND), seats=car_db.get_values_of_col(car_db.SEATS))
            elif role == "admin":
                booking_records = booking_db.get_all_booking()
                return flask.render_template("rental_history.html", history=booking_records, property_list=booking_db.property_list, type=car_db.get_values_of_col(car_db.BODY_TYPE), colours=car_db.get_values_of_col(car_db.COLOUR), brands=car_db.get_values_of_col(car_db.BRAND), seats=car_db.get_values_of_col(car_db.SEATS))
            else:
                return flask.redirect(flask.url_for("forbidden"))


@app.route('/booking/cancel/<int:id>', methods=["POST", "GET"])
def delete_booking(id):
    """Remove the booking
    
    Parameters
    ----------
    id
        id of the booking
    """
    booking_db.cancel_booking(id)
    return flask.redirect(flask.url_for("booking"))


@app.route('/booking/modify/<int:id>', methods=["POST", "GET"])
def modify_booking(id):
    """Change the information of the booking
    
    Parameters
    ----------
    id
        Id of the booking to be changed
    """
    # Set the default values of attributes in the form
    attributes = {"error": False, "booked_before": False}
    old_records = booking_db.find_booking(**{booking_db.ID: id})
    attributes = {**attributes, **(old_records[0])}
    old_from, old_end = old_records[0].get(booking_db.FROM), old_records[0].get(booking_db.TO)
    attributes["from_date"], attributes["to_date"], attributes["from_time"], attributes["to_time"] = old_from.strftime('%Y-%m-%d'), old_end.strftime('%Y-%m-%d'), old_from.strftime('%H:%M'), old_end.strftime('%H:%M')

    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}

        # Process submitted attributes
        from_time, to_time = data["from_date"] + " " + data["from_time"] + ":00", data["to_date"] + " " + data["to_time"] + ":00"
        del data["from_date"], data["to_time"], data["from_time"], data["to_date"]

        # Check if from_time < to_time
        if (datetime.datetime.strptime(from_time, '%Y-%m-%d %H:%M:%S') >= datetime.datetime.strptime(to_time, '%Y-%m-%d %H:%M:%S')):
            attributes["error"] = True
            attributes["from_date"] = old_records[0][booking_db.FROM].split
            return flask.render_template("booking_infos.html", **attributes)

        # Try to insert into table booking
        try:
            # Perform action
            data[booking_db.FROM], data[booking_db.TO] = from_time, to_time
            booking_db.update_booking(id, **data)
        except Exception as e:
            print(e)
            attributes["booked_before"] = True
            return flask.render_template("booking_modify.html", **attributes)
        else:
            return flask.redirect(flask.url_for("home"))
    else:
        if flask.session.get("username", None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            print(attributes)
            return flask.render_template("booking_modify.html", **attributes)

@app.route('/booking/add', methods = ["GET", "POST"])
def booking_add():
    """Log the user into the system
    
    Parameters
    ----------
    error
        The modes to render the html page
    """
    attributes = {}
    attributes[BookingDatabase.CAR_ID] = list(set(car_db.get_values_of_col(car_db.ID)))
    attributes[BookingDatabase.USER_ID] = list(set(user_db.get_values_of_col(user_db.ID)))
    print(attributes)
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}

        # Process attributes
        from_time, to_time = data["from_date"] + " " + data["from_time"] + \
            ":00", data["to_date"] + " " + data["to_time"] + ":00"
        del data["from_date"], data["to_time"], data["from_time"], data["to_date"]
        if (datetime.datetime.strptime(from_time, '%Y-%m-%d %H:%M:%S') >= datetime.datetime.strptime(to_time, '%Y-%m-%d %H:%M:%S')):
            return flask.render_template("booking_add.html", message="Departure should be lower than Arrival", **attributes)

        try:
            # Perform action
            data[booking_db.FROM] = from_time
            data[booking_db.TO] = to_time
            booking_db.add_booking(**data)
        except Exception as e:
            return flask.render_template("booking_add.html", message=str(e), **attributes)
        else:
            return flask.redirect(flask.url_for("home"))
    else:
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:       
            return flask.render_template("booking_add.html", **attributes)


# Issues
@app.route('/issues', methods=["POST", "GET"])
def issues():
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {k: v for k, v in form_data.items() if v}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print("Data", data)

        role = flask.session.get(login_db.ROLES)
        if role == "engineer":
            data[issues_db.ENGINEER_ID] = flask.session.get(login_db.ID)
            records = issues_db.find_issues(**data)
            return flask.render_template("issues_engineer.html", all_issues=records, car_id_list=issues_db.get_values_of_col(issues_db.CAR_ID), engineer_id_list=issues_db.get_values_of_col(issues_db.ENGINEER_ID))
        elif role == "admin":
            records = issues_db.find_issues(**data)
            return flask.render_template("issues_admin.html", all_issues=records, car_id_list=issues_db.get_values_of_col(issues_db.CAR_ID), engineer_id_list=issues_db.get_values_of_col(issues_db.ENGINEER_ID))
        else:
            flask.redirect(flask.url_for("forbidden"))
    else:
        if flask.session.get("username", None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            role = flask.session.get(login_db.ROLES)
            if role == "engineer":
                params = {
                    issues_db.ENGINEER_ID: flask.session.get(login_db.ID)}
                issues = issues_db.find_issues(**params)
                all_issues = issues_db.get_all_issues()
                return flask.render_template("issues_engineer.html", my_issues=issues, all_issues=all_issues, car_id_list=issues_db.get_values_of_col(issues_db.CAR_ID), engineer_id_list=issues_db.get_values_of_col(issues_db.ENGINEER_ID))
            elif role == "admin":
                all_issues = issues_db.get_all_issues()
                return flask.render_template("issues_admin.html", all_issues=all_issues, car_id_list=issues_db.get_values_of_col(issues_db.CAR_ID), engineer_id_list=issues_db.get_values_of_col(issues_db.ENGINEER_ID))
            else:
                return flask.redirect(flask.url_for("forbidden"))


@app.route('/issues/add/<int:id>', methods=["GET"])
@app.route('/cars/report/<int:id>', methods=["GET"])
def cars_report(id):
    issues_db.add_issues(**{issues_db.CAR_ID: id})
    return flask.redirect(flask.url_for("issues"))


@app.route('/issues/cancel/<int:id>', methods=["GET"])
def cancel_issues(id):
    """Cancelling an issue
    
    Parameters
    ----------
    id
        id of the issue
    """
    issues_db.cancel_issues(id)
    return flask.redirect(flask.url_for("issues"))


@app.route('/issues/accept/<int:id>', methods=["GET"])
def accept_issues(id):
    issues_db.accept_issues(id, flask.session.get(login_db.ID))
    return flask.redirect(flask.url_for("issues"))


@app.route('/issues/complete/<int:id>', methods=["GET"])
def complete_issues(id):
    """Report that an issue is completed
    
    Parameters
    ----------
    id
        id of the completed issue
    """
    issues_db.complete_issues(id)
    return flask.redirect(flask.url_for("issues"))


# Cars
@app.route('/cars', methods=["GET", "POST"])
def cars():
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print(data)

        records = car_db.find_car(**data)
        return flask.render_template("cars_users.html", cars=records, type=car_db.get_values_of_col(car_db.BODY_TYPE), colours=car_db.get_values_of_col(car_db.COLOUR), brands=car_db.get_values_of_col(car_db.BRAND), seats=car_db.get_values_of_col(car_db.SEATS))
    else:
        if flask.session.get("username", None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            cars = car_db.get_all_car()

            # Change behaviour based on the ROLES
            role = flask.session.get(login_db.ROLES)
            if role == "user":
                return flask.render_template("cars_users.html", cars=cars, type=car_db.get_values_of_col(car_db.BODY_TYPE), colours=car_db.get_values_of_col(car_db.COLOUR), brands=car_db.get_values_of_col(car_db.BRAND), seats=car_db.get_values_of_col(car_db.SEATS))
            elif role == "admin":
                return flask.render_template("cars_admin.html", cars=cars, type=car_db.get_values_of_col(car_db.BODY_TYPE), colours=car_db.get_values_of_col(car_db.COLOUR), brands=car_db.get_values_of_col(car_db.BRAND), seats=car_db.get_values_of_col(car_db.SEATS))
            else:
                return flask.redirect(flask.url_for("forbidden"))


@app.route('/cars/delete/<int:id>', methods=["GET"])
def cars_delete(id):
    """Remove a car from the system
    
    Parameters
    ----------
    id
        The id of the car to be deleted
    """
    car_db.remove_car(id)
    return flask.redirect(flask.url_for("cars"))


@app.route('/cars/modify/<int:id>', methods=["POST", "GET"])
def cars_modify(id):
    """Change the information of a car
    
    Parameters
    ----------
    id
        id of the car to be modified
    """
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}

        records = car_db.update_car(id, **data)
        return flask.redirect(flask.url_for("cars"))
    else:
        if flask.session.get("username", None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            return flask.render_template("cars_modify.html", car_id=id)


# Users
@app.route('/users', methods=["POST", "GET"])
def users():
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {k: v for k, v in form_data.items() if v}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print("Data", data)

        role = flask.session.get(login_db.ROLES)
        if role == "admin":
            records = user_db.find_user(**data)
            return flask.render_template("users_admin.html", users=records)
        else:
            flask.redirect(flask.url_for("forbidden"))

    else:
        if flask.session.get("username", None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            role = flask.session.get(login_db.ROLES)
            if role == "admin":
                records = user_db.get_all()
                return flask.render_template("users_admin.html", users=records)
            else:
                return flask.redirect(flask.url_for("forbidden"))


@app.route('/users/delete/<int:id>', methods=["GET"])
def users_delete(id):
    """Delete a user from the system
    
    Parameters
    ----------
    id
        id of the user to be deleted
    """
    user_db.remove_user(id)
    return flask.redirect(flask.url_for("users"))


@app.route('/users/modify/<int:id>', methods=["POST", "GET"])
def users_modify(id):
    """Change the user information
    
    Parameters
    ----------
    id
        the id of the user to change
    """    
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print(data)

        records = user_db.update_user(id, **data)
        return flask.redirect(flask.url_for("users"))
    else:
        if flask.session.get("username", None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            return flask.render_template("users_modify.html", ID=id)


@app.route('/403', methods=["GET"])
def forbidden():
    """Render the forbidden page
    """
    return flask.render_template("403.html")


@app.route('/dashboard', methods=["GET"])
def dashboard():
    if flask.session.get("username", None) is None:
        return flask.redirect(flask.url_for("login"))
    elif flask.session.get(login_db.ROLES) != "manager":
        return flask.redirect(flask.url_for("forbidden"))
    else:
        # print("car_db.get_booked_car()", car_db.get_booked_car())
        return flask.render_template("dashboard.html", allCar=statistics_db.get_number_of_car()[0][0], bookedCar=statistics_db.get_booked_car()[0][0], freeCar=statistics_db.get_free_car()[0][0], issues=statistics_db.get_today_issues()[0][0], monthlyRevenues=statistics_db.get_monthly_revenue(), numberOfNewUsers=statistics_db.get_number_of_new_users())


# # AGENT PI
# @app.route('/agentPi/<int:car_id>', methods=["GET"])
# def agent_pi(car_id):
#     return flask.render_template("agentPi/agentPi.html", car_id=car_id)


# @app.route('/agentPi/<int:car_id>/users', methods=["GET"])
# def agent_pi_users(car_id):
#     return flask.render_template("/agentPi/agentPi_users.html", car_id=car_id)


# @app.route('/agentPi/<int:car_id>/users/normal', methods=["GET", "POST"])
# def agent_pi_users_normal(car_id):
#     if flask.request.method == "POST":
#         client_socket = socket_communication.Socket_Client()

#         form_data = flask.request.form.to_dict()
#         data = form_data
#         data[booking_db.CAR_ID] = car_id

#         print(data)

#         client_socket.send_message("Users".encode())
#         client_socket.receive_message()
#         client_socket.send_message("Normal".encode())
#         client_socket.receive_message()
#         client_socket.send_message(json.dumps(data).encode())
#         client_socket.receive_message()
#         return_message = client_socket.receive_message()

#         print("Return message:", return_message)

#         if return_message == "Correct":
#             return flask.redirect(flask.url_for("welcome", car_id=car_id))
#         else:
#             return flask.render_template("agentPi/agentPi_users_normal.html", car_id=car_id, message=return_message)

#     else:
#         return flask.render_template("agentPi/agentPi_users_normal.html", car_id=car_id, message="")


# @app.route('/agentPi/<int:car_id>/users/facial', methods=["GET", "POST"])
# def agent_pi_users_facial(car_id):
#     return "Facial Implementation"


# @app.route('/agentPi/<int:car_id>/engineers', methods=["GET"])
# def agent_pi_engineers(car_id):
#     return flask.render_template("/agentPi/agentPi_engineers.html", car_id=car_id)


# @app.route('/agentPi/<int:car_id>/engineers/normal', methods=["GET", "POST"])
# def agent_pi_engineers_normal(car_id):
#     if flask.request.method == "POST":
#         client_socket = socket_communication.Socket_Client()

#         form_data = flask.request.form.to_dict()
#         data = form_data
#         data[issues_db.CAR_ID] = car_id

#         print(data)

#         # Send and receive data back and forth
#         client_socket.send_message("Engineers".encode())
#         client_socket.receive_message()
#         client_socket.send_message("Normal".encode())
#         client_socket.receive_message()
#         client_socket.send_message(json.dumps(data).encode())
#         client_socket.receive_message()
#         return_message = client_socket.receive_message()

#         print("Return message:", return_message)

#         if return_message == "Correct":
#             return flask.redirect(flask.url_for("welcome", car_id=car_id))
#         else:
#             return flask.render_template("agentPi/agentPi_engineers_normal.html", car_id=car_id, message=return_message)

#     else:
#         return flask.render_template("agentPi/agentPi_engineers_normal.html", car_id=car_id, message="")


# @app.route('/login_agentPi/facial', methods=["GET"])
# def login_agent_pi_facial():
#     return "Waiting to implement"


# @app.route('/welcome/<int:car_id>', methods=["GET"])
# def welcome(car_id):
#     return flask.render_template("agentPi/welcome.html", car_id=car_id)


# @app.route('/login_agentPi/QR', methods=["GET", "POST"])
# def QR_detect():
#     return flask.render_template("QR_detect.html")

# Utility route
def image_generator(camera, UID):
    while True:
        yield camera.capture_faces(UID)

def camera_generator(camera, UID):
    #get camera frame
    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + next(image_generator(camera, UID)) + b'\r\n\r\n')


@app.route('/video', methods = ['GET'])
def video():
    # value = next(camera_generator(camera))
    # with open("temp", "r+b") as f:
    #     f.write(value)
    # if issubclass(value, bytes):
    #     frame = (b'--frame\r\n'
    #             b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') 
    return flask.Response(camera_generator(VideoCamera.VideoCamera(), flask.session.get(login_db.ID)), mimetype='multipart/x-mixed-replace; boundary=frame')
    # return flask.redirect(flask.url_for("home"))


@app.route('/welcome/<int:car_id>', methods = ["GET"])
def welcome(car_id):
    return flask.render_template("agentPi/welcome.html", car_id = car_id)

if __name__ == "__main__":
    app.run(debug=True)
