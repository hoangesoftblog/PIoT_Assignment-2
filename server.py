# # # MP Bluetooth

import bluetooth
      
def MP_bluetooth():

    msg="hello"
    
    while True:

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

            sock.close()

MP_bluetooth()



