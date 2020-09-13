# # # MP Bluetooth

import bluetooth
      
def MP_bluetooth():

    msg="hello"
    
    while True:
        print("Looking for bluetooth device")
        #### Detect devices
        devices = bluetooth.discover_devices(lookup_names = True)
        #### Start connection and send data here
        for addr, name in devices:
            # Socket mush be opened and closed for each time
            # To avoid Error 9 - Bad file descriptor
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

            # Connect error will raise Error 11 - Connection refused
            sock.connect((addr, 1))
            sock.send(msg)
            print("Sent")

            sock.close()

# MP_bluetooth()

# # # AP Bluetooth


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

# AP_bluetooth()

