import flask
from database import *
import json
import time
import flask_mail
import qr_code
import socket_communication
import camera as VideoCamera
import base64
from werkzeug.utils import secure_filename
import google_cloud_storage
import os


app = flask.Flask(__name__)
app.secret_key = "jose"
# socket_communication.tcp_start_server()

# Config the mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "hoangesoftblog@gmail.com"
app.config['MAIL_PASSWORD'] = "ndfl xduk ahqr jexj"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = flask_mail.Mail(app)

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




# https://blog.tecladocode.com/how-to-add-user-logins-to-your-flask-website/


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
        records = login_db.login_existed(**flask.request.form.to_dict())
        print(records)
        if len(records) != 1:
            return flask.render_template("login.html", error=True)
        else:
            flask.session[login_db.USERNAME] = records[0][login_db.USERNAME]
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
        if flask.session.get(login_db.USERNAME) == None:
            return flask.render_template("register.html", **attributes)
        else:
            return flask.redirect(flask.url_for("home"))
    else:
        form_data = flask.request.form.to_dict()
        data = form_data
        # data = {key: val for key, val in form_data.items() if val}
        # data = {k: (v if v != "None" else None) for k, v in data.items()}

        username, password, password_confirmed = data.get(
            "email"), data.get("password"), data.get("password2")
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
        user_db.add_user(**{user_db.ID: user_id})

        return flask.redirect(flask.url_for("home"))


@app.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    """Render the forget password page

    """
    if flask.request.method == "GET":
        return flask.render_template("forget_password.html")
    else:
        return "Not done yet"


@app.route('/user_setting', methods = ["GET", "POST"])
def update_info():
    """Update the user setting
    
    """
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}

        user_db.update_user(flask.session.get(login_db.ID), **data)
        return flask.redirect(flask.url_for("home"))
    else:
        records = user_db.find_user(**{user_db.ID: flask.session.get(login_db.ID)})
        return flask.render_template("user_setting.html", **(records[0]))


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
    """Show the calendar of booking info of the car
    
    Parameters
    ----------
    car_id
        The id of the car to check
    """
    attributes = {"error": False, "booked_before": False}
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}

        records = car_db.to_dictionary(car_db.execute_return(
            f"select * from {car_db.table} where {car_db.ID} = %s", (car_id, )), attribute_list=car_db.property_list)
        attributes["car_id"] = car_id
        attributes["lat"] = records[0][car_db.LAT]
        attributes["lng"] = records[0][car_db.LNG]

        # Process attributes
        from_time, to_time = data["from_date"] + " " + data["from_time"] + \
            ":00", data["to_date"] + " " + data["to_time"] + ":00"
        del data["from_date"], data["to_time"], data["from_time"], data["to_date"]
        if (datetime.datetime.strptime(from_time, '%Y-%m-%d %H:%M:%S') >= datetime.datetime.strptime(to_time, '%Y-%m-%d %H:%M:%S')):
            attributes["error"] = True
            return flask.render_template("booking_infos.html", **attributes)

        try:
            # Perform action
            data[booking_db.CAR_ID] = car_id
            data[booking_db.USER_ID] = flask.session.get(login_db.ID)
            data[booking_db.FROM] = from_time
            data[booking_db.TO] = to_time
            booking_db.add_booking(**data)
        except Exception as e:
            print(e)
            # print(flask.session.get(login_db.ID))
            attributes["booked_before"] = True
            return flask.render_template("booking_infos.html", **attributes)

        return flask.redirect(flask.url_for("home"))
    else:
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            records = car_db.to_dictionary(car_db.execute_return(
                f"select * from {car_db.table} where {car_db.ID} = %s", (car_id, )), attribute_list=car_db.property_list)
            attributes["car_id"] = car_id
            attributes["lat"] = records[0][car_db.LAT]
            attributes["lng"] = records[0][car_db.LNG]

            return flask.render_template("booking_infos.html", **attributes)


@app.route('/booking_history', methods=["GET", "POST"])
def booking():
    """Book the car for the user

    """
    all_bookings = booking_db.get_all_booking()

    # Add keys and values for render_template
    attributes = {}
    attributes["location"] = list(set([i.get(CarDatabase.LOCATION) for i in all_bookings if i.get(CarDatabase.LOCATION)]))
    attributes["colours"] = list(set([i.get(CarDatabase.COLOUR) for i in all_bookings if i.get(CarDatabase.COLOUR)]))
    attributes[BookingDatabase.USER_ID] = list(set([i.get(BookingDatabase.USER_ID) for i in all_bookings if i.get(BookingDatabase.USER_ID)]))
    attributes["brands"] = list(set([i.get(CarDatabase.BRAND) for i in all_bookings if i.get(CarDatabase.BRAND)]))
    attributes["colours"] = list(set([i.get(CarDatabase.COLOUR) for i in all_bookings if i.get(CarDatabase.COLOUR)]))
    attributes["seats"] = list(set([i.get(CarDatabase.SEATS) for i in all_bookings if i.get(CarDatabase.SEATS)]))

    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print(data)

        role = flask.session.get(login_db.ROLES)
        if role == "user":
            data[BookingDatabase.USER_ID] = flask.session.get(login_db.ID)
            records = booking_db.find_booking(**data)
            attributes["history"] = records
            return flask.render_template("booking_history.html", **attributes)
        elif role == "admin":
            records = booking_db.find_booking(**data)   
            attributes["history"] = records       
            return flask.render_template("rental_history.html", **attributes)
        else:
            return flask.redirect(flask.url_for("forbidden"))
    else:
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            role = flask.session.get(login_db.ROLES)
            if role == "user":
                params = {BookingDatabase.USER_ID: flask.session.get(login_db.ID)}
                records = booking_db.find_booking(**params)
                attributes["history"] = records
                return flask.render_template("booking_history.html", **attributes)
            elif role == "admin":
                attributes["history"] = all_bookings
                return flask.render_template("rental_history.html", **attributes)
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
        if flask.session.get(login_db.USERNAME, None) is None:
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
    """Render the page with car issues
    
    """
    attributes = {}
    if flask.request.method == "POST":
        # Get submitted form data
        # Remove keys with empty values
        # and change "None" values into None
        form_data = flask.request.form.to_dict()
        data = {k: v for k, v in form_data.items() if v}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print("Data", data)

        role = flask.session.get(login_db.ROLES)
        if role == "engineer":
            data[issues_db.ENGINEER_ID] = flask.session.get(login_db.ID)
            records = issues_db.find_issues(**data)

            # Add keys, values for attributes
            attributes['all_issues'] = records
            attributes['car_id_list'] = issues_db.get_values_of_col(
                issues_db.CAR_ID)
            # attributes['location_list'] = issues_db.get_values_of_col(car_db.LOCATION)
            # attributes['status'] = issues_db.get_values_of_col(issues_db.STATUS)
            return flask.render_template("issues_engineer.html", **attributes)
        elif role == "admin":
            records = issues_db.find_issues(**data)

            # Add keys, values for attributes
            attributes['all_issues'] = records
            attributes['car_id_list'] = issues_db.get_values_of_col(
                issues_db.CAR_ID)
            attributes['engineer_id_list'] = issues_db.get_values_of_col(
                issues_db.ENGINEER_ID)
            # attributes['location_list'] = issues_db.get_values_of_col(car_db.LOCATION)
            # attributes['status'] = issues_db.get_values_of_col(issues_db.STATUS)
            return flask.render_template("issues_admin.html", **attributes)
        else:
            flask.redirect(flask.url_for("forbidden"))
    else:
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            role = flask.session.get(login_db.ROLES)
            if role == "engineer":
                params = {
                    issues_db.ENGINEER_ID: flask.session.get(login_db.ID)}
                issues = issues_db.find_issues(**params)
                all_issues = issues_db.get_all_issues()

                # Add keys, values for attributes
                attributes['all_issues'] = all_issues
                attributes['car_id_list'] = issues_db.get_values_of_col(
                    issues_db.CAR_ID)
                attributes['engineer_id_list'] = issues_db.get_values_of_col(
                    issues_db.ENGINEER_ID)
                attributes["my_issues"] = issues
                # attributes['location_list'] = issues_db.get_values_of_col(car_db.LOCATION)
                # attributes['status'] = issues_db.get_values_of_col(issues_db.STATUS)
                return flask.render_template("issues_engineer.html", **attributes)
            elif role == "admin":
                all_issues = issues_db.get_all_issues()

                # Add keys, values for attributes
                attributes['all_issues'] = all_issues
                attributes['car_id_list'] = issues_db.get_values_of_col(
                    issues_db.CAR_ID)
                attributes['engineer_id_list'] = issues_db.get_values_of_col(
                    issues_db.ENGINEER_ID)
                # attributes['location_list'] = issues_db.get_values_of_col(car_db.LOCATION)
                # attributes['status'] = issues_db.get_values_of_col(issues_db.STATUS)
                return flask.render_template("issues_admin.html", **attributes)
            else:
                return flask.redirect(flask.url_for("forbidden"))


@app.route('/issues/add/<int:id>', methods=["GET"])
@app.route('/cars/report/<int:id>', methods=["GET"])
def cars_report(id):
    """Report that a car has issues
    
    Parameters
    ----------
    id
        The id of the car
    """
    # This is difficult because if there is no Issues in the DB
    # The normal query used for this return nothing

    # First, get the total of employees
    query = f"select distinct({employee_db.table}.{employee_db.ID}), {login_db.USERNAME} from {employee_db.table}, {login_db.table} where {employee_db.table}.{employee_db.ID} = {login_db.table}.{login_db.ID} and {login_db.table}.{login_db.ROLES} = 'engineer'"
    engineers_with_email = dict(employee_db.execute_return(query))
    list_engineer = list(engineers_with_email.keys())

    # Then get the amount of Issues each Engineer has
    query = f"select {issues_db.ENGINEER_ID}, count({issues_db.ENGINEER_ID}) from {issues_db.table}, {login_db.table} where {login_db.ID} = {issues_db.ENGINEER_ID} group by {issues_db.ENGINEER_ID}"
    amount_of_issues = dict(issues_db.execute_return(query))
    amount_of_issues = {k: amount_of_issues.get(k, 0) for k in list_engineer}

    e_id = min(amount_of_issues.items(), key=lambda x: x[1])[0]
    issues_db.add_issues(**{issues_db.CAR_ID: id, issues_db.ENGINEER_ID: e_id})

    new_message = flask_mail.Message(f"New issues with Car {id}",
                                     sender=flask.session.get(
                                         login_db.USERNAME),
                                     recipients=[engineers_with_email[e_id]]
                                     )
    mail.send(new_message)
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


# @app.route('/issues/accept/<int:id>', methods = ["GET"])
# def accept_issues(id):
#     issues_db.accept_issues(id, flask.session.get(login_db.ID))
#     return flask.redirect(flask.url_for("issues"))


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
    """Render the car page for user or admins
    
    """
    attributes = {}
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print(data)

        records = car_db.find_car(**data)

        # Add keys, values for attributes
        attributes['cars'] = records
        attributes['brands'] = car_db.get_values_of_col(car_db.BRAND)
        attributes['seats'] = car_db.get_values_of_col(car_db.SEATS)
        attributes['type'] = car_db.get_values_of_col(car_db.BODY_TYPE)
        attributes['colours'] = car_db.get_values_of_col(car_db.COLOUR)
        return flask.render_template("cars_users.html", **attributes)
    else:
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            # Add keys, values for attributes
            attributes['brands'] = car_db.get_values_of_col(car_db.BRAND)
            attributes['seats'] = car_db.get_values_of_col(car_db.SEATS)
            attributes['cars'] = car_db.get_all_car()
            attributes['type'] = car_db.get_values_of_col(car_db.BODY_TYPE)
            attributes['colours'] = car_db.get_values_of_col(car_db.COLOUR)

            # Change behaviour based on the ROLES
            role = flask.session.get(login_db.ROLES)
            if role == "user":
                return flask.render_template("cars_users.html", **attributes)
            elif role == "admin":
                return flask.render_template("cars_admin.html", **attributes)
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


@app.route('/cars/add', methods=["GET", "POST"])
def add_car():
    """Adding a car to the system
    
    """
    if flask.request.method == "POST":
        # Handle normal form data
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print("Data:", data)

        print("Request files:", flask.request.files.to_dict())
        # Handle the upload images
        if car_db.IMAGE not in flask.request.files:
            print("No images upload")
        
        # Retrieve real files in the requests
        upload_file = flask.request.files.get(car_db.IMAGE)
        if upload_file and allowed_file(upload_file.filename):
            # Upload file
            filename = secure_filename(upload_file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            upload_file.save(file_path)
            file_url = cloud_storage.upload_file_and_return_url(file_path, filename)
            # Delete file created temporarily
            if os.path.exists(file_path):
                os.remove(file_path)

            # Insert data into database
            data[car_db.IMAGE] = file_url
            records = car_db.insert_car(**data)
            return flask.redirect(flask.url_for("cars"))
        else:
            # Insert data into database
            records = car_db.insert_car(**data)
            # return flask.redirect(flask.url_for("cars"))
            return flask.render_template("cars_add.html", message = "File is not chosen")
    else:
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            return flask.render_template("cars_add.html")


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
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            return flask.render_template("cars_modify.html", **(car_db.find_car(**{car_db.ID: id})[0]))


# Users
@app.route('/users', methods=["POST", "GET"])
def users():
    """print 
    
    Parameters
    ----------
    error
        The modes to render the html page
    """
    attributes = {}
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {k: v for k, v in form_data.items() if v}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print("Data", data)

        role = flask.session.get(login_db.ROLES)
        if role == "admin":
            records = user_db.find_user(**data)

            # Add keys, values for attributes
            return flask.render_template("users_admin.html", users=records)
        else:
            flask.redirect(flask.url_for("forbidden"))

    else:
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            role = flask.session.get(login_db.ROLES)
            if role == "admin":
                records = user_db.get_all()
                return flask.render_template("users_admin.html", users=records)
            else:
                return flask.redirect(flask.url_for("forbidden"))


@app.route('/users/add', methods=["GET", "POST"])
def users_add():
    """Add a user to the system
    
    """
    if flask.request.method == "POST":
        form_data = flask.request.form.to_dict()
        data = {key: val for key, val in form_data.items() if val}
        data = {k: (v if v != "None" else None) for k, v in data.items()}
        print(data)
        
        login_keys, user_keys = [login_db.USERNAME, login_db.PASSWORD], [user_db.NAME, user_db.ADDRESS, user_db.PHONE_NUMBER]
        try:
            new_id = login_db.add_login(**{k: data.get(k) for k in login_keys})
            records = user_db.add_user(**{user_db.ID: new_id}, **{k: data.get(k) for k in user_keys})
        except Exception as e:
            return flask.render_template("users_add.html", message = "Email has been existed before")
        else:
            return flask.redirect(flask.url_for("users"))
    else:
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            return flask.render_template("users_add.html")


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
        if flask.session.get(login_db.USERNAME, None) is None:
            return flask.redirect(flask.url_for("login"))
        else:
            print(user_db.find_user(**{user_db.ID: id}))
            return flask.render_template("users_modify.html", **(user_db.find_user(**{user_db.ID: id})[0]))


@app.route('/403', methods=["GET"])
def forbidden():
    """Render the forbidden page
    """
    return flask.render_template("403.html")


@app.route('/dashboard', methods=["GET"])
def dashboard():
    """Render the dashboard
    """
    if flask.session.get(login_db.USERNAME, None) is None:
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    # import threading
    # try: 
    #     thread_main = threading.Thread(target=app.run, args={"debug": True})
    #     thread_main.start()
    #     thread_main = threading.Thread(target=socket_communication.tcp_start_server)
    #     thread_main.start()
    # except Exception as e:
    #     print(e)
    app.run(debug=True)
