# """https://code.tutsplus.com/vi/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972"""

import MySQLdb as SQLDatabase
#import sqlite3 as SQLDatabase
import datetime
# from abc import *
from google_calendar import GoogleCalendar

mode = "On"

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
    """An Abstract Database, served as a template for other databases

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
        
        Parameters
        ----------
        query
            The query command to be executed
        data
            The data to put into the query
        connector_setting
            The setting for the connector to initialize
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
        
        Parameters
        ----------
        query
            The query command to be executed
        data
            The data to put into the query
        amount
            Thoose to either fetch one of the query or fetch all of the found query ("many" or "one" string)
        connector_setting
            The setting for the connector to initialize
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
        
        Parameters
        ----------
        data
            The data of attribute
        attribute_list
            The list of attribute that you want to add to the data
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
        """Return values of a column name
        
        Parameters
        ----------
        col_name
            Name of the column whose values will be returned
        """
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
        """ Create the login and register database

        """
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

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.USERNAME} varchar(50) unique, {self.PASSWORD} varchar(50), {self.ROLES} varchar(15) )"
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
        return self.execute_no_return(query=query, data=(username, password, role))

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
        hashed_password = flask_bcrypt.bcrypt.hashpw(password.encode(
            'utf-8'), flask_bcrypt.bcrypt.gensalt()).decode('utf-8')
        query = f"update {self.table} set {self.PASSWORD} = %s where {self.ID} = %s"
        return self.execute_no_return(query, (password, id))

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
        """Get all the users in the database
        
        """
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)


class UserDatabase (AbstractDatabase):
    """The user database contains all the customers information
    """
    ID = "USER_ID"
    NAME = "name"
    ADDRESS = "address"
    PHONE_NUMBER = "phone_number"
    CREATED_DATE = "created_date"
    property_list = [ID, NAME, ADDRESS, PHONE_NUMBER, CREATED_DATE]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=USER_TABLE, drop_existing_table=False):
        """ Create the customer database

        """
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
        query = f"CREATE TABLE IF NOT EXISTS {self.table} " + "(" + table_property + ")"
        self.execute_no_return(query)

    def add_user(self, **property_list):
        """Add a new customer
        
        Parameters
        ----------
        property_list
            the information of the user, should be in the property_list dict
        """
        if not property_list.get(self.CREATED_DATE):
            property_list[self.CREATED_DATE] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

        numeric_keys = [self.ID]

        if len(search_term.keys()) > 0:
            search_value = [("%" + value + "%" if key not in numeric_keys else value)
                            for key, value in search_term.items()]
            print(search_value)
            query = f"""select * from {self.table} where {' and '.join([key + (' like ' if key not in numeric_keys else ' = ') + '%s' for key in search_term.keys()])} """
            print(query)
            records = self.execute_return(query, search_value)
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
        query = f"delete from {self.table} where {self.ID} = %s"
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
    """The database containing all the cars information
    """
    BRAND = "brand"
    MAKE = BRAND
    BODY_TYPE = "body_type"
    COLOUR = "colour"
    SEATS = "seats"
    LOCATION = "location"
    COST_PER_HOUR = "cost_per_hour"
    ID = "CAR_ID"
    property_list = [ID, BRAND, BODY_TYPE,
                     COLOUR, SEATS, LOCATION, COST_PER_HOUR]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=CAR_TABLE, drop_existing_table=False):
        """ Create the car database
        """
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

    def insert_car(self, **property_list):
        """Add the the new car to the database
        
        Parameters
        ----------
        property_list
            the information of the car, should be in the self.property_list array
        """
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

        if len(search_term.keys()) > 0:
            search_value = [("%" + value + "%" if key not in numeric_keys else value)
                            for key, value in search_term.items()]
            print(search_value)
            query = f"""select * from {self.table} where {' and '.join([key + (' like ' if key not in numeric_keys else ' = ') + '%s' for key in search_term.keys()])} """
            print(query)
            records = self.execute_return(query, search_value)
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

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values)
        params.append(car_id)
        return self.execute_no_return(query, params)

    def get_values_of_col(self, col_name):
        """ Return the unique values of column
        
        Parameters
        ----------
        col_name
            the name of the column whose value will be returned
        """
        query = f"select distinct({col_name}) from {self.table}"
        records = self.execute_return(query)
        return [record[0] for record in records]


# Between car and user
class BookingDatabase(AbstractDatabase):
    """The database containing booking information
    """
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
        """Creating the booking database
        """
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password
        self.calendar = calendar

        self.join_property_list = self.property_list + \
            UserDatabase.property_list + CarDatabase.property_list
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

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int, {self.USER_ID} int, {self.BOOKING_DETAIL} text, {self.FROM} datetime, {self.TO} datetime, {self.EVENT_ID_CALENDAR} varchar(50), foreign key({self.USER_ID}) references {USER_TABLE}({UserDatabase.ID}), foreign key({self.CAR_ID}) references {CAR_TABLE}({CarDatabase.ID}) on update cascade on delete set null )"
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
        """Get all booking info

        """
        records = []
        # This is to find all bookings not null
        query = f"select {', '.join(self.join_property_list)} from {BOOKING_TABLE}, {USER_TABLE}, {CAR_TABLE} " + \
            f" where {BOOKING_TABLE}.{BookingDatabase.USER_ID} = {USER_TABLE}.{UserDatabase.ID} and {BOOKING_TABLE}.{BookingDatabase.CAR_ID} = {CAR_TABLE}.{CarDatabase.ID} "
        print(query)

        records = self.execute_return(query)
        # print(records)

        return self.to_dictionary(records, self.join_property_list)

    def find_booking(self, **search_params):
        """Get a booking based on the search parameters
        
        Parameters
        ----------
        search_params
            the attributes of the booking we are looking for in dict form
        """
        #### from-time and end-time are treated separatedly
        from_time, to_time = None, None
        if self.FROM in search_params.keys():
            from_time = search_params.get(self.FROM) if isinstance(search_params.get(self.FROM), str) else datetime.datetime.strftime(search_params.get(self.FROM), "%Y-%m-%d %H:%M:%S")
            del search_params[self.FROM]

        if self.TO in search_params.keys():
            to_time = search_params.get(self.TO) if isinstance(search_params.get(self.TO), str) else datetime.datetime.strftime(search_params.get(self.TO), "%Y-%m-%d %H:%M:%S")
            del search_params[self.TO]

        #### Specify on which keys are null, numeric or the remaining ones
        #### Since for each type, they will have different SQL syntaxes
        null_keys = [key for key in search_params.keys() if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys() if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys() if key not in null_keys + numeric_keys]

        if len(search_params.keys()) > 0:
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + \
                [search_params[key]
                    for key in numeric_keys] + [None for key in null_keys]
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
            
            print("The combine query:", query + where_clause + additional_where_clause)
            print("Params:", parameters)

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
        print("THE RECORDS", records)
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
        records = self.find_booking(**{self.ID: booking_id})
        event_calendar_id = records[0][self.EVENT_ID_CALENDAR]

        calendar_update_keys = self.property_list[1: -1]
        calendar_update_params = {key: update_values.get(key) if update_values.get(
            key) else records[0][key] for key in calendar_update_keys}

        self.calendar.update_event(event_calendar_id, **calendar_update_params)

        query = f"update {self.table} set {', '.join([key + ' = %s ' for key in update_values.keys()])} " + \
            f" where {self.ID} = %s"
        return self.execute_no_return(query, list(update_values.values()) + [booking_id])


class EmployeesDatabase(AbstractDatabase):
    """The database containing employee information
    """
    ID = "ID"
    NAME = "name"
    property_list = [ID, NAME]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=EMPLOYEE_TABLE, drop_existing_table=False):
        """The database containing employee information
        """ 
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
    """The database containing issues of cars and the engineer responsible for it
    """
    CAR_ID = "CID2"
    ID = "Issues_ID"
    ENGINEER_ID = "Engineer_ID"
    FROM = "from_time"
    TO = "end_time"
    property_list = [ID, CAR_ID, ENGINEER_ID, FROM, TO]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=ISSUES_TABLE, drop_existing_table=False):
        """Creating the IssuesDatabase
        """
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password
        self.join_property_list = self.property_list + [CarDatabase.LOCATION]

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(
            self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)

        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int, {self.ENGINEER_ID} int, {self.FROM} datetime, {self.TO} datetime, foreign key({self.ENGINEER_ID}) references {EMPLOYEE_TABLE}({EmployeesDatabase.ID}) " + \
            f" , foreign key({self.CAR_ID}) references {CAR_TABLE}({CarDatabase.ID}) on update cascade on delete set null )"
        self.execute_no_return(query)

    def add_issues(self, **property_list):
        """Add an issue
        
        Parameters
        ----------
        property_list
            the properties of the issues, such as Car id, engineer ID, from time, to time
        """
        query = f"insert into {self.table} " + \
            f" ({', '.join(property_list.keys())} , {self.FROM}, {self.TO}) values ({', '.join([' %s ' for i in range(len(property_list.values()))])} , now(), '9999-12-31 23:59:59')".format(
                *self.property_list[1:-1])
        self.execute_no_return(query, property_list.values())

    def accept_issues(self, id, engineer_id):
        """Allocate the engineer to solve the issue
        
        Parameters
        ----------
        id
            the id of the issue
        engineer_id
            the id of the engineer
        """
        query = f"update {self.table} set {self.ENGINEER_ID} = %s where {self.ID} = %s "
        return self.execute_no_return(query, (engineer_id, id))

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
        #### from-time and end-time are treated separatedly
        from_time, to_time = None, None
        if self.FROM in search_params.keys():
            from_time = search_params.get(self.FROM) if isinstance(search_params.get(self.FROM), str) else datetime.datetime.strftime(search_params.get(self.FROM), "%Y-%m-%d %H:%M:%S")
            del search_params[self.FROM]

        if self.TO in search_params.keys():
            to_time = search_params.get(self.TO) if isinstance(search_params.get(self.TO), str) else datetime.datetime.strftime(search_params.get(self.TO), "%Y-%m-%d %H:%M:%S")
            del search_params[self.TO]

        #### Specify on which keys are null, numeric or the remaining ones
        #### Since for each type, they will have different SQL syntaxes
        null_keys = [key for key in search_params.keys() if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys() if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys() if key not in null_keys + numeric_keys]

        #### Now combine everything into 1 SQL command
        if len(search_params.keys()) > 0:
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + \
                [search_params[key]
                    for key in numeric_keys] + [None for key in null_keys]
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
            
            records = self.execute_return(query + where_clause + additional_where_clause, tuple(parameters))
            print(records)
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


if __name__ == "__main__":
    # Drop schema first
    connector = SQLDatabase.connect(host, user, password)
    cursor = connector.cursor()
    query = f"drop database if exists {schema}"
    cursor.execute(query)
    connector.commit()
    connector.close()

    # Drop all events
    calendar = GoogleCalendar()
    calendar.cancel_all_events()

    # Login Database
    # Role 0 is User
    # Role 1 is Engineer
    # Role 2 is Manager
    # Role 3 is Admin

    login_db = LoginDatabase()
    print(login_db.add_login("hoangafublog@email.com", "112358", "user"))
    print(login_db.add_login("hoang", "159753", "engineer"))
    print(login_db.add_login("hoangesoftblog", "1", "manager"))
    print(login_db.add_login("hello", "123456", "admin"))
    print(login_db.add_login("temp1", "12", "user"))
    print(login_db.add_login("temp", "1", "user"))

    print(login_db.change_password(3, "1010101"))
    print(login_db.delete_login(5))
    print(login_db.get_all_login())
    print(login_db.find_login("hello", "123456"))

    # User Database

    user_db = UserDatabase()
    user_db.add_user(1, "hoang truong", "Thu Duc, TP.HCM", "0973557408")
    user_db.add_user(6, "rand", "rand", "0973557408")

    print(user_db.find_user(**{user_db.ID: 1}))
    user_db.update_user(6, **{user_db.NAME: "Viet Nam oi"})
    user_db.remove_user(6)
    user_db.add_user(6, "mahadoyugi", "VN", "0123456789")
    print(user_db.get_all())

    # Car database

    car_db = CarDatabase()
    car_db.insert_car("Honda Civic", "Sedan", "Black",
                      "4", "Thu Duc", "1000000")
    car_db.insert_car("Toyota Camry", "Sedan", "Brown", "5", "Q1", "1500000")
    car_db.insert_car("Fortuner", "Something", "Green", "7", "Q1", "2000000")
    car_db.insert_car("Random", "Random", "Random", "10", "Vietnam", "500000")

    print(car_db.find_car(**{car_db.BRAND: "Toyota"}))
    print(car_db.update_car(
        4, **{car_db.BRAND: "Zoros", car_db.BODY_TYPE: "Unicycle"}))
    car_db.remove_car(4)
    print(car_db.get_all_car())

    # #### Employees database

    employee_db = EmployeesDatabase()
    employee_db.add_employee(2, "Dang Dinh Khanh")
    employee_db.add_employee(3, "Tui la tui chu la ai")
    employee_db.add_employee(4, "Duc la tui")

    # employee_db.update_employee(4, **{employee_db.NAME: "??????"})
    # print(employee_db.get_all())

    # # #### Booking database
    # booking_db = BookingDatabase(calendar)
    # # booking_db.add_booking(2, 1, "Hello, it's me!", '2020-08-24 13:10:10', '2020-08-25 14:10:10')
    # # booking_db.add_booking(1, 1, "I want to borrow it!", '2020-08-24 05:10:10', '2020-08-26 09:10:10')
    # # booking_db.add_booking(3, 1, "1234", '2020-06-01 10:10:10', '2020-06-30 10:10:10')
    # # print(booking_db.get_all_booking())
    # # booking_db.cancel_booking(3)
    # # print(len(booking_db.find_booking(seats=4, address="Thu Duc, TP.HCM")))

    # # #### Issues Database
    # issues_db = IssuesDatabase()
    # # issues_db.add_issues(2, 2, "Nha phan phoi duy long", "Please fix it soon")

    # # ###### Test set
    # # # # Test for add same username - table Account
    # # # account_db.add_user("hoangesoftblog", "h@angeSoftB1og", "hoang truong", "Thu Duc, TP.HCM", "0973557408")

    # # # # Test add booking overlap - Table Booking
    # # # booking_db.add_booking(2, 3, "Let's go to Vung Tau!", '2020-08-01 13:00:00', '2020-08-01 14:05:10')
    # # login_db = LoginDatabase()
    # # print(login_db.find_login("hoangafublog@email.com", "112358"))

    pass
