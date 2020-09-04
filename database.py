"""
                                BIG BIG NOTE: 
                    This code is only applied for SQLite only.
                        Needs to change into MySQL
"""
from google_calendar import GoogleCalendar
from abc import *
import flask
import datetime
import MySQLdb as SQLDatabase
"https://code.tutsplus.com/vi/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972"


#import sqlite3 as SQLDatabase

# On for online db, off for local db
mode = "On"

if mode == "Off":
    host = "localhost"
    user = "root"
    password = "h@angeSoftB1og"
    schema = "temps"
else:
    host = "35.247.132.39"
    user = "root"
    password = "h@angeSoftB1og"
    schema = "PIoT_Assignment_2"

USER_TABLE = "Account"
CAR_TABLE = "Car"
BOOKING_TABLE = "Booking"
EMPLOYEE_TABLE = "Employee"
ISSUES_TABLE = "Issues"
LOGIN_TABLE = "Login_Info"


class AbstractDatabase():
    # Abstract Class Implementation
    # @abstractproperty
    # def database(self):
    #     return NotImplemented

    # @abstractproperty
    # def host(self):
    #     return NotImplemented

    # @abstractproperty
    # def user(self):
    #     return NotImplemented

    # @abstractproperty
    # def password(self):
    #     return NotImplemented

    # __metaclass__ = ABCMeta

    def __init__(self):
        self.database = self.host = self.user = self.password = self.property_list = None

    def execute_no_return(self, query, data=None, connector_setting: tuple = None):
        # Prepare config settings to perform SQL
        # As some special operations required to have special configs
        if connector_setting is None:
            self.connector = SQLDatabase.connect(
                self.host, self.user, self.password, self.database)
        else:
            self.connector = SQLDatabase.connect(*connector_setting)

        self.cursor = self.connector.cursor()

        # Get the correct operation for writing SQL
        if data is not None:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

        # Finish the operation and close
        self.connector.commit()
        self.connector.close()
        # This will return the ID for some operation
        return self.cursor.lastrowid

    def execute_return(self, query, data=None, amount="many", connector_setting=None):
        # Prepare config settings to perform SQL
        # As some special operations required to have special configs
        if connector_setting is None:
            self.connector = SQLDatabase.connect(
                self.host, self.user, self.password, self.database)
        else:
            self.connector = SQLDatabase.connect(*connector_setting)

        self.cursor = self.connector.cursor()

        # Get the correct operation for writing SQL
        if amount == "many":
            fetch = self.cursor.fetchall
        elif amount == "one":
            fetch = self.cursor.fetchone
        else:
            fetch = self.cursor.fetchall

        if data is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, data)
        records = fetch()

        # Finish operation
        self.connector.close()
        return records

    def to_dictionary(self, data):
        if not data:
            return data
        elif isinstance(data[0], tuple):
            return [self.to_dictionary(child_data) for child_data in data]
        else:
            return dict(zip(self.property_list, data))


class LoginDatabase (AbstractDatabase):
    USERNAME = "username"
    PASSWORD = "password"
    ID = "ID"
    ROLES = "roles"

    property_list = [ID, USERNAME, PASSWORD, ROLES]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=LOGIN_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute_no_return(query)

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.USERNAME} varchar(50) unique, {self.PASSWORD} varchar(50), {self.ROLES} integer )"
        self.execute_no_return(query)

    def add_login(self, username, password, role=0):
        query = f"insert into {self.table} " + \
            " ({}, {}, {}) values (%s, %s, %s)".format(*self.property_list[1:])
        return self.execute_no_return(query=query, data=(username, password, role))

    def delete_login(self, id):
        """Delete statement will return 0. So no return instead"""
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query=query, data=(id,))

    def change_password(self, id, password):
        query = f"update {self.table} set {self.PASSWORD} = %s where {self.ID} = %s"
        return self.execute_no_return(query, (password, id))

    def find_login(self, username, password):
        query = f"select * from {self.table} where {self.USERNAME} = %s and {self.PASSWORD} = %s"
        records = self.execute_return(query, (username, password))
        return self.to_dictionary(records)

    def get_all_login(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)


class UserDatabase (AbstractDatabase):
    ID = "ID"
    NAME = "name"
    ADDRESS = "address"
    PHONE_NUMBER = "phone_number"
    property_list = [ID, NAME, ADDRESS, PHONE_NUMBER]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=USER_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute_no_return(query)

        table_property = f"{self.ID} INTEGER primary key, {self.NAME} varchar(100), {self.ADDRESS} varchar(200), {self.PHONE_NUMBER} varchar(20), foreign key ({self.ID}) references {LOGIN_TABLE} ({LoginDatabase.ID}) on update cascade on delete cascade"
        query = f"CREATE TABLE IF NOT EXISTS {self.table} " + \
            "(" + table_property + ")"
        self.execute_no_return(query)

    def add_user(self, id, name, address, phone_number):
        query = f"insert into {self.table} " + \
            " ({}, {}, {}, {}) values (%s, %s, %s, %s)".format(
                *self.property_list)
        return self.execute_no_return(query=query, data=(id, name, address, phone_number))

    def get_all(self):
        query = "select * from " + self.table
        records = self.execute_return(query)
        return self.to_dictionary(records)

    def find_user(self, id):
        query = f"select * from {self.table} where {self.ID} = %s"
        records = self.execute_return(query, (id,))
        return self.to_dictionary(records)

    def remove_user(self, user_id):
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (user_id,))

    def update_user(self, user_id, cols_update: tuple, new_values: tuple):
        if len(cols_update) != len(new_values):
            raise Exception(f"Number of rows and numbers of new values are not equal. " +
                            str({len(cols_update)}) + " " + str({len(new_values)}))
        else:
            pass

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values)
        params.append(str(user_id))
        return self.execute_no_return(query, params)


class CarDatabase (AbstractDatabase):
    BRAND = "brand"
    MAKE = BRAND
    BODY_TYPE = "body_type"
    COLOUR = "colour"
    SEATS = "seats"
    LOCATION = "location"
    COST_PER_HOUR = "cost_per_hour"
    ID = "ID"
    property_list = [ID, BRAND, BODY_TYPE,
                     COLOUR, SEATS, LOCATION, COST_PER_HOUR]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=CAR_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.BRAND} varchar(20), {self.BODY_TYPE} varchar(30), {self.COLOUR} varchar(40), {self.SEATS} numeric, {self.LOCATION} varchar(100), {self.COST_PER_HOUR} numeric)"
        self.execute_no_return(query)

    def insert_car(self, brand, body, color, seats, location, cost):
        query = f"""insert into {self.table} ({self.BRAND}, {self.BODY_TYPE}, {self.COLOUR}, {self.SEATS}, {self.LOCATION}, {self.COST_PER_HOUR}) 
        values(%s, %s, %s, %s, %s, %s)"""

        return self.execute_no_return(query, (brand, body, color, seats, location, cost))

    def get_all_car(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)

    def find_car(self, search_term: str):
        query = f"""select * from {self.table} 
        where {self.BRAND} LIKE %s OR {self.BODY_TYPE} LIKE %s OR {self.COLOUR} LIKE %s OR {self.LOCATION} LIKE %s"""

        records = self.execute_return(query, tuple(
            [("%" + search_term + "%") for i in range(4)]))

        if search_term.isnumeric():
            query = f"""select * from {self.table} 
            where {self.SEATS} = %s OR {self.COST_PER_HOUR} = %s"""
            records_2 = self.execute_return(
                query, tuple([search_term for i in range(2)]))
            records.extend(records_2)

        return self.to_dictionary(records)

    def remove_car(self, car_id):
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (car_id,))

    def update_car(self, car_id, cols_update: tuple, new_values: tuple):
        if len(cols_update) != len(new_values):
            raise Exception(
                "Number of rows and numbers of new values are not equal.")
        else:
            pass

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values)
        params.append(str(car_id))
        return self.execute_no_return(query, params)


# Between car and user
class BookingDatabase(AbstractDatabase):
    ID = "ID"
    USER_ID = "UID"
    CAR_ID = "Car_ID"
    BOOKING_DETAIL = "booking_details"
    FROM = "from_time"
    TO = "to_time"
    EVENT_ID_CALENDAR = "id_on_google_calendar"
    property_list = [ID, CAR_ID, USER_ID,
                     BOOKING_DETAIL, FROM, TO, EVENT_ID_CALENDAR]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=BOOKING_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password
        self.calendar = GoogleCalendar()

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int not null, {self.USER_ID} int not null, {self.BOOKING_DETAIL} text, {self.FROM} datetime, {self.TO} datetime, {self.EVENT_ID_CALENDAR} varchar(50), foreign key({self.USER_ID}) references {USER_TABLE}({UserDatabase.ID}), foreign key({self.CAR_ID}) references {CAR_TABLE}({CarDatabase.ID}))"
        self.execute_no_return(query)

    def add_booking(self, car_id, user_id, booking_detail, from_time, to_time):
        # Check for anyone who rent at the moment first
        query = f"""select * from (select * from {self.table} where {self.CAR_ID} = %s) as b where not (b.{self.FROM} >= %s or b.{self.TO} <= %s)"""
        records = self.execute_return(query, (car_id, to_time, from_time))

        # If there is no one booking, then add booking
        if len(records) > 0:
            raise Exception("This car has been booked at this time.")
        else:
            # Add to Google Calendar first
            response = self.calendar.add_event(user_id, car_id, datetime.datetime.strptime(
                from_time, "%Y-%m-%d %H:%M:%S"), datetime.datetime.strptime(to_time, "%Y-%m-%d %H:%M:%S"), booking_detail)
            event_id = response["id"]

            query = f"insert into {self.table} " + \
                " ({}, {}, {}, {}, {}, {}) values(%s, %s, %s, %s, %s, %s)".format(
                    *self.property_list[1:])
            return self.execute_no_return(query, (car_id, user_id, booking_detail, from_time, to_time, event_id))

    def get_all_booking(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)

    def cancel_booking(self, booking_id):
        # Get the Calendar ID for booking
        query = f"select * from {self.table} where {self.ID} = %s"
        records = self.execute_return(query, (booking_id, ))
        event_calendar_id = records[0][-1]

        # Cancel on Google Calendar
        self.calendar.cancel_event(event_calendar_id)

        # Cancel on database
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (booking_id,))
        print("Cancel booking ", booking_id)


class EmployeesDatabase(AbstractDatabase):
    ID = "ID"
    NAME = "name"
    property_list = [ID, NAME]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=EMPLOYEE_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key references {LOGIN_TABLE}({LoginDatabase.ID}), {self.NAME} varchar(100))"
        self.execute_no_return(query)

    def add_employee(self, id, name):
        query = f"insert into {self.table} " + \
            " ({}, {}) values (%s, %s)".format(*self.property_list)
        return self.execute_no_return(query, (id, name))

    def get_all(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)

    def update_employee(self, employee_id, cols_update: tuple, new_values: tuple):
        if len(cols_update) != len(new_values):
            raise Exception(
                "Number of rows and numbers of new values are not equal.")
        else:
            pass

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values)
        params.append(str(employee_id))
        return self.execute_no_return(query, params)


class IssuesDatabase(AbstractDatabase):
    CAR_ID = "Car_ID"
    ID = "ID"
    ENGINEER_ID = "Engineer_ID"
    STATUS = "Done"
    LOCATION = "Location"
    MESSAGE = "Message"
    property_list = [ID, CAR_ID, ENGINEER_ID, LOCATION, STATUS, MESSAGE]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=ISSUES_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int not null, {self.ENGINEER_ID} int not null, {self.LOCATION} varchar(100), {self.STATUS} boolean, {self.MESSAGE} text, foreign key({self.ENGINEER_ID}) references {EMPLOYEE_TABLE}({EmployeesDatabase.ID}), foreign key({self.CAR_ID}) references {CAR_TABLE}({CarDatabase.ID}))"
        self.execute_no_return(query)

    def add_issues(self, car_id, engineer_id, location, message):
        query = f"insert into {self.table} " + \
            " ({}, {}, {}, {}, {}) values (%s, %s, %s, %s, %s)".format(
                *self.property_list[1:])
        self.execute_no_return(
            query, (car_id, engineer_id, location, False, message))

    def complete_issues(self, car_id, engineer_id):
        query = f"update {self.table} set {self.STATUS} = true where {self.CAR_ID} = %s and {self.ENGINEER_ID} = %s"
        self.execute_no_return(query, (car_id, engineer_id))


if __name__ == "__main__":
    # Drop schema first
    connector = SQLDatabase.connect(host, user, password)
    cursor = connector.cursor()
    query = f"drop database if exists {schema}"
    cursor.execute(query)
    connector.commit()
    connector.close()

    # Login Database
    # Role 0 is User
    # Role 1 is Engineer
    # Role 2 is Manager
    # Role 3 is Admin
    login_db = LoginDatabase()
    print(login_db.add_login("hoangafublog@email.com", "112358", 0))
    print(login_db.add_login("hoang", "159753", 1))
    print(login_db.add_login("hoangesoftblog", "1", 2))
    print(login_db.add_login("hello", "123456", 3))
    print(login_db.add_login("random", "rand", 0))
    print(login_db.change_password(3, "1010101"))
    print(login_db.delete_login(5))
    print(login_db.get_all_login())
    print(login_db.find_login("hello", "123456"))

    # User Database
    user_db = UserDatabase()
    user_db.add_user(1, "hoang truong", "Thu Duc, TP.HCM", "0973557408")
    print(user_db.find_user(2))
    user_db.remove_user(6)
    user_db.update_user(4, cols_update=(user_db.NAME,),
                        new_values=("Viet Nam oi",))
    print(user_db.get_all())

    # Car database
    car_db = CarDatabase()
    car_db.insert_car("Honda Civic", "Sedan", "Black",
                      "4", "Thu Duc", "1000000")
    car_db.insert_car("Toyota Camry", "Sedan", "Brown", "5", "Q1", "1500000")
    car_db.insert_car("Fortuner", "Something", "Green", "7", "Q1", "2000000")
    car_db.insert_car("Random", "Random", "Random", "10", "Vietnam", "500000")
    print(car_db.get_all_car())
    print(car_db.find_car(""))
    print(car_db.update_car(
        4, [car_db.BRAND, car_db.BODY_TYPE], ("Zoros", "Unicycle")))
    car_db.remove_car(4)
    print(car_db.get_all_car())

    # Booking database
    booking_db = BookingDatabase()
    booking_db.add_booking(2, 1, "Hello, it's me!",
                           '2020-08-24 13:10:10', '2020-08-25 14:10:10')
    booking_db.add_booking(1, 1, "I want to borrow it!",
                           '2020-08-24 05:10:10', '2020-08-26 09:10:10')
    booking_db.add_booking(
        3, 1, "1234", '2020-06-01 10:10:10', '2020-06-30 10:10:10')
    print(booking_db.get_all_booking())
    booking_db.cancel_booking(3)

    # Employees database
    employee_db = EmployeesDatabase()
    employee_db.add_employee(2, "Dang Dinh Khanh")
    employee_db.add_employee(3, "Tui la tui chu la ai")
    employee_db.add_employee(4, "Duc la tui")
    print(employee_db.get_all())

    # Issues Database
    issues_db = IssuesDatabase()
    issues_db.add_issues(2, 2, "Nha phan phoi duy long", "Please fix it soon")

    # ###### Test set
    # # # Test for add same username - table Account
    # # account_db.add_user("hoangesoftblog", "h@angeSoftB1og", "hoang truong", "Thu Duc, TP.HCM", "0973557408")

    # # # Test add booking overlap - Table Booking
    # # booking_db.add_booking(2, 3, "Let's go to Vung Tau!", '2020-08-01 13:00:00', '2020-08-01 14:05:10')
