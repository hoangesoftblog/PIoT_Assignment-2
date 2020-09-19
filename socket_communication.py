import socket
import database
import json
import datetime

login_db = database.LoginDatabase()
booking_db = database.BookingDatabase()
issues_db = database.IssuesDatabase()

def tcp_start_server():
    """Start the server with TCP protocol, handle all message sent by the clients
    """
    #### Dataflow for Socket Communication
    # 1) Receive a message what kind of login it is from Client
    # 2) Receive the data from the Login
    # 3) Check if that user is using the right car at the right time
    ADDRESS = ("localhost", 65433)  
    # Standard loopback interface address (localhost)
    # Port to listen on (non-privileged ports are > 1023)
    
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(ADDRESS)
            s.listen()

            print("Listening on {}...".format(ADDRESS))
            conn, addr = s.accept()
            with conn:
                print("Connected to {}".format(addr))
                user = conn.recv(1024).decode()
                print("Login as:", user)
                conn.sendall("Done".encode())

                if user == "Users":
                    data = conn.recv(1024).decode()
                    print("Login type", data)
                    conn.sendall("Done".encode())
                    # data = conn.recv(4096)
                    if data == "Normal":
                        # Receive and parse the login info
                        received_json = conn.recv(1024)
                        received_json = received_json.decode()
                        login_info = json.loads(received_json)
                        print("Login info:", login_info)
                        conn.sendall("Done".encode())

                        car_id = login_info.get(booking_db.CAR_ID)
                        del login_info[booking_db.CAR_ID]

                        # Find the login records
                        records = login_db.login_existed(**login_info)
                        print("User records:", records)
                        if len(records) == 1:
                            UserID = records[0][login_db.ID]
                            # Check for booking records
                            booking_records = booking_db.find_booking(**{
                                booking_db.USER_ID: UserID, 
                                booking_db.CAR_ID: car_id, 
                                booking_db.FROM: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                            print("Check booking records:", booking_records)
                            # Send message after getting the records
                            if len(booking_records) > 0:
                                conn.sendall("Correct".encode())
                            else:
                                conn.sendall("No booking at this time".encode())
                        else:
                            conn.send("Incorrect info".encode())
                            
                    elif data == "Facial":
                        received_json = conn.recv(1024)
                        received_json = received_json.decode()
                        login_info = json.load(received_json)
                        
                        booking_records = booking_db.find_booking(**{
                            booking_db.FROM: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            **login_info
                        })
                        if len(booking_records) > 0:
                            conn.sendall("Correct".encode())
                        else:
                            conn.sendall("No booking at this time".encode())
                    elif data == "":
                        print("Empty data")
                    else:
                        print("Unknown data:", data)

                elif user == "Engineers":
                    data = conn.recv(1024).decode()
                    print("Login type", data)
                    # data = conn.recv(4096)
                    conn.sendall("Done".encode())
                    if data == "Normal":
                        # Receive and parse the login info
                        received_json = conn.recv(1024)
                        received_json = received_json.decode()
                        login_info = json.loads(received_json)
                        print("Login info:", login_info)
                        conn.sendall("Done".encode())

                        car_id = login_info.get(issues_db.CAR_ID)
                        del login_info[issues_db.CAR_ID]

                        # Find the login records
                        records = login_db.login_existed(**login_info)
                        print("Engineers records:", records)
                        if len(records) == 1:
                            UserID = records[0][login_db.ID]
                            # Check for issues records
                            issues_records = issues_db.find_issues(**{
                                issues_db.ENGINEER_ID: UserID, 
                                issues_db.CAR_ID: car_id, 
                                })
                            print("Check issues records:", issues_records)
                            # Send message after getting the records
                            if len(issues_records) > 0:
                                conn.sendall("Correct".encode())
                            else:
                                conn.sendall("No issues for you to fix at this time".encode())
                        else:
                            conn.send("Incorrect info".encode())
                            
                    elif data == "QR":
                        received_json = conn.recv(1024)
                        received_json = received_json.decode()
                        login_info = json.load(received_json)
                        
                        booking_records = booking_db.find_booking(**{
                            booking_db.FROM: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            **login_info
                        })
                        if len(booking_records) > 0:
                            conn.sendall("Correct".encode())
                        else:
                            conn.sendall("No booking at this time".encode())
                    elif data == "":
                        print("Empty data")
                    else:
                        print("Unknown data:", data)        

                # print("Sending data back.")
                # conn.sendall(data)
                
                # print("Disconnecting from client.")
        print("Closing listening socket.")
        print()


class Socket_Client:
    """ The Socket client class, send all messages to the server through TCP protocol
    """
    # HOST = "127.0.0.1" # The server's hostname or IP address.
    HOST = "localhost" # The server's hostname or IP address.
    PORT = 65433        # The port used by the server.
    ADDRESS = (HOST, PORT)

    def __init__(self):
        self.the_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to {}...".format(self.ADDRESS))
        self.the_socket.connect(self.ADDRESS)
        print("Connected.")


    def send_message(self, message):
        """Send the message to the server
        
        Parameters
        ----------
        message
            The message to send
        """
        self.the_socket.sendall(message)


    def receive_message(self):
        """Return the message the server sentback
        """
        message = self.the_socket.recv(1024)
        return message.decode()


    def __del__(self):
        print("Close socket")
        self.the_socket.close()


if __name__ == "__main__":
    tcp_start_server()
    # tcp_client_send_message("Hey")
