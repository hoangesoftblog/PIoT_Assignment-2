# import sys

# import bluetooth

# class Bluetooth_Client:
#     addr = None
#     host_name = None
#     port_name = None
#     sock = None
#     service_matches = None

#     def __init__(self):
#         uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
#         self.service_matches = bluetooth.find_service(uuid=uuid, address=self.addr)

#     def finding_sampleServer(self):
#         while True:
#             if len(self.service_matches) == 0:
#                 print("Couldn't find the SampleServer service.")
#                 continue

#             first_match = self.service_matches[0]
#             port = first_match["port"]
#             name = first_match["name"]
#             host = first_match["host"]

#             print("Connecting to \"{}\" on {}".format(name, host))

#             # Generate the client socket
#             self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
#             self.sock.connect((host, port))

#             self.host_name = host
#             self.port_name = port

#             print("Connected. Type something...")
#             break

#     def send_message(self,message):
#         self.sock.send(message)

#     def __del__(self):
#         self.sock.close()

# class Bluetooth_Server():
#     port_any = bluetooth.PORT_ANY

#     def __init__(self):
#         self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
#         self.server_sock.bind(("", self.port_any))

#     def start_server(self):
#         while True:
#             self.server_sock.listen(1)

#             port = self.server_sock.getsockname()[1]

#             uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

#             bluetooth.advertise_service(self.server_sock, "SampleServer", service_id=uuid,
#                                         service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
#                                         profiles=[bluetooth.SERIAL_PORT_PROFILE],
#                                     )     
            
#             print("Waiting for connection on nearby device", port)

#             self.client_sock, address = self.server_sock.accept()
#             print("Accepted connection from", address)

#             self.client_sock.close()

#     def receive_message(self):
#         try:
#             data = self.client_sock.recv(1024)
#             if not data:
#                 pass
#             print("Received", data)
#         except OSError:
#             pass

#     def __del__(self):
#         print("Disconnected.")

#         self.server_sock.close()
#         print("All done.")
    
# if __name__ == "__main__":
#     # # Client test
#     server = Bluetooth_Server()
#     server.start_server()


#     # # Client test
#     # client = Bluetooth_Client()
#     # client.finding_sampleServer()
#     # client.send_message(b'hi')
    

# # if len(sys.argv) < 2:
# #     print("No device specified. Searching all nearby bluetooth devices for "
# #           "the SampleServer service...")
# # else:
# #     addr = sys.argv[1]
# #     print("Searching for SampleServer on {}...".format(addr))

# # search for the SampleServer service

    

    

import sys
import bluetooth

uuid = "1e0ca4ea-299d-4335-93eb-27fcfe7fa848"
service_matches = bluetooth.find_service( uuid = uuid )

if len(service_matches) == 0:
    print("couldn't find the FooBar service")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \"%s\" on %s" % (name, host))

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((host, port))
sock.send("hello!!")
sock.close()

