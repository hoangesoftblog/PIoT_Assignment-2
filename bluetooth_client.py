import bluetooth
import time

while True:
    #### Detect devices
    print("Searching for Bluetooth devices.")
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names = True)
    print("Found %d devices" % len(nearby_devices))

    for addr, name in nearby_devices:
        print("%s - '%s'" % (addr, name))

    #### Start connection and send data here
    is_sent_successfully = False
    for addr, name in nearby_devices:
        print()
        print(f"Connecting with {name} - {addr}")
        try:
            # Socket mush be opened and closed for each time
            # To avoid Error 9 - Bad file descriptor
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

            # Connect error will raise Error 11 - Connection refused
            sock.connect((addr, 1))

            # Try to send Engineer ID
            sock.send(str(2))
            sock.recv(1024)

            # Try to send Car ID
            car_id = int(input("Enter Car ID you are fixing: "))
            sock.send(str(car_id))
            sock.recv(1024)

            # Now receive response
            response = sock.recv(1024).decode('ascii')
            print(response)
        except bluetooth.BluetoothError as e:
            print(e)
        except:
            raise
        else:
            print("Finish message")
            is_sent_successfully = True
        finally:
            sock.close()
            pass

    if is_sent_successfully:
        stop_time = 10
        print()
        print(f"Stop for {stop_time} seconds")
        time.sleep(stop_time)