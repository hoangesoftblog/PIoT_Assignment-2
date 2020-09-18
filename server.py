import bluetooth

def main():
    port = bluetooth.PORT_ANY

    while True:
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", port))
        server_sock.listen(port)

        # Accept the connection
        client_sock, address = server_sock.accept()
        print("Accepted connection from ", address)

        # Receive the data sent from client
        data = client_sock.recv(1024)
        print("received [%s]" % data) 

        client_sock.close()
        server_sock.close()

main()