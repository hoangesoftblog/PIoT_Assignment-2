#"""https://code.tutsplus.com/vi/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972"""

import MySQLdb as SQLDatabase
#import sqlite3 as SQLDatabase
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
    ### Abstract Class Implementation
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
        self.database = self.host = self.user = self.password = self.property_list = self.table = None


    def execute_no_return(self, query, data=None, connector_setting: tuple=None):
        ### Prepare config settings to perform SQL
        ### As some special operations required to have special configs        
        if connector_setting is None:
            self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        else:
            self.connector = SQLDatabase.connect(*connector_setting)
        
        self.cursor = self.connector.cursor()

        ### Get the correct operation for writing SQL
        if data is not None:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

        ### Finish the operation and close
        self.connector.commit()
        self.connector.close()
        # This will return the ID for some operation
        return self.cursor.lastrowid


    def execute_return(self, query, data=None, amount="many", connector_setting=None):
        ### Prepare config settings to perform SQL
        ### As some special operations required to have special configs
        if connector_setting is None:
            self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        else:
            self.connector = SQLDatabase.connect(*connector_setting)

        self.cursor = self.connector.cursor()

        ### Get the correct operation for writing SQL
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

        ### Finish operation
        self.connector.close()
        return records


    def to_dictionary(self, data, attribute_list=None):
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
    USERNAME = "email"
    EMAIL = USERNAME
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
        self.execute_no_return(query, connector_setting=(self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute_no_return(query)
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.USERNAME} varchar(100) unique, {self.PASSWORD} varchar(100), {self.ROLES} varchar(15) )"
        self.execute_no_return(query)


    def add_login(self, email, password, role="user"):
        # The password needed to be hashed first before being put into the DB
        hashed_password = flask_bcrypt.bcrypt.hashpw(password.encode('utf-8'), flask_bcrypt.bcrypt.gensalt()).decode('utf-8')
        query = f"insert into {self.table} " + " ({}, {}, {}) values (%s, %s, %s)".format(*self.property_list[1:])
        return self.execute_no_return(query=query, data=(email, hashed_password, role))


    def delete_login(self, id):
        """Delete statement will return 0. So no return instead"""
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query=query, data=(id,))


    def change_password(self, id, password):
        hashed_password = flask_bcrypt.bcrypt.hashpw(password.encode('utf-8'), flask_bcrypt.bcrypt.gensalt()).decode('utf-8')
        query = f"update {self.table} set {self.PASSWORD} = %s where {self.ID} = %s"
        return self.execute_no_return(query, (hashed_password, id))


    def login_existed(self, email, password):
        query = f"select * from {self.table} where {self.USERNAME} = %s"
        print(query)
        record = self.to_dictionary(self.execute_return(query, (email, ), amount="one"))
        if record is None:
            return []
        else:
            stored_password = record.get(self.PASSWORD).encode('utf-8')
            if flask_bcrypt.bcrypt.checkpw(password.encode('utf-8'), stored_password):
                return [record]
            else:
                return []


    def get_all_login(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)

 

class UserDatabase (AbstractDatabase):
    ID = "USER_ID"
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
        self.execute_no_return(query, connector_setting=(self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute_no_return(query)
        
        table_property = f"{self.ID} INTEGER primary key, {self.NAME} varchar(100), {self.ADDRESS} varchar(200), {self.PHONE_NUMBER} varchar(20), foreign key ({self.ID}) references {LOGIN_TABLE} ({LoginDatabase.ID}) on update cascade on delete cascade"
        query = f"CREATE TABLE IF NOT EXISTS {self.table} " + "(" + table_property + ")"
        self.execute_no_return(query)


    def add_user(self, **info):
        query = f"insert into {self.table} ({', '.join(info.keys())}) values ({', '.join([' %s ' for i in range(len(info.keys()))])})".format(*self.property_list)
        return self.execute_no_return(query=query, data=info.values())


    def get_all(self):
        query = "select * from " + self.table
        records = self.execute_return(query)
        return self.to_dictionary(records)


    def find_user(self, **search_params):
        null_keys = [key for key in search_params.keys() if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys() if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys() if key not in null_keys + numeric_keys]

        if len(search_params.keys()) > 0:
            # Building the search query and the parameters
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + [search_params[key] for key in numeric_keys] + [None for key in null_keys]
            additional_where_clause =  f" where {' and '.join([key + ' like %s ' for key in remaining_keys])} " + ("and" if numeric_keys else "") + f" {' and '.join([key + ' = %s ' for key in numeric_keys])} " + ("and" if null_keys else "") + f" {' and '.join([key + ' is %s ' for key in null_keys])} "
            query = f"""select * from {self.table}  """
            print(query + additional_where_clause)
            records = self.execute_return(query + additional_where_clause, parameters)
            return self.to_dictionary(records)
        else:
            return self.get_all()

        
    def remove_user(self, user_id):
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (user_id,))

    
    def update_user(self, user_id, **update_values):
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
    property_list = [ID, BRAND, BODY_TYPE, COLOUR, SEATS, LOCATION, COST_PER_HOUR, LAT, LNG]


    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=CAR_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password

        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.BRAND} varchar(20), {self.BODY_TYPE} varchar(30), {self.COLOUR} varchar(40), {self.SEATS} numeric, {self.LOCATION} varchar(100), {self.COST_PER_HOUR} numeric, {self.LAT} float, {self.LNG} float)"
        self.execute_no_return(query)


    def insert_car(self, brand, body, color, seats, location, cost, lat=None, lng=None):
        query = f"""insert into {self.table} ({self.BRAND}, {self.BODY_TYPE}, {self.COLOUR}, {self.SEATS}, {self.LOCATION}, {self.COST_PER_HOUR}, {self.LAT}, {self.LNG}) 
        values({', '.join([' %s ' for i in range(len(self.property_list[1:]))])})"""

        return self.execute_no_return(query, (brand, body, color, seats, location, cost, lat, lng))

    def get_all_car(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)


    def find_car(self, **search_params):
        null_keys = [key for key in search_params.keys() if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys() if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys() if key not in null_keys + numeric_keys]

        if len(search_params.keys()) > 0:
            # Building the search query and the parameters
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + [search_params[key] for key in numeric_keys] + [None for key in null_keys]
            additional_where_clause =  f" where {' and '.join([key + ' like %s ' for key in remaining_keys])} " + ("and" if numeric_keys else "") + f" {' and '.join([key + ' = %s ' for key in numeric_keys])} " + ("and" if null_keys else "") + f" {' and '.join([key + ' is %s ' for key in null_keys])} "
            query = f"""select * from {self.table}  """
            print(query + additional_where_clause)
            records = self.execute_return(query + additional_where_clause, parameters)
            return self.to_dictionary(records)
        else:
            return self.get_all_car()


    def remove_car(self, car_id):
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (car_id,))

    
    def update_car(self, car_id, **update_values):
        cols_update, new_values = update_values.keys(), update_values.values()

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values)
        params.append(car_id)    
        return self.execute_no_return(query, params)


    def get_values_of_col(self, col_name):
        query = f"select distinct({col_name}) from {self.table}"
        records = self.execute_return(query)
        return [record[0] for record in records]


# Between car and user
class BookingDatabase(AbstractDatabase):
    ID = "ID"
    USER_ID = "UID"
    CAR_ID = "CID"
    BOOKING_DETAIL = "booking_details"
    FROM = "from_time"
    TO = "to_time"
    EVENT_ID_CALENDAR = "id_on_google_calendar"

    property_list = [ID, CAR_ID, USER_ID, BOOKING_DETAIL, FROM, TO, EVENT_ID_CALENDAR]
    
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
        self.execute_no_return(query, connector_setting=(self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int, {self.USER_ID} int, {self.BOOKING_DETAIL} text, {self.FROM} datetime, {self.TO} datetime, {self.EVENT_ID_CALENDAR} varchar(50), foreign key({self.USER_ID}) references {USER_TABLE}({UserDatabase.ID}) on update cascade on delete set null, foreign key({self.CAR_ID}) references {CAR_TABLE}({CarDatabase.ID}) on update cascade on delete set null )"
        self.execute_no_return(query)


    def add_booking(self, car_id, user_id, booking_detail, from_time: str, to_time: str):
        # Check for anyone who rent at the moment first
        query = f"""select * from (select * from {self.table} where {self.CAR_ID} = %s) as b where not (b.{self.FROM} >= %s or b.{self.TO} <= %s)"""
        records = self.execute_return(query, (car_id, to_time, from_time))

        # If there is no one booking, then add booking
        if len(records) > 0:
            raise Exception("This car has been booked at this time.")
        else:
            # Add to Google Calendar first
            response = self.calendar.add_event(user_id, car_id, datetime.datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S"), datetime.datetime.strptime(to_time, "%Y-%m-%d %H:%M:%S"), booking_detail, **{"colorId": str(int(car_id) % 11)})
            event_id = response["id"]

            query = f"insert into {self.table} " + " ({}, {}, {}, {}, {}, {}) values(%s, %s, %s, %s, %s, %s)".format(*self.property_list[1:])
            return self.execute_no_return(query, (car_id, user_id, booking_detail, from_time, to_time, event_id))


    def get_all_booking(self):
        records = []
        # This is to find all bookings not null
        query = f"select {', '.join(self.join_property_list)} from {BOOKING_TABLE}, {USER_TABLE}, {CAR_TABLE} " + f" where {BOOKING_TABLE}.{BookingDatabase.USER_ID} = {USER_TABLE}.{UserDatabase.ID} and {BOOKING_TABLE}.{BookingDatabase.CAR_ID} = {CAR_TABLE}.{CarDatabase.ID} "
        records += self.to_dictionary(self.execute_return(query), self.join_property_list)

        # This query is to find all remaining bookings with UID or CID is null
        query = f"select {', '.join(self.property_list)} from {BOOKING_TABLE} where {self.USER_ID} is %s or {self.CAR_ID} is %s"
        records += self.to_dictionary(self.execute_return(query, (None, None)))

        return records


    def find_booking(self, **search_params):
        #### Specify on which keys are null, numeric or the remaining ones
        #### Since for each type, they will have different SQL syntaxes
        null_keys = [key for key in search_params.keys() if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys() if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys() if key not in null_keys + numeric_keys]

        if len(search_params.keys()) > 0:
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + [search_params[key] for key in numeric_keys] + [None for key in null_keys]
            query = f"select {', '.join(self.join_property_list)} from {BOOKING_TABLE}, {USER_TABLE}, {CAR_TABLE} "
            where_clause = f" where {BOOKING_TABLE}.{BookingDatabase.USER_ID} = {USER_TABLE}.{UserDatabase.ID} and {BOOKING_TABLE}.{BookingDatabase.CAR_ID} = {CAR_TABLE}.{CarDatabase.ID} " 
            additional_where_clause = ("and" if remaining_keys else "") +  f" {' and '.join([key + ' like %s ' for key in remaining_keys])} " + ("and" if numeric_keys else "") + f" {' and '.join([key + ' = %s ' for key in numeric_keys])} " + ("and" if null_keys else "") + f" {' and '.join([key + ' is %s ' for key in null_keys])} "
            # print(query)

            records = self.execute_return(query + where_clause + additional_where_clause, parameters)
            return self.to_dictionary(records, self.join_property_list)
        else:
            return self.get_all_booking()


    def cancel_booking(self, booking_id):
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
        records = self.find_booking(**{self.ID: booking_id})
        event_calendar_id = records[0][self.EVENT_ID_CALENDAR]

        calendar_update_keys = self.property_list[1: -1]
        calendar_update_params = {key: update_values.get(key) if update_values.get(key) else records[0][key] for key in calendar_update_keys}

        self.calendar.update_event(event_calendar_id, **calendar_update_params)

        query = f"update {self.table} set {', '.join([key + ' = %s ' for key in update_values.keys()])} " + f" where {self.ID} = %s" 
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
        self.execute_no_return(query, connector_setting=(self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key references {LOGIN_TABLE}({LoginDatabase.ID}), {self.NAME} varchar(100))"
        self.execute_no_return(query)


    def add_employee(self, id, name):
        query = f"insert into {self.table} " + " ({}, {}) values (%s, %s)".format(*self.property_list)
        return self.execute_no_return(query, (id, name))


    def get_all(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.to_dictionary(records)


    def update_employee(self, employee_id, **update_values):
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
    FROM = "from_time"
    TO = "end_time"
    STATUS = "completed"
    property_list = [ID, CAR_ID, ENGINEER_ID, FROM, TO, STATUS]

    def __init__(self, host=host, user=user, password=password, schema=schema, tb_name=ISSUES_TABLE, drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password
        self.join_property_list = self.property_list + [CarDatabase.LOCATION]
        
        # Check for existing schema
        query = f"create database if not exists {self.database}"
        self.execute_no_return(query, connector_setting=(self.host, self.user, self.password))

        # Create table if not exists
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int, {self.ENGINEER_ID} int, {self.FROM} datetime, {self.TO} datetime, {self.STATUS} bool, foreign key({self.ENGINEER_ID}) references {EMPLOYEE_TABLE}({EmployeesDatabase.ID}) on update cascade on delete set null" + f" , foreign key({self.CAR_ID}) references {CAR_TABLE}({CarDatabase.ID}) on update cascade on delete set null )"
        self.execute_no_return(query)


    def add_issues(self, **property_list):
        query = f"insert into {self.table} " + f" ({', '.join(property_list.keys())} , {self.FROM}, {self.STATUS}) values ({', '.join([' %s ' for i in range(len(property_list.values()))])} , now(), %s)".format(*self.property_list[1:-1])
        self.execute_no_return(query, list(property_list.values()) + [False])


    def accept_issues(self, id, engineer_id):
        query = f"update {self.table} set {self.ENGINEER_ID} = %s where {self.ID} = %s "
        return self.execute_no_return(query, (engineer_id, id))


    def complete_issues(self, id):
        query = f"update {self.table} set {self.TO} = now(), {self.STATUS} = %s where {self.ID} = %s "
        return self.execute_no_return(query, (True, id))

    
    def get_all_issues(self):
        records = []
        # Get the normal issues
        query = f"select {', '.join(self.join_property_list)} from {self.table}, {CAR_TABLE} where {self.table}.{self.CAR_ID} = {CAR_TABLE}.{CarDatabase.ID}"
        records += self.to_dictionary(self.execute_return(query), self.join_property_list)

        # Get the issues with car_id or engineer_id is Null
        query = f"select {', '.join(self.property_list)} from {self.table} where {self.CAR_ID} is %s or {self.ENGINEER_ID} is %s"
        records += self.to_dictionary(self.execute_return(query, (None, None)))
        
        return records


    def find_issues(self, **search_params):
        #### Specify on which keys are null, numeric or the remaining ones
        #### Since for each type, they will have different SQL syntaxes
        null_keys = [key for key in search_params.keys() if search_params.get(key) is None]
        numeric_keys = [key for key in search_params.keys() if key not in null_keys and str(search_params.get(key)).isnumeric()]
        remaining_keys = [key for key in search_params.keys() if key not in null_keys + numeric_keys]
        
        #### from-time and end-time are treated separatedly
        from_time, to_time = None, None
        if self.FROM in search_params.keys():
            from_time = search_params.get(self.FROM) if search_params.get(self.FROM) is str else datetime.datetime.strftime(search_params.get(self.FROM), "%Y-%m-%d %H:%M:%S")
            del search_params[self.FROM]

        if self.TO in search_params.keys():
            to_time = search_params.get(self.TO) if search_params.get(self.TO) is str else datetime.datetime.strftime(search_params.get(self.TO), "%Y-%m-%d %H:%M:%S")
            del search_params[self.TO]

        #### Now combine everything into 1 SQL command
        if len(search_params.keys()) > 0:
            parameters = ["%" + search_params[key] + "%" for key in remaining_keys] + [search_params[key] for key in numeric_keys] + [None for key in null_keys]
            query = f"select {', '.join(self.join_property_list)} from {self.table}, {CAR_TABLE} " 
            where_clause = f" where {CAR_TABLE}.{CarDatabase.ID} = {self.table}.{self.CAR_ID} "
            additional_where_clause = (" and " if remaining_keys else "") + f" {' and '.join([key + ' like %s ' for key in remaining_keys])} " + (" and " if numeric_keys else "") + f" {' and '.join([key + ' = %s ' for key in numeric_keys])} "  + (" and " if null_keys else "") + f" {' and '.join([key + ' is %s ' for key in null_keys])} "
            
            if from_time:
                query += f" and {self.TO} > {from_time} "
            
            if to_time:
                query += f" and {self.FROM} < {to_time} "
            
            records = self.execute_return(query + where_clause + additional_where_clause, tuple(parameters))
            print(records)
            return self.to_dictionary(records, self.join_property_list)
        else:
            return self.get_all_issues()


    def modify_issues(self, id, **update_values):
        cols_update, new_values = update_values.keys(), update_values.values()

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values) + [id]
        return self.execute_no_return(query, params) 


    def cancel_issues(self, id):
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
    calendar=GoogleCalendar()
    calendar.cancel_all_events()

    #### Login Database
    # Role 0 is User
    # Role 1 is Engineer
    # Role 2 is Manager
    # Role 3 is Admin

    login_db = LoginDatabase()
    print(login_db.add_login("hoangafublog@email.com", "112358", "user"))
    print(login_db.add_login("hoangviethoa123@yahoo.com.vn", "159753", "engineer"))
    print(login_db.add_login("hoangesoftblog", "1", "manager"))
    print(login_db.add_login("hoangesoftblog@gmail.com", "123456", "admin"))
    print(login_db.add_login("temp1", "12", "user"))
    print(login_db.add_login("temp", "1", "user"))

    print(login_db.change_password(3, "1010101"))
    print(login_db.delete_login(5))
    print(login_db.get_all_login())
    print(login_db.login_existed("hello", "123456"))


    #### User Database

    user_db = UserDatabase()   
    user_db.add_user(USER_ID=1, name="hoang truong", address="Thu Duc, TP.HCM", phone_number="0973557408")  
    user_db.add_user(USER_ID=6, name="rand", address="rand", phone_number="0973557408")  

    # print(user_db.find_user(**{user_db.ID: 1}))
    # user_db.update_user(6, **{user_db.NAME: "Viet Nam oi"})
    # user_db.remove_user(6)
    # user_db.add_user(USER_ID=6, name="rand", address="rand", phone_number="0973557408")  
    # print(user_db.get_all())


    # #### Car database

    car_db = CarDatabase()
    car_db.insert_car("Honda Civic", "Sedan", "Black", "4", "Thu Duc", "1000000", 10.730104, 106.691745)
    car_db.insert_car("Toyota Camry", "Sedan", "Brown", "5", "Q1", "1500000", 10.857306, 106.769463)
    car_db.insert_car("Fortuner", "Something", "Green", "7", "Q1", "2000000", 10.856727, 106.766620)
    car_db.insert_car("Random", "Random", "Random", "10", "Vietnam", "500000", 10.801016, 106.669408)
    
    # print(car_db.find_car(**{car_db.BRAND: "Toyota"}))
    # print(car_db.update_car(4, **{car_db.BRAND: "Zoros", car_db.BODY_TYPE: "Unicycle"}))
    # car_db.remove_car(4)
    # print(car_db.get_all_car())


    # # #### Employees database
    
    employee_db = EmployeesDatabase()
    employee_db.add_employee(2, "Dang Dinh Khanh")
    employee_db.add_employee(3, "Tui la tui chu la ai")
    employee_db.add_employee(4, "Duc la tui")
    
    # employee_db.update_employee(4, **{employee_db.NAME: "??????"})
    # print(employee_db.get_all())


    # # #### Booking database
    booking_db = BookingDatabase(calendar = calendar)
    # # booking_db.add_booking(2, 1, "Hello, it's me!", '2020-08-24 13:10:10', '2020-08-25 14:10:10')
    # # booking_db.add_booking(1, 1, "I want to borrow it!", '2020-08-24 05:10:10', '2020-08-26 09:10:10')
    # # booking_db.add_booking(3, 1, "1234", '2020-06-01 10:10:10', '2020-06-30 10:10:10')
    # # print(booking_db.get_all_booking())
    # # booking_db.cancel_booking(3)
    # # print(len(booking_db.find_booking(seats=4, address="Thu Duc, TP.HCM")))
    

    # # #### Issues Database
    issues_db = IssuesDatabase()
    # query = f"select {issues_db.ENGINEER_ID}, count({issues_db.ENGINEER_ID}) from {issues_db.table} group by {issues_db.ENGINEER_ID}"
    # result = dict(issues_db.execute_return(query))
    # print(result)
    # # issues_db.add_issues(2, 2, "Nha phan phoi duy long", "Please fix it soon")

    # # ###### Test set
    # # # # Test for add same username - table Account
    # # # account_db.add_user("hoangesoftblog", "h@angeSoftB1og", "hoang truong", "Thu Duc, TP.HCM", "0973557408")  

    # # # # Test add booking overlap - Table Booking
    # # # booking_db.add_booking(2, 3, "Let's go to Vung Tau!", '2020-08-01 13:00:00', '2020-08-01 14:05:10')
    # # login_db = LoginDatabase()
    # # print(login_db.find_login("hoangafublog@email.com", "112358"))

    # hashed_password = flask_bcrypt.bcrypt.hashpw(password.encode('utf-8'), flask_bcrypt.bcrypt.gensalt()).decode('utf-8')
    # print(len(hashed_password))
