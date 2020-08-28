# CAR RENTAL SYSTEM
by BIG CITY BOIS
Pham Trung Hieu - Truong Quoc Hoang - Ho Minh Duc - Dang Dinh Khanh

## What is this?

Car Rental System is an Internet of Things project developed by the Big City Bois group, facilitated by RMIT Vietnam's Programming IoT course, which is dedlivered by Dr. Tao Gu and Dr. Anna-Lyza Felipe Sancho.

The goal of this system is to allow customers to rent cars to drive themselves. The system is applicable to use at parking lots with a lot of registered cars from the system owners. Through the raspberry Pi installed nearby, the customers can book their preferred cars and provide their credentials to the car to unlock the car and take it for a ride.

The for types of users are:
- Customers: The users that would like to book the car and use them for a certain amount of days. The customers are able to go to the nearby installed raspberry Pi, register/login the system, choose a car they would like to book, the days that they are booking. One the days that the cars are available to them, the car would allow the customer to unlock them through their user credentials, a QR that was provided by the system at the time they made the booking, or through facial recognition. At the end of the timeframe that they booked the car, they have to be returned or extra charges will be put on the customer.
- System admins: The users that are able to view and manage cars information and update car statuses. They also report damaged cars to engineers to have the problem sorted out.
- Company managers: The users that are provided with statistical information from the Car Rental System.
- Engineers: The users responsible for fixing the damaged cars, reported by the system admins. When a car is reported that it needs fixing, the car will unlock itself once the engineer come close to the car.

## System details:
The system involves using 2 kinds of Raspberry Pi:
- The master Pi (MP): where the users can register, login, book the cars. System admins, company managers will be able to manage and view statistics base on their respective permission. 
- The agent Pi (AP) are installed on each cars that the company has registered for the system. They provide security, making sure that only the customers that have booked the right car can use the car. They will also detect engineers that are appointed to fix/maintain thee car.





## Instruction:







## User credentials, used for testing:
- Customer:
    username:
    password:
- System admin:
    username:
    password:
- Company manager:
    username:
    password:
- Engineer:
    username:
    password:


## Contribution Reports:
### Github:






### Trello:















