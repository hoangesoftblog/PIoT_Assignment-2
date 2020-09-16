# # # AP Bluetooth

import bluetooth


def AP_bluetooth():
    port = bluetooth.PORT_ANY

    while True:
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", port))
        server_sock.listen(port)

        # Accept the connection
        client_sock, address = server_sock.accept()
        print("Accepted connection from ", address)

        # Print data
        print('HIIIIIIIIIIIIIIII')

        client_sock.close()
        server_sock.close()

AP_bluetooth()