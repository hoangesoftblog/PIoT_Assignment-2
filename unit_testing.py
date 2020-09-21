import unittest
from database import *
import MySQLdb as SQLDatabase
import google_calendar

unittest.TestLoader.sortTestMethodsUsing = None


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


# class TestingGoogleCalendar(unittest.TestCase):
#     def setUp(self):
#         self.calendar = google_calendar.GoogleCalendar()
#         self.events = []
    
#     def add_events(self):
#         event_1 = calendar.add_event(1, 2, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(1), "birthday today")
#         events += [event_1]
#         event_2 = calendar.add_event(2, 3, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(2), "Travel today")
#         events += [event_2]

# Drop schema first
connector = SQLDatabase.connect(host, user, password)
cursor = connector.cursor()
cursor.execute(f"drop database if exists {schema}")
connector.commit()
connector.close()

# Create current database
login_db = LoginDatabase()
user_db = UserDatabase()
car_db = CarDatabase()
employee_db = EmployeesDatabase()
booking_db = BookingDatabase(calendar=google_calendar.GoogleCalendar())
issues_db = IssuesDatabase()

class TestDatabase(unittest.TestCase): 
    # def set       
    def setUp(self):
        # Setup will run before each test
        pass

    def test01_add_login(self):
        login_db.add_login("s3694808@rmit.edu.vn", "Rm!th@angeSoftB1og", "user")
        login_db.add_login("s3618748@rmit.edu.vn", "159753", "engineer")
        login_db.add_login("s3694365@rmit.edu.vn", "123456", "manager")
        login_db.add_login("s3695336@rmit.edu.vn", "Rm!t", "admin")
        login_db.add_login("l9933429@rmit.edu.vn", "password", "user")
        login_db.add_login("random_user@yahoo.com.vn", "password", "user")
        login_db.add_login("random_user2@yahoo.com.vn", "password2", "user")

    def test02_add_users(self):
        user_db.add_user(USER_ID=1, name="hoang truong", address="Thu Duc, TP.HCM", phone_number="0973557408")
        user_db.add_user(USER_ID=5, name="hoang (English)", address="Q. Thu Duc, TP. HCM", phone_number="0973557408")
        user_db.add_user(USER_ID=6, name="Random user", address="TP.HCM, VN", phone_number="0913885983")


    def test03_add_cars(self):
        car_db.insert_car(**{car_db.BRAND: "Honda Civic", car_db.BODY_TYPE: "Sedan", car_db.COLOUR: "Black", car_db.SEATS: "4",
                         car_db.LOCATION: "Thu Duc", car_db.COST_PER_HOUR: "1000000", car_db.LAT: 10.730104, car_db.LNG: 106.691745})
        car_db.insert_car(**{car_db.BRAND: "Toyota Camry", car_db.BODY_TYPE: "Sedan", car_db.COLOUR: "Brown", car_db.SEATS: "5",
                            car_db.LOCATION: "Q1", car_db.COST_PER_HOUR: "1500000", car_db.LAT: 10.857306, car_db.LNG: 106.769463})
        car_db.insert_car(**{car_db.BRAND: "Fortuner", car_db.BODY_TYPE: "Something", car_db.COLOUR: "Green", car_db.SEATS: "7",
                         car_db.LOCATION: "Q1", car_db.COST_PER_HOUR: "2000000", car_db.LAT: 10.856727, car_db.LNG: 106.766620})
        
        
    def test04_add_employees(self):
        employee_db.add_employee(
            **{employee_db.ID: 2, employee_db.NAME: "Dang Dinh Khanh"})
        employee_db.add_employee(
            **{employee_db.ID: 3, employee_db.NAME: "Pham Trung Hieu"})
        employee_db.add_employee(
            **{employee_db.ID: 4, employee_db.NAME: "Ho Minh Duc"})


    def test05_add_bookings(self):
        booking_db.add_booking(CID=2, UID=1, booking_details="Hello, it's me!",
                           from_time='2020-09-24 13:10:10', to_time='2020-09-25 14:10:10')
        booking_db.add_booking(CID=1, UID=6, booking_details="I want to borrow it!",
                            from_time='2020-09-24 05:10:10', to_time='2020-09-26 09:10:10')
        booking_db.add_booking(CID=3, UID=1, booking_details="1234",
                           from_time='2020-10-01 10:10:10', to_time='2020-10-02 10:10:10')
        


    def test06_add_issues(self):
        issues_db.add_issues(CID2=3, Engineer_ID=2)
        issues_db.add_issues(CID2=1, Engineer_ID=2)


    # Test other methods related to UserDatabase
    def test07_find_user(self):
        user_ID1 = user_db.find_user(**{user_db.ID: 1})
        self.assertEqual(user_ID1, [{"USER_ID": 1, "name": "hoang truong", "address": "Thu Duc, TP.HCM", "phone_number": "0973557408", 'created_date': datetime.datetime(2020, 9, 20, 21, 25)}])
        
        user_addressTD = user_db.find_user(**{user_db.ADDRESS: "VN"})
        self.assertEqual(user_addressTD, [{"USER_ID": 6, "name": "Random user", "address": "TP.HCM, VN", "phone_number": "0913885983", 'created_date': datetime.datetime(2020, 9, 20, 21, 25)}])

    def test08_count_user(self):
        list_users = user_db.get_all()
        self.assertTrue(len(list_users) == 3)

    def test09_update_user(self):
        update_ID = user_db.update_user(6, **{user_db.NAME: "Viet Nam oi"})
        self.assertTrue(update_ID == 6)
        self.assertEqual(user_db.find_user(**{user_db.ID: update_ID}), [{"USER_ID": 6, user_db.NAME: "Viet Nam oi", "address": "TP.HCM, VN", "phone_number": "0913885983", 'created_date': datetime.datetime(2020, 9, 20, 21, 25)}])
    
    def test10_delete_user(self):
        user_db.remove_user(5)
        self.assertTrue(len(user_db.get_all()) == 2)
        self.assertTrue(len(login_db.get_all_login()) == 6)


    # Test other methods related to LoginDatabase
    def test11_count_login_infos(self):
        count = login_db.get_all_login()
        self.assertTrue(count == 6)

    # def test12_s
    




if __name__ == "__main__":
    unittest.main()