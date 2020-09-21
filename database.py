# """https://code.tutsplus.com/vi/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972"""

import MySQLdb as SQLDatabase
# import sqlite3 as SQLDatabase
import datetime
# from abc import *
from google_calendar import GoogleCalendar
import flask_bcrypt

mode = "Off"

if mode != "On":
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
    """An Abstract Database, served as a standard for other databases

    """

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
        """Abstract database variables initialization

        """
        self.database = self.host = self.user = self.password = self.property_list = self.table = None

    def execute_no_return(self, query, data=None, connector_setting: tuple = None):
        """Execute query on the database, return the row id, but does not return the records
        ...
        :param query: the query command to be executed
        :type query: string
        :param data: the data to put into the query
        :type data: string
        :param connector_setting: the setting for the connector to initialize
        :type connector: string
        ...
        :return: the id of the last row of the database
        :rtype: int
        """
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
        """Execute query on the MySQL database, and return the records
        ...
        :param query: the query command to be executed
        :type query: string
        :param data: the data to put into the query
        :type data: string
        :param amount: choose to either fetch one of the query or fetch all of the found query
        :type amount: "many" or "one" string
        :param connector_setting: the setting for the connector to initialize
        :type connector: string
        ...
        :return: the record(s) found by the query
        :rtype: a dict of resulted query
        """
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

    def to_dictionary(self, data, attribute_list=None):
        """Return the dict data type of input data and attributee
        ...
        :param data: the data of attribute
        :type data: string
        :param attribute_list: the list of attribute that you want to add to the data
        :type attribute_list: string
        ...
        :return: the dict type of attributes and its data
        :rtype: tuple
        """
        attribute_list = attribute_list if attribute_list else self.property_list
        # print("The list is:", attribute_list)

        if not data:
            return data
        elif isinstance(data[0], tuple):
            return [self.to_dictionary(child_data, attribute_list) for child_data in data]
        else:
            return dict(zip(attribute_list, data))

    def get_values_of_col(self, col_name):
        query = f"select distinct({col_name}) from {self.table}"
        records = self.execute_return(query)
        return [record[0] for record in records]


class LoginDatabase (AbstractDatabase):
    """The Login and Register database
    """
    USERNAME = "email"
    EMAIL = USERNAME
    PASSWORD = "password"
    ID = "ID"
    ROLES = "roles"

    property_list = [ID, USERNAME, PASSWORD, ROLES]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=LOGIN_TABLE, drop_existing_table=False):
        """Init class"""
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

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.USERNAME} varchar(100) unique, {self.PASSWORD} varchar(100), {self.ROLES} varchar(15) )"
        self.execute_no_return(query)

    def add_login(self, email, password, role="user"):
        """Register a new user
        
        Parameters
        ----------
        username
            The username of the new user
        password
            The password of the new user
        role
            The role of the user, string "user", "manager", "admin" or "engineer"
        """
        # The password needed to be hashed first before being put into the DB
        hashed_password = flask_bcrypt.bcrypt.hashpw(password.encode(
            'utf-8'), flask_bcrypt.bcrypt.gensalt()).decode('utf-8')
        query = f"insert into {self.table} " + \
            " ({}, {}, {}) values (%s, %s, %s)".format(*self.property_list[1:])
        return self.execute_no_return(query=query, data=(email, hashed_password, role))

    def delete_login(self, id):
        """Delete a user
        
        Parameters
        ----------
        id
            The id of the user to be deleted
        """

        """Delete statement will return 0. So no return instead"""
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query=query, data=(id,))

    def change_password(self, id, password):
        """Change password of a user
        
        Parameters
        ----------
        id
            The id of the user to be deleted
        password
            The new password
        """
        hashed_password = flask_bcrypt.bcrypt.hashpw(password.encode('utf-8'), flask_bcrypt.bcrypt.gensalt()).decode('utf-8')
        query = f"update {self.table} set {self.PASSWORD} = %s where {self.ID} = %s"
        return self.execute_no_return(query, (hashed_password, id))

    def login_existed(self, email, password):
        """Get the information of a user based on their username and password
        
        Parameters
        ----------
        email
            The email of the user to be found
        password
            The password of the user to be found
        """
        query = f"select * from {self.table} where {self.USERNAME} = %s"
        print(query)
        record = self.to_dictionary(
            self.execute_return(query, (email, ), amount="one"))
        if record is None:
            return []
        else:
            stored_password = record.get(self.PASSWORD).encode('utf-8')
            if flask_bcrypt.bcrypt.checkpw(password.encode('utf-8'), stored_password):
                return [record]
            else:
                return []

    def get_all_login(self):
        """Get the information of a user based on their username and password
        
        Parameters
        ----------
        email
            The email of the user to be found
        password
            The password of the user to be found
        """
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)


class UserDatabase (AbstractDatabase):
    ID = "USER_ID"
    NAME = "name"
    ADDRESS = "address"
    PHONE_NUMBER = "phone_number"
    CREATED_DATE = "created_date"
    property_list = [ID, NAME, ADDRESS, PHONE_NUMBER, CREATED_DATE]

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

        table_property = f"{self.ID} INTEGER primary key, {self.NAME} varchar(100), {self.ADDRESS} varchar(200), {self.PHONE_NUMBER} varchar(20), foreign key ({self.ID}) references {LOGIN_TABLE} ({LoginDatabase.ID}) on update cascade on delete cascade " + f", {self.CREATED_DATE} datetime"
        query = f"CREATE TABLE IF NOT EXISTS {self.table} " + \
            "(" + table_property + ")"
        self.execute_no_return(query)

    def add_user(self, **property_list):
        """Add a new customer
        
        Parameters
        ----------
        property_list
            the information of the user, should be in the property_list dict
        """
        if not property_list.get(self.CREATED_DATE):
            property_list[self.CREATED_DATE] = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
        query = f"insert into {self.table} ({', '.join(property_list.keys())}) values ({', '.join([' %s ' for i in range(len(property_list.keys()))])})"

        return self.execute_no_return(query=query, data=property_list.values())

    def get_all(self):
        """Get The dictionary containt all the customers
        
        """
        query = "select * from " + self.table
        records = self.execute_return(query)
        return self.to_dictionary(records)

    def find_user(self, **search_params):
        """Find a user based on input parameters
        
        Parameters
        ----------
        search_term
            The parameters to search for
        """
        null_keys = [key for key in search_params.keys(
        ) if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys(
        ) if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys(
        ) if key not in null_keys + numeric_keys]

        if len(search_params.keys()) > 0:
            # Building the search query and the parameters
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + \
                [search_params[key]
                    for key in numeric_keys] + [None for key in null_keys]

            # query is the base
            # where_clause is for join table
            # additional_where_clause is for real search params
            query = f"""select * from {self.table}  """
            where_clause = f""" where 1 """
            additional_where_clause = ("and" if remaining_keys else "") + f" {' and '.join([key + ' like %s ' for key in remaining_keys])} " + ("and" if numeric_keys else "") + \
                f" {' and '.join([key + ' = %s ' for key in numeric_keys])} " + (
                    "and" if null_keys else "") + f" {' and '.join([key + ' is %s ' for key in null_keys])} "
            records = self.execute_return(
                query + where_clause + additional_where_clause, parameters)
            return self.to_dictionary(records)
        else:
            return self.get_all()

    def remove_user(self, user_id):
        """Remove a user based on their id
        
        Parameters
        ----------
        user_id
            id of the user to be deleted
        """
        
        query = f"delete from {LOGIN_TABLE} where {LoginDatabase.ID} = %s"
        self.execute_no_return(query, (user_id,))

    def update_user(self, user_id, **update_values):
        """Update the parameters of a user
        
        Parameters
        ----------
        user_id
            id of the user to be updated
        update_values
            the parameters to be updated and their new values in dict form
        """
        cols_update, new_values = update_values.keys(), update_values.values()

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
    ID = "CAR_ID"
    LAT = "lat"
    LNG = "lng"
    IMAGE = "image"
    BEING_USED = "being_used"
    property_list = [ID, BRAND, BODY_TYPE, COLOUR,
                     SEATS, LOCATION, COST_PER_HOUR, LAT, LNG, IMAGE, BEING_USED]

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

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.BRAND} varchar(100), {self.BODY_TYPE} varchar(30), {self.COLOUR} varchar(40), {self.SEATS} numeric, {self.LOCATION} varchar(100), {self.COST_PER_HOUR} numeric, {self.LAT} float, {self.LNG} float, {self.IMAGE} text, {self.BEING_USED} bool )" 
        self.execute_no_return(query)

    def insert_car(self, **property_list):
        """Add the the new car to the database
        
        Parameters
        ----------
        property_list
            the information of the car, should be in the self.property_list array
        """
        if self.BEING_USED not in property_list:
            property_list[self.BEING_USED] = False

        query = f"insert into {self.table} ({', '.join(property_list.keys())}) values ({', '.join([' %s ' for i in range(len(property_list.values()))])} )"
        return self.execute_no_return(query, list(property_list.values()))

    def get_all_car(self):
        """Get all cars in dict form
        
        """
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)

    def find_car(self, **search_params):
        """Find a car based on input parameters
        
        Parameters
        ----------
        search_params
            the parameters to search for
        """
        null_keys = [key for key in search_params.keys(
        ) if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys(
        ) if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys(
        ) if key not in null_keys + numeric_keys]

        if len(search_params.keys()) > 0:
            # Building the search query and the parameters
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + \
                [search_params[key]
                    for key in numeric_keys] + [None for key in null_keys]

            # query is the base query
            # where_clause is the join condition
            # additional_where_clause is where all search items will be
            query = f"""select * from {self.table}  """
            where_clause = f""" where 1 """
            additional_where_clause = ("and" if remaining_keys else "") + f" {' and '.join([key + ' like %s ' for key in remaining_keys])} " + \
                ("and" if numeric_keys else "") + f" {' and '.join([key + ' = %s ' for key in numeric_keys])} " + \
                ("and" if null_keys else "") + f" {' and '.join([key + ' is %s ' for key in null_keys])} "
            print(query + where_clause + additional_where_clause)

            records = self.execute_return(
                query + where_clause + additional_where_clause, parameters)
            return self.to_dictionary(records)
        else:
            return self.get_all_car()

    def remove_car(self, car_id):
        """Remove a car based on their id
        
        Parameters
        ----------
        car_id
            id of the car to be deleted
        """
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (car_id,))

    def update_car(self, car_id, **update_values):
        """Update the parameters of a car
        
        Parameters
        ----------
        car_id
            id of the car to be updated
        update_values
            the parameters to be updated and their new values in dict form
        """
        cols_update, new_values = update_values.keys(), update_values.values()

        # Prepare query and params
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        params = list(new_values) + [car_id]
        return self.execute_no_return(query, params)

    def unlock_car(self, car_id):
        return self.update_car(car_id, **{self.BEING_USED: True})

    def lock_car(self, car_id):
        return self.update_car(car_id, **{self.BEING_USED: False})



# Between car and user
class BookingDatabase(AbstractDatabase):
    ID = "ID"
    USER_ID = "UID"
    CAR_ID = "CID"
    BOOKING_DETAIL = "booking_details"
    FROM = "from_time"
    TO = "to_time"
    EVENT_ID_CALENDAR = "id_on_google_calendar"

    property_list = [ID, CAR_ID, USER_ID,
                     BOOKING_DETAIL, FROM, TO, EVENT_ID_CALENDAR]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=BOOKING_TABLE, calendar=None, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password
        self.calendar = calendar

        self.join_property_list = self.property_list + UserDatabase.property_list + CarDatabase.property_list
        self.join_property_list.remove(UserDatabase.ID)
        self.join_property_list.remove(CarDatabase.ID)

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int, {self.USER_ID} int, {self.BOOKING_DETAIL} text, {self.FROM} datetime, {self.TO} datetime, {self.EVENT_ID_CALENDAR} varchar(50), foreign key({self.USER_ID}) references {USER_TABLE}({UserDatabase.ID}) on update cascade on delete set null, foreign key({self.CAR_ID}) references {CAR_TABLE}({CarDatabase.ID}) on update cascade on delete set null )"
        self.execute_no_return(query)

    def add_booking(self, **property_list):
        """Add a new booking schedule
        
        Parameters
        ----------
        property_list
            The properties of the new booking to be added(car id, user id, booking details, start/end time)
        """
        # Check for anyone who rent at the moment first
        query = f"""select * from (select * from {self.table} where {self.CAR_ID} = %s) as b where not (b.{self.FROM} >= %s or b.{self.TO} <= %s)"""
        records = self.execute_return(query, (property_list.get(
            self.CAR_ID), property_list.get(self.TO), property_list.get(self.FROM)))

        # Now check if the car is currently reported
        query_2 = f"""select * from (select * from {ISSUES_TABLE} where {IssuesDatabase.CAR_ID} = %s) as b where b.{IssuesDatabase.FROM} < %s and (b.{IssuesDatabase.TO} <= %s or b.{IssuesDatabase.TO} is null)"""
        records_2 = self.execute_return(query_2, (property_list.get(
            self.CAR_ID), property_list.get(self.TO), property_list.get(self.FROM)))

        print(records)
        print(records_2)

        # If there is no one booking, then add booking
        if len(records) > 0 or len(records_2) > 0:
            raise Exception(
                "This car has been booked or being fixed at this time.")
        else:
            # Add to Google Calendar first
            response = self.calendar.add_event(property_list.get(self.USER_ID), property_list.get(self.CAR_ID), datetime.datetime.strptime(property_list.get(self.FROM), "%Y-%m-%d %H:%M:%S"),
                                               datetime.datetime.strptime(property_list.get(self.TO), "%Y-%m-%d %H:%M:%S"), property_list.get(self.BOOKING_DETAIL), **{"colorId": str(int(property_list.get(self.CAR_ID)) % 11)})
            event_id = response["id"]

            query = f"insert into {self.table} ({', '.join(property_list.keys())}, {self.EVENT_ID_CALENDAR}) values ({', '.join([' %s ' for i in range(len(property_list.values()))])} , %s)"
            self.execute_no_return(query, list(
                property_list.values()) + [event_id])


    def get_all_booking(self):
        """Get all booking info
        """
        records = []
        # This is to find all bookings not null
        query = f"select {', '.join(self.join_property_list)} from {BOOKING_TABLE}, {USER_TABLE}, {CAR_TABLE} " + \
            f" where {BOOKING_TABLE}.{BookingDatabase.USER_ID} = {USER_TABLE}.{UserDatabase.ID} and {BOOKING_TABLE}.{BookingDatabase.CAR_ID} = {CAR_TABLE}.{CarDatabase.ID} "
        records += self.to_dictionary(self.execute_return(query),
                                      self.join_property_list)

        # This query is to find all remaining bookings with UID or CID is null
        query = f"select {', '.join(self.property_list)} from {BOOKING_TABLE} where {self.USER_ID} is %s or {self.CAR_ID} is %s"
        records += self.to_dictionary(self.execute_return(query, (None, None)))

        return records

    def find_booking(self, **search_params):
        """Get a booking based on the search parameters
        
        Parameters
        ----------
        search_params
            the attributes of the booking we are looking for in dict form
        """
        # from-time and end-time are treated separatedly
        from_time, to_time = None, None
        if self.FROM in search_params.keys():
            from_time = search_params.get(self.FROM) if isinstance(search_params.get(
                self.FROM), str) else datetime.datetime.strftime(search_params.get(self.FROM), "%Y-%m-%d %H:%M:%S")
            del search_params[self.FROM]

        if self.TO in search_params.keys():
            to_time = search_params.get(self.TO) if isinstance(search_params.get(
                self.TO), str) else datetime.datetime.strftime(search_params.get(self.TO), "%Y-%m-%d %H:%M:%S")
            del search_params[self.TO]

        # Specify on which keys are null, numeric or the remaining ones
        # Since for each type, they will have different SQL syntaxes
        null_keys = [key for key in search_params.keys() if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys() if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys() if key not in null_keys + numeric_keys]

        # Build the parameter list and the combine query
        if len(search_params.keys()) > 0:
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + \
                [search_params[key]
                    for key in numeric_keys] + [None for key in null_keys]

            # query is the base query
            # where_clause is the join condition
            # additional_where_clause is where all search items will be
            query = f"select {', '.join(self.join_property_list)} from {BOOKING_TABLE}, {USER_TABLE}, {CAR_TABLE} "
            where_clause = f" where {BOOKING_TABLE}.{BookingDatabase.USER_ID} = {USER_TABLE}.{UserDatabase.ID} and {BOOKING_TABLE}.{BookingDatabase.CAR_ID} = {CAR_TABLE}.{CarDatabase.ID} "
            additional_where_clause = ("and" if remaining_keys else "") + f" {' and '.join([key + ' like %s ' for key in remaining_keys])} " + (
                "and" if numeric_keys else "") + f" {' and '.join([key + ' = %s ' for key in numeric_keys])} " + ("and" if null_keys else "") + f" {' and '.join([key + ' is %s ' for key in null_keys])} "
            # print(query)

            if from_time:
                additional_where_clause += f" and {self.TO} > %s "
                parameters += [from_time]
            if to_time:
                additional_where_clause += f" and {self.FROM} < %s "
                parameters += [to_time]
            
            print("Query", query + where_clause + additional_where_clause)
            print("Params: ", parameters)
            records = self.execute_return(query + where_clause + additional_where_clause, parameters)
            return self.to_dictionary(records, self.join_property_list)
        else:
            return self.get_all_booking()

    def cancel_booking(self, booking_id):
        """Cancel the booking made before
        
        Parameters
        ----------
        booking_id
            the id of the booking
        """
        # Get the Calendar ID for booking
        records = self.find_booking(**{self.ID: booking_id})
        if len(records) < 1:
            return
        else:
            event_calendar_id = records[0][self.EVENT_ID_CALENDAR]

            # Cancel on database
            query = f"delete from {self.table} where {self.ID} = %s"
            self.execute_no_return(query, (booking_id,))
            print("Cancel booking ", booking_id)

            # Cancel on Google Calendar
            self.calendar.cancel_event(event_calendar_id)

    def update_booking(self, booking_id, **update_values):
        """Update the information of the booking
        
        Parameters
        ----------
        booking_id
            The id of the booking
        update_values
            The key and value of the booking parameters in dict form
        """
        # Find the value of old record
        records = self.find_booking(**{self.ID: booking_id})

        if len(records) == 0:
            return None
        else:
            event_calendar_id = records[0][self.EVENT_ID_CALENDAR]

            # Check for anyone who rent at updated moment first
            query = f"""select * from (select * from {self.table} where {self.CAR_ID} = %s) as b where not (b.{self.FROM} >= %s or b.{self.TO} <= %s)"""
            records_1 = self.execute_return(query, (records[0].get(
                self.CAR_ID), update_values.get(self.TO), update_values.get(self.FROM)))

            # Now check if the car is currently reported
            query_2 = f"""select * from (select * from {ISSUES_TABLE} where {IssuesDatabase.CAR_ID} = %s) as b where b.{IssuesDatabase.FROM} < %s and (b.{IssuesDatabase.TO} <= %s or b.{IssuesDatabase.TO} is null)"""
            records_2 = self.execute_return(query_2, (records[0].get(
                self.CAR_ID), update_values.get(self.TO), update_values.get(self.FROM)))

            if len(records_1) > 1 or len(records_2) > 0:
                raise Exception(
                    "This car has been booked or being fixed at this time.")
            else:
                # Then update it with new values
                calendar_update_keys = self.property_list[1: -1]
                calendar_update_params = {key: update_values.get(key) if update_values.get(
                    key) else records[0][key] for key in calendar_update_keys}

                self.calendar.update_event(
                    event_calendar_id, **calendar_update_params)

                query = f"update {self.table} set {', '.join([key + ' = %s ' for key in update_values.keys()])} " + \
                    f" where {self.ID} = %s"
                return self.execute_no_return(query, list(update_values.values()) + [booking_id])


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

    def add_employee(self, **property_list):
        """Add an employee
        
        Parameters
        ----------
        property_list
            the property of the employee (id and name)
        """
        query = f"insert into {self.table} ({', '.join(property_list.keys())}) values ({', '.join([' %s ' for i in range(len(property_list.values()))])} )"
        self.execute_no_return(query, list(property_list.values()))

    def get_all(self):
        """Get all employees
        """
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)

    def update_employee(self, employee_id, **update_values):
        """Update the information of the employee
        
        Parameters
        ----------
        employee_id
            The id of the employee
        update_values
            the key and value of the employee parameters in dict form
        """
        cols_update, new_values = update_values.keys(), update_values.values()

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values) + [employee_id]
        return self.execute_no_return(query, params)


class IssuesDatabase(AbstractDatabase):
    CAR_ID = "CID2"
    ID = "Issues_ID"
    ENGINEER_ID = "Engineer_ID"
    FROM = "start_time"
    TO = "end_time"
    STATUS = "completed"
    property_list = [ID, CAR_ID, ENGINEER_ID, FROM, TO, STATUS]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=ISSUES_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password
        self.join_property_list = self.property_list + CarDatabase.property_list

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int, {self.ENGINEER_ID} int, {self.FROM} datetime, {self.TO} datetime, {self.STATUS} bool, foreign key({self.ENGINEER_ID}) references {EMPLOYEE_TABLE}({EmployeesDatabase.ID}) on update cascade on delete set null" + \
            f" , foreign key({self.CAR_ID}) references {CAR_TABLE}({CarDatabase.ID}) on update cascade on delete set null )"
        self.execute_no_return(query)

    def add_issues(self, **property_list):
        """Add an issue
        
        Parameters
        ----------
        property_list
            the properties of the issues, such as Car id, engineer ID, from time, to time
        """
        query = f"insert into {self.table} " + f" ({', '.join(property_list.keys())} , {self.FROM}, {self.STATUS}) values ({', '.join([' %s ' for i in range(len(property_list.values()))])} , now(), %s)"
        self.execute_no_return(query, list(property_list.values()) + [False])


    def complete_issues(self, id):
        """Signifying that the issue is solved
        
        Parameters
        ----------
        id
            the id of the issue
        """
        query = f"update {self.table} set {self.TO} = now(), {self.STATUS} = %s where {self.ID} = %s "
        return self.execute_no_return(query, (True, id))

    def get_all_issues(self):
        """Get all the issues
        """
        records = []
        # Get the normal issues
        query = f"select {', '.join(self.join_property_list)} from {self.table}, {CAR_TABLE} where {self.table}.{self.CAR_ID} = {CAR_TABLE}.{CarDatabase.ID}"
        records += self.to_dictionary(self.execute_return(query),
                                      self.join_property_list)

        # Get the issues with car_id or engineer_id is Null
        query = f"select {', '.join(self.property_list)} from {self.table} where {self.CAR_ID} is %s or {self.ENGINEER_ID} is %s"
        records += self.to_dictionary(self.execute_return(query, (None, None)))

        return records

    def find_issues(self, **search_params):
        """ Get the issues based on the parameters
        
        Parameters
        ----------
        search_params
            the parameters dict to search for
        """
        # from-time and end-time are treated separatedly
        from_time, to_time = None, None
        if self.FROM in search_params.keys():
            from_time = search_params.get(self.FROM) if isinstance(search_params.get(
                self.FROM), str) else datetime.datetime.strftime(search_params.get(self.FROM), "%Y-%m-%d %H:%M:%S")
            del search_params[self.FROM]

        if self.TO in search_params.keys():
            to_time = search_params.get(self.TO) if isinstance(search_params.get(
                self.TO), str) else datetime.datetime.strftime(search_params.get(self.TO), "%Y-%m-%d %H:%M:%S")
            del search_params[self.TO]

        # Specify on which keys are null, numeric or the remaining ones
        # Since for each type, they will have different SQL syntaxes
        null_keys = [key for key in search_params.keys(
        ) if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys(
        ) if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys(
        ) if key not in null_keys + numeric_keys]

        # Now combine everything into 1 SQL command
        if len(search_params.keys()) > 0:
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + \
                [search_params[key]
                    for key in numeric_keys] + [None for key in null_keys]

            # query is the base query
            # where_clause is the join condition
            # additional_where_clause is where all search items will be
            query = f"select {', '.join(self.join_property_list)} from {self.table}, {CAR_TABLE} "
            where_clause = f" where {CAR_TABLE}.{CarDatabase.ID} = {self.table}.{self.CAR_ID} "
            additional_where_clause = (" and " if remaining_keys else "") + f" {' and '.join([key + ' like %s ' for key in remaining_keys])} " + (
                " and " if numeric_keys else "") + f" {' and '.join([key + ' = %s ' for key in numeric_keys])} " + (" and " if null_keys else "") + f" {' and '.join([key + ' is %s ' for key in null_keys])} "

            if from_time:
                additional_where_clause += f" and ({self.TO} > %s or {self.TO} is null)"
                parameters += [from_time]

            if to_time:
                additional_where_clause += f" and {self.FROM} < %s "
                parameters += [to_time]

            records = self.execute_return(
                query + where_clause + additional_where_clause, tuple(parameters))
            # print(records)
            return self.to_dictionary(records, self.join_property_list)
        else:
            return self.get_all_issues()

    def modify_issues(self, id, **update_values):
        """ Changing issue information
        
        Parameters
        ----------
        id
            the id of the issue
        update_values
            the values to be changed
        """
        cols_update, new_values = update_values.keys(), update_values.values()

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values) + [id]
        return self.execute_no_return(query, params)

    def cancel_issues(self, id):
        """ Cancel the issue
        
        Parameters
        ----------
        id
            the id of the issue
        """
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (id, ))


class StatisticsDatabase(AbstractDatabase):
    def __init__(self, host=host, user=user, password=password, schema=schema, drop_existing_table=False):
        self.database = schema
        self.host = host
        self.user = user
        self.password = password

    # For statistic report, monthly revenue for the last 12 months

    def get_monthly_revenue(self):
        """
        Get revenue for each month
        """

        query = f"""SELECT month({BookingDatabase.FROM}) as month_number, 
            sum(round((unix_timestamp({BookingDatabase.TO}) - unix_timestamp({BookingDatabase.FROM})) / (60 * 60)) * {CarDatabase.COST_PER_HOUR}) as monthly_revenue
            FROM {BOOKING_TABLE}, {CAR_TABLE}
            where {BookingDatabase.CAR_ID} = {CarDatabase.ID}
            group by month({BookingDatabase.FROM}) """
        records = self.execute_return(query)
        records = dict(records)

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        records = list(records.items())
        records = [list(item) for item in records]
        records = [[months[item[0] - 1]] +
                   [int(item[1])] + item[2:] for item in records]

        return records

    # Get current reported car in current date
    def get_today_issues(self):
        """
        Get the amount of issues for today
        """

        query = f"""SELECT count(*) 
        FROM (select * from {ISSUES_TABLE} 
        WHERE {IssuesDatabase.FROM} between current_date() and date_add(current_date(), interval 1 day)) as e"""
        records = self.execute_return(query)
        return records

    def get_number_of_new_users(self):
        """Get the number of new users by today"""

        query = f"""SELECT month({UserDatabase.CREATED_DATE}) as month_number, count(*) as new_users 
        FROM {USER_TABLE} 
        group by month({UserDatabase.CREATED_DATE})"""
        records = self.execute_return(query)
        records = dict(records)

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        records = list(records.items())
        records = [list(item) for item in records]
        records = [[months[item[0] - 1]] +[int(item[1])] + item[2:] for item in records]

        return records

    # Number of all car

    def get_number_of_car(self):
        """
        Get the total number of cars in the inventory
        """
        query = f"select count(*) from {CAR_TABLE}"
        records = self.execute_return(query)
        return records

    # Get current booked car in current date

    def get_booked_car(self):
        """
        Get the amount of cars that booked by each month
        """
        query = f"""select COUNT(b.{BookingDatabase.CAR_ID}) from {BOOKING_TABLE} as b 
        WHERE b.{BookingDatabase.FROM} between current_date() and date_add(current_date(), interval 1 day)"""
        # query = f"select DATE_ADD(CURRENT_DATE(), INTERVAL 1 DAY)"
        records = self.execute_return(query)
        return records

    # Get current free car in current date

    def get_free_car(self):
        """ 
        Get the number of free cars (No booking, no issues) by month 
        """
        query = f"""select COUNT(c.{CarDatabase.ID}) from {CAR_TABLE} as c 
        where c.{CarDatabase.ID} not in 
            (select i.{IssuesDatabase.CAR_ID} as ID from {ISSUES_TABLE} as i 
            WHERE {IssuesDatabase.FROM} between current_date() and date_add(current_date(), interval 1 day
            ) 
            union 
            select b.{BookingDatabase.CAR_ID} as ID from {BOOKING_TABLE} as b 
            WHERE {BookingDatabase.FROM} between current_date() and date_add(current_date(), interval 1 day)
            )"""
        records = self.execute_return(query)
        return records


if __name__ == "__main__":
    # Drop schema first
    connector = SQLDatabase.connect(host, user, password)
    cursor = connector.cursor()
    query = f"drop database if exists {schema}"
    cursor.execute(query)
    connector.commit()
    connector.close()

    # # Drop all events
    calendar = GoogleCalendar()
    calendar.cancel_all_events()

    # # # # Define the Database
    login_db = LoginDatabase()
    user_db = UserDatabase()
    car_db = CarDatabase()
    employee_db = EmployeesDatabase()
    booking_db = BookingDatabase(calendar=calendar)
    issues_db = IssuesDatabase()

    # # # # Insert data into tables
    # Login Database
    login_db.add_login("s3694808@rmit.edu.vn", "Rm!th@angeSoftB1og", "user")
    login_db.add_login("s3618748@rmit.edu.vn", "159753", "engineer")
    login_db.add_login("s3694365@rmit.edu.vn", "123456", "manager")
    login_db.add_login("hoangesoftblog@gmail.com", "Rm!t", "admin")
    login_db.add_login("l9933429@rmit.edu.vn", "password", "user")
    login_db.add_login("random_user@yahoo.com.vn", "password", "user")
    login_db.add_login("random_user2@yahoo.com.vn", "password2", "user")

    # User Database
    user_db.add_user(USER_ID=1, name="hoang truong", address="Thu Duc, TP.HCM", phone_number="0973557408")
    user_db.add_user(USER_ID=5, name="hoang (English)", address="Q. Thu Duc, TP. HCM", phone_number="0973557408")
    user_db.add_user(USER_ID=6, name="Random user", address="TP.HCM, VN", phone_number="0913885983")

    # Car Database
    car_db.insert_car(**{car_db.BRAND: "Merc C 300 AMG", car_db.BODY_TYPE: "Sedan", car_db.COLOUR: "Black", car_db.SEATS: "4", car_db.LOCATION: "Dist. 1", car_db.COST_PER_HOUR: "100000", car_db.LAT: 10.778157, car_db.LNG: 106.702830})

    car_db.insert_car(**{car_db.BRAND: "Merc E 200", car_db.BODY_TYPE: "Sedan", car_db.COLOUR: "White", car_db.SEATS: "4", car_db.LOCATION: "Dist. 7", car_db.COST_PER_HOUR: "120000", car_db.LAT: 10.744073, car_db.LNG: 106.701548})

    car_db.insert_car(**{car_db.BRAND: "Merc S 450 L", car_db.BODY_TYPE: "Sedan", car_db.COLOUR: "Grey", car_db.SEATS: "4", car_db.LOCATION: "RMIT", car_db.COST_PER_HOUR: "150000", car_db.LAT: 10.730060, car_db.LNG: 106.692875})

    car_db.insert_car(**{car_db.BRAND: "BMW X4", car_db.BODY_TYPE: "Sedan", car_db.COLOUR: "Red", car_db.SEATS: "5", car_db.LOCATION: "Dist. Binh Thanh", car_db.COST_PER_HOUR: "100000", car_db.LAT: 10.805242, car_db.LNG: 106.716938})

    car_db.insert_car(**{car_db.BRAND: "BMW X7", car_db.BODY_TYPE: "SUV", car_db.COLOUR: "Black", car_db.SEATS: "7", car_db.LOCATION: "Thu Duc", car_db.COST_PER_HOUR: "180000", car_db.LAT: 10.730104, car_db.LNG: 106.691745})
    car_db.insert_car(**{car_db.BRAND: "Audi Q7", car_db.BODY_TYPE: "SUV", car_db.COLOUR: "Yellow", car_db.SEATS: "7", car_db.LOCATION: "Dist. 2", car_db.COST_PER_HOUR: "180000", car_db.LAT: 10.815434, car_db.LNG: 106.730482})


    car_db.insert_car(**{car_db.BRAND: "Merc GLC 300", car_db.BODY_TYPE: "SUV", car_db.COLOUR: "Black", car_db.SEATS: "5", car_db.LOCATION: "Dist. 8", car_db.COST_PER_HOUR: "180000", car_db.LAT: 10.739963, car_db.LNG: 106.657276})

    car_db.insert_car(**{car_db.BRAND: "Honda City", car_db.BODY_TYPE: "Sedan", car_db.COLOUR: "Blue", car_db.SEATS: "4", car_db.LOCATION: "Dist. 8", car_db.COST_PER_HOUR: "100000", car_db.LAT: 10.739963, car_db.LNG: 106.657276})
    car_db.insert_car(**{car_db.BRAND: "Merc GLC 250", car_db.BODY_TYPE: "SUV", car_db.COLOUR: "Red", car_db.SEATS: "5", car_db.LOCATION: "Dist. 8", car_db.COST_PER_HOUR: "180000", car_db.LAT: 10.739963, car_db.LNG: 106.657276})

    car_db.insert_car(**{car_db.BRAND: "Honda Accord", car_db.BODY_TYPE: "Sedan", car_db.COLOUR: "Blue", car_db.SEATS: "4", car_db.LOCATION: "Dist. 8", car_db.COST_PER_HOUR: "150000", car_db.LAT: 10.739963, car_db.LNG: 106.657276})

    # Employees Database
    employee_db.add_employee(
            **{employee_db.ID: 2, employee_db.NAME: "Dang Dinh Khanh"})
    employee_db.add_employee(
        **{employee_db.ID: 3, employee_db.NAME: "Pham Trung Hieu"})
    employee_db.add_employee(
        **{employee_db.ID: 4, employee_db.NAME: "Ho Minh Duc"})

    # Booking Database
    booking_db.add_booking(CID=2, UID=1, booking_details="Hello, it's me!",
                           from_time='2020-09-24 13:10:10', to_time='2020-09-25 14:10:10')
    booking_db.add_booking(CID=1, UID=6, booking_details="I want to borrow it!",
                           from_time='2020-09-24 05:10:10', to_time='2020-09-26 09:10:10')
    booking_db.add_booking(CID=3, UID=1, booking_details="1234",
                           from_time='2020-10-01 10:10:10', to_time='2020-10-02 10:10:10')

    # Issues Database
    issues_db.add_issues(CID2=3, Engineer_ID=2)
    issues_db.add_issues(CID2=1, Engineer_ID=2)

    # # # Other methods
    login_db.change_password(3, "1010101")
    login_db.delete_login(5)
    print("User existed:", login_db.login_existed("hello", "123456"))
    print("All login:", login_db.get_all_login())

    # User Database
    print("User 1 is:", user_db.find_user(**{user_db.ID: 1}))
    print()
    user_db.update_user(6, **{user_db.NAME: "Viet Nam oi"})
    user_db.remove_user(5)

    print("Get all users:", user_db.get_all())
    print()

    # Car database
    print(r"Find car with brand 'Toyota':",
          car_db.find_car(**{car_db.BRAND: "Toyota"}))
    print(car_db.update_car(
        4, **{car_db.BRAND: "Zoros", car_db.BODY_TYPE: "Unicycle"}))
    car_db.remove_car(1)
    car_db.unlock_car(2)

    print("All cars:", car_db.get_all_car())
    print()

    # Employees database
    employee_db.update_employee(4, **{employee_db.NAME: "??????"})
    print("All employees:", employee_db.get_all())
    print()

    # Booking database
    booking_db.update_booking(
        3, from_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    booking_db.cancel_booking(2)
    print("Booking with seats = 4 and location = Thu Duc:",
          booking_db.find_booking(seats=4, address="Thu Duc, TP.HCM"))
    print("All bookings:", booking_db.get_all_booking())
    print()

    # Issues Database
    print("Issues with ID = 1:", issues_db.find_issues(Issues_ID=1))
    issues_db.modify_issues(1, start_time='2020-10-03 10:10:10')
    issues_db.complete_issues(1)
    issues_db.cancel_issues(2)
    print("All issues:", issues_db.get_all_issues())
    print()

    statistics_db = StatisticsDatabase()
    method_list = [print(method + ":", getattr(statistics_db, method)()) for method in dir(statistics_db)
                   if callable(getattr(statistics_db, method)) and method not in dir(AbstractDatabase())]


    # # ###### Test set
    # # # # Test for add same username - table Account
    # # # account_db.add_user("hoangesoftblog", "h@angeSoftB1og", "hoang truong", "Thu Duc, TP.HCM", "0973557408")

    # # # # Test add booking overlap - Table Booking
    # # # booking_db.add_booking(2, 3, "Let's go to Vung Tau!", '2020-08-01 13:00:00', '2020-08-01 14:05:10')
    # # login_db = LoginDatabase()
    # # print(login_db.find_login("hoangafublog@email.com", "112358"))

    # hashed_password = flask_bcrypt.bcrypt.hashpw(password.encode('utf-8'), flask_bcrypt.bcrypt.gensalt()).decode('utf-8')
    # print(len(hashed_password))

    