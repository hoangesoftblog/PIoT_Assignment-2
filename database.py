"""
                                BIG BIG NOTE: 
                    This code is only applied for SQLite only.
                        Needs to change into MySQL
"""
"https://code.tutsplus.com/vi/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972"


import MySQLdb as SQLDatabase
#import sqlite3 as SQLDatabase
import datetime
import flask
from abc import *

host = "localhost"
user = "root"
password = "h@angeSoftB1og"
schema = "temps"

TEMPORARY_DATABASE = "database.db"
applying_database = schema

ACCOUNT_TABLE = "Account"
CAR_TABLE = "Car"
BOOKING_TABLE = "Booking"
EMPLOYEE_TABLE = "Employee"


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
        self.database = self.host = self.user = self.password = self.property_list = None

    def execute_no_return(self, query, data=None, connector_setting: tuple=None):
        # Some special operations required to connect to different areas
        if connector_setting is None:
            self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        else:
            self.connector = SQLDatabase.connect(*connector_setting)
        
        self.cursor = self.connector.cursor()

        ### 
        if data is not None:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

        self.connector.commit()
        self.connector.close()


    def execute_return(self, query, data=None, amount="many", connector_setting=None):
        if connector_setting is None:
            self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        else:
            self.connector = SQLDatabase.connect(*connector_setting)

        self.cursor = self.connector.cursor()

        # Get the correct operation for database
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

        self.connector.close()
        
        return records
    

class UserDatabase (AbstractDatabase):
    USERNAME = "username"
    PASSWORD = "password"
    ID = "ID"
    NAME = "name"
    ADDRESS = "address"
    PHONE_NUMBER = "phone_number"
    property_list = [ID, USERNAME, PASSWORD, NAME, ADDRESS, PHONE_NUMBER]

    def __init__(self, host=host, user=user, password=password, schema=applying_database, tb_name=ACCOUNT_TABLE, drop_existing_table=False):
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
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.USERNAME} varchar(50) unique, {self.PASSWORD} varchar(50), {self.NAME} varchar(100), {self.ADDRESS} varchar(200), {self.PHONE_NUMBER} varchar(20))"
        self.execute_no_return(query)

    def __to_dictionary(self, data):
        if not data:
            return data
        elif isinstance(data[0], tuple):
            return [self.__to_dictionary(child_data) for child_data in data]
        else:
            return dict(zip(self.property_list, data))


    def add_user(self, username, password, name, address, phone_number):
        query = f"insert into {self.table} " + " ({}, {}, {}, {}, {}) values (%s, %s, %s, %s, %s)".format(*self.property_list[1:])
        self.execute_no_return(query=query, data=(username, password, name, address, phone_number))


    def get_all(self):
        query = "select * from " + self.table
        records = self.execute_return(query)
        return self.__to_dictionary(records)


    def get_latest(self):
        query = f"select * from {self.table} where {self.ID} = (select max({self.ID}) from {self.table})"
        record = self.execute_return(query)
        return self.__to_dictionary(record)


    def find_user(self, username, password):
        query = f"select * from {self.table} where {self.USERNAME} = %s and {self.PASSWORD} = %s"
        records = self.execute_return(query, (username, password))
        return self.__to_dictionary(records)

        
    def remove_user(self, user_id):
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (user_id,))

    
    def update_user(self, user_id, cols_update: tuple, new_values: tuple):
        if len(cols_update) != len(new_values):
            raise Exception("Number of rows and numbers of new values are not equal.")
        else:
            pass

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values)
        params.append(str(user_id))     
        self.execute_no_return(query, params)


class CarDatabase (AbstractDatabase):
    BRAND = "brand"
    MAKE = BRAND
    BODY_TYPE = "body_type"
    COLOUR = "colour"
    SEATS = "seats"
    LOCATION = "location"
    COST_PER_HOUR = "cost_per_hour"
    ID = "ID"
    property_list = [ID, BRAND, BODY_TYPE, COLOUR, SEATS, LOCATION, COST_PER_HOUR]


    def __init__(self, host=host, user=user, password=password, schema=applying_database, tb_name=CAR_TABLE, drop_existing_table=False):
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
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.BRAND} varchar(20), {self.BODY_TYPE} varchar(30), {self.COLOUR} varchar(40), {self.SEATS} numeric, {self.LOCATION} varchar(100), {self.COST_PER_HOUR} numeric)"
        self.execute_no_return(query)


    def __to_dictionary(self, data):
        if not data:
            return data
        elif isinstance(data[0], tuple):
            return [self.__to_dictionary(child_data) for child_data in data]
        else:
            return dict(zip(self.property_list, data))


    def insert_car(self, brand, body, color, seats, location, cost):
        query = f"""insert into {self.table} ({self.BRAND}, {self.BODY_TYPE}, {self.COLOUR}, {self.SEATS}, {self.LOCATION}, {self.COST_PER_HOUR}) 
        values(%s, %s, %s, %s, %s, %s)"""

        self.execute_no_return(query, (brand, body, color, seats, location, cost))

    def get_all_car(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.__to_dictionary(records)

    def find_car(self, search_term: str):
        query = f"""select * from {self.table} 
        where {self.BRAND} LIKE %s OR {self.BODY_TYPE} LIKE %s OR {self.COLOUR} LIKE %s OR {self.LOCATION} LIKE %s"""

        records = self.execute_return(query, tuple([("%" + search_term + "%") for i in range(4)]))

        if search_term.isnumeric():
            query = f"""select * from {self.table} 
            where {self.SEATS} = %s OR {self.COST_PER_HOUR} = %s"""
            records_2 = self.execute_return(query, tuple([search_term for i in range(2)]))
            records.extend(records_2)

        return self.__to_dictionary(records)


    def remove_car(self, car_id):
        query = f"delete from {self.table} where {self.ID} = %s"
        self.execute_no_return(query, (car_id,))

    
    def update_car(self, user_id, cols_update: tuple, new_values: tuple):
        if len(cols_update) != len(new_values):
            raise Exception("Number of rows and numbers of new values are not equal.")
        else:
            pass

        # Prepare query
        query = f"update {self.table} set {', '.join([str(col) + ' = %s' for col in cols_update])} where {self.ID} = %s;"
        # Prepare params
        params = list(new_values)
        params.append(str(user_id))     
        self.execute_no_return(query, params)


# Between car and user
class BookingDatabase(AbstractDatabase):
    ID = "ID"
    USER_ID = "UID"
    CAR_ID = "Car_ID"
    BOOKING_DETAIL = "booking_details"
    FROM = "from_time"
    TO = "to_time"
    property_list = [ID, CAR_ID, USER_ID, BOOKING_DETAIL, FROM, TO]

    def __init__(self, host=host, user=user, password=password, schema=applying_database, tb_name=BOOKING_TABLE, drop_existing_table=False):
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
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.CAR_ID} int not null, {self.USER_ID} int not null, {self.BOOKING_DETAIL} text, {self.FROM} datetime, {self.TO} datetime, foreign key({self.USER_ID}) references {ACCOUNT_TABLE}(ID), foreign key({self.CAR_ID}) references {CAR_TABLE}(ID))"
        self.execute_no_return(query)


    def add_booking(self, car_id, user_id, booking_detail, from_time, to_time):
        # Check for anyone who rent at the moment first
        query = f"""select * from (select * from {self.table} where {self.CAR_ID} = %s) as b where not (b.{self.FROM} >= %s or b.{self.TO} <= %s)"""
        print(query)
        records = self.execute_return(query, (car_id, to_time, from_time))
        print(records)

        # If there is no one booking, then add booking
        if len(records) > 0:
            raise Exception("This car has been booked at this time.")
        else:
            query = f"insert into {self.table} " + " ({}, {}, {}, {}, {}) values(%s, %s, %s, %s, %s)".format(*self.property_list[1:])
            self.execute_no_return(query, (car_id, user_id, booking_detail, from_time, to_time))


    def get_all_booking(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.__to_dictionary(records)


    def __to_dictionary(self, data):
        if not data:
            return data
        elif isinstance(data[0], tuple):
            return [self.__to_dictionary(child_data) for child_data in data]
        else:
            return dict(zip(self.property_list, data))


class EmployeesDatabase(AbstractDatabase):
    ID = "ID"
    NAME = "name"
    USERNAME = "username"
    PASSWORD = "password"
    ROLES = "roles"
    property_list = [ID, USERNAME, PASSWORD, NAME, ROLES]


    def __init__(self, host=host, user=user, password=password, schema=applying_database, tb_name=EMPLOYEE_TABLE, drop_existing_table=False):
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
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.ID} INTEGER primary key auto_increment, {self.USERNAME} varchar(50) unique, {self.PASSWORD} varchar(50), {self.NAME} varchar(100), {self.ROLES} integer )"
        self.execute_no_return(query)


    def __to_dictionary(self, data):
        if not data:
            return data
        elif isinstance(data[0], tuple):
            return [self.__to_dictionary(child_data) for child_data in data]
        else:
            return dict(zip(self.property_list, data))


    def add_employee(self, username, password, name, roles):
        query = f"insert into {self.table} " + " ({}, {}, {}, {}) values (%s, %s, %s, %s)".format(*self.property_list[1:])
        self.execute_no_return(query, (username, password, name, roles))


    def get_all(self):
        query = f"select * from {self.table}"
        records = self.execute_return(query)
        return self.__to_dictionary(records)



class CarIssuesDatabase(AbstractDatabase):
    CAR_ID = "Car_ID"
    ID = "ID"
    ENGINEER_ID = ""





if __name__ == "__main__":
    # First database
    account_db = UserDatabase()   
    # account_db.add_user("hoangesoftblog", "h@angeSoftB1og", "hoang truong", "Thu Duc, TP.HCM", "0973557408")  
    # account_db.add_user("hoangtruongvip", "m@h@dOyUgI", "Truong Quoc Hoang", "1 noi nao do trong TP.HCM", "0913885983")  
    # account_db.add_user("hoang", "159753", "Captain America", "Q.9, TP.HCM", "0908687930")  
    # print(account_db.find_user("hoangesoftblog", "159753"))
    # print(account_db.find_user("hoang", "159753"))
    # account_db.remove_user(6)
    # account_db.update_user(1, cols_update=(account_db.USERNAME, account_db.PASSWORD), new_values=("hoang", "111111"))
    # print(account_db.get_all())
    # print(account_db.get_latest())



    # Second database
    car_db = CarDatabase()
    # car_db.insert_car("Honda Civic", "Sedan", "Black", "4", "Thu Duc", "1000000")
    # car_db.insert_car("Toyota Camry", "Sedan", "Brown", "5", "Q1", "1500000")
    # car_db.insert_car("Fortuner", "Something", "Green", "7", "Q1", "2000000")
    # print(car_db.get_all_car())
    # print(car_db.find_car(""))

    # # Third database
    # booking_db = BookingDatabase()
    # booking_db.add_booking(2, 1, "Hello, it's me!", '2020-01-01 13:10:10', '2020-01-01 14:10:10+05:30')
    # booking_db.add_booking(1, 3, "I want to borrow it!", '2020-01-01 10:10:10', '2020-01-01 10:10:10+05:30')
    # print(booking_db.get_all_booking())

    # Fourth database
    employee_db = EmployeesDatabase()
    employee_db.add_employee("Khanh", "123", "Dang Dinh Khanh", 1)
    employee_db.add_employee("Tui", "159753", "Tui la tui chu la ai", 2)
    employee_db.add_employee("Duc", "111", "Duc la tui", 3)
    print(employee_db.get_all())

    ###### Test set
    # # Test for add same username - table Account
    # account_db.add_user("hoangesoftblog", "h@angeSoftB1og", "hoang truong", "Thu Duc, TP.HCM", "0973557408")  

    # # Test add booking overlap - Table Booking
    # booking_db.add_booking(2, 3, "Let's go to Vung Tau!", '2020-08-01 13:00:00', '2020-08-01 14:05:10')
    
