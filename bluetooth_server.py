import bluetooth
import database
 
port = 1

while True:
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))

    print("Listening ...")
    server_sock.listen(port)

    client_sock, (address, client_port) = server_sock.accept()
    print("Accept from ", address, " - ", client_port)

    # Receive Engineer ID and return acknowledgement
    engineer_id = int(client_sock.recv(1024).decode('ascii'))
    server_sock.send("Done".encode('ascii'))

    # Receive Car ID and return acknowledgement
    car_id = int(client_sock.recv(1024).decode('ascii'))
    server_sock.send("Done".encode('ascii'))

    # Check from database for the Issue
    car_db = database.CarDatabase()
    issues_db = database.IssuesDatabase()
    
    records = issues_db.find_issues(**{issues_db.CAR_ID: car_id, issues_db.ENGINEER_ID: engineer_id})
    if len(records) > 0:
        server_sock.send("Granted".encode('ascii'))
    else:
        server_sock.send("Denied".encode('ascii'))

    client_sock.close()
    server_sock.close()