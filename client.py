import bluetooth
      

def main():

    while True:
        
        status = "OK"

        #### Detect devices
        devices = bluetooth.discover_devices(lookup_names = True)
        
        #### Start connection and send data here
        for addr, name in devices:
            # Socket mush be opened and closed for each time
            # To avoid Error 9 - Bad file descriptor
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

            sock.send(status)

            sock.close()

main()