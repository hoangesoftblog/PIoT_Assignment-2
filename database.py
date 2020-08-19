"""
                                BIG BIG NOTE: 
                    This code is only applied for SQLite only.
                        Needs to change into MySQL
"""
"https://code.tutsplus.com/vi/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972"


#import MySQLdb as SQLDatabase
import sqlite3 as SQLDatabase
import datetime
import flask

host = "localhost"
user = "root"
password = "h@angeSoftB1og"
schema = "temps"

TEMPORARY_DATABASE = "database.db"

class AccountDatabase:
    USER = "username"
    PASS = "password"
    ID = "ID"


    def __init__(self, host=host, user=user, password=password, schema=TEMPORARY_DATABASE, tb_name="Account", drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password

        
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} (ID INTEGER primary key autoincrement, {self.USER} varchar(50), {self.PASS} varchar(50))"
        self.__execute_no_return(query)
    

    def __execute_no_return(self, query, data=None):
        # self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        self.connector = SQLDatabase.connect(self.database)
        self.cursor = self.connector.cursor()

        if data:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

        self.connector.commit()
        self.connector.close()


    def __execute_return(self, query, data=None, amount="many"):
        # self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        self.connector = SQLDatabase.connect(self.database)
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

    def __to_dictionary(self, data):
        if isinstance(data, dict):
            return data
        elif isinstance(data, tuple):
            return {self.ID: data[0], self.USER: data[1], self.PASS: data[2]}
        elif isinstance(data, list):
            return [self.__to_dictionary(child_data) for child_data in data]
        else:
            return None


    def add_user(self, username, password):
        query = f"insert into {self.table}({self.USER}, {self.PASS}) values (?, ?)"
        self.__execute_no_return(query=query, data=(username, password))


    def get_all(self):
        query = "select * from " + self.table
        return self.__execute_return(query)


    def find_user(self, username, password):
        query = f"select * from {self.table} where {self.USER} = ? and {self.PASS} = ?"
        records = self.__execute_return(query, (username, password))
        return records


class CarDatabase:
    BRAND = "brand"
    MAKE = BRAND
    BODY_TYPE = "body_type"
    COLOUR = "colour"
    SEATS = "seats"
    LOCATION = "location"
    COST_PER_HOUR = "cost_per_hour"
    ID = "ID"

    def __init__(self, host=host, user=user, password=password, schema=TEMPORARY_DATABASE, tb_name="Car", drop_existing_table=False):
        self.database = schema
        self.table = tb_name
        self.host = host
        self.user = user
        self.password = password
        
        if drop_existing_table:
            query = "DROP TABLE IF EXISTS " + self.table
            self.cursor.execute(query)
        
        query = f"CREATE TABLE IF NOT EXISTS {self.table} (ID INTEGER primary key autoincrement, {self.BRAND} varchar(20), {self.BODY_TYPE} varchar(30), {self.COLOUR} varchar(40), {self.SEATS} numeric, {self.LOCATION} varchar(100), {self.COST_PER_HOUR} numeric)"
        self.__execute_no_return(query)

    def __execute_no_return(self, query, data=None):
        # self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        self.connector = SQLDatabase.connect(self.database)
        self.cursor = self.connector.cursor()

        if data:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

        self.connector.commit()
        self.connector.close()


    def __execute_return(self, query, data=None, amount="many"):
        # self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        self.connector = SQLDatabase.connect(self.database)
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


    def __to_dictionary(self, data):
        if isinstance(data, dict):
            return data
        elif isinstance(data, tuple):
            return {self.ID: data[0], self.BRAND: data[1], self.BODY_TYPE: data[2], self.COLOUR: data[3], self.SEATS: data[4], self.LOCATION: data[5], self.COST_PER_HOUR: data[6]}
        elif isinstance(data, list):
            return [self.__to_dictionary(child_data) for child_data in data]
        else:
            return None


    def insert_car(self, brand, body, color, seats, location, cost):
        query = f"""insert into {self.table} ({self.BRAND}, {self.BODY_TYPE}, {self.COLOUR}, {self.SEATS}, {self.LOCATION}, {self.COST_PER_HOUR}) 
        values(?, ?, ?, ?, ?, ?)"""

        self.__execute_no_return(query, (brand, body, color, seats, location, cost))

    def get_all_car(self):
        query = f"select * from {self.table}"
        records = self.__execute_return(query)
        return self.__to_dictionary(records)

    def find_car(self, search_term: str):
        query = f"""select * from {self.table} 
        where {self.BRAND} LIKE ? OR {self.BODY_TYPE} LIKE ? OR {self.COLOUR} LIKE ? OR {self.LOCATION} LIKE ?"""

        records = self.__execute_return(query, tuple([("%" + search_term + "%") for i in range(4)]))

        if search_term.isnumeric():
            query = f"""select * from {self.table} 
            where {self.SEATS} = ? OR {self.COST_PER_HOUR} = ?"""
            records_2 = self.__execute_return(query, tuple([search_term for i in range(2)]))
            records.extend(records_2)

        return self.__to_dictionary(records)


def HistoryDatabase():
    def __execute_no_return(self, query, data=None):
        # self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        self.connector = SQLDatabase.connect(self.database)
        self.cursor = self.connector.cursor()

        if data:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

        self.connector.commit()
        self.connector.close()


    def __execute_return(self, query, data=None, amount="many"):
        # self.connector = SQLDatabase.connect(self.host, self.user, self.password, self.database)
        self.connector = SQLDatabase.connect(self.database)
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




if __name__ == "__main__":
    db = AccountDatabase()    
    # db.add_user("hoangesoftblog", "h@angeSoftB1og")    
    print(db.get_all())

    db_2 = CarDatabase()
    # db_2.insert_car("Honda Civic", "SUV", "Black", "4", "Thu Duc", "1000000")
    # db_2.insert_car("Toyota Camry", "Sedan", "Brown", "5", "Q1", "1500000")
    print(db_2.get_all_car())