import socket

def tcp_start_server():
    ADDRESS = ("", 65000)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(ADDRESS)
        s.listen()

        print("Listening on {}...".format(ADDRESS))
        conn, addr = s.accept()
        with conn:
            print("Connected to {}".format(addr))

            while True:
                data = conn.recv(4096)
                if(not data):
                    break
                print("Received {} bytes of data decoded to: '{}'".format(
                    len(data), data.decode()))
                print("Sending data back.")
                conn.sendall(data)
            
            print("Disconnecting from client.")
        print("Closing listening socket.")
    print("Done.")

def tcp_client_send_message(message):
    HOST = input("Enter IP address of server: ")

    # HOST = "127.0.0.1" # The server's hostname or IP address.
    PORT = 65000         # The port used by the server.
    ADDRESS = (HOST, PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("Connecting to {}...".format(ADDRESS))
        s.connect(ADDRESS)
        print("Connected.")

        while True:
            if(not message):
                break
            
            s.sendall(message.encode())
            data = s.recv(4096)
            print("Received {} bytes of data decoded to: '{}'".format(
                len(data), data.decode()))
        
        print("Disconnecting from server.")
    print("Done.")

def udp_start_server():
    localIP     = "127.0.0.1"
    localPort   = 20001
    bufferSize  = 1024

    msgFromServer       = "Hello UDP Client"
    bytesToSend         = str.encode(msgFromServer)

    
    # Create a datagram socket
    # communication domain in which the socket should be created. Some of address families are AF_INET (IP), AF_INET6 (IPv6), 
    # AF_UNIX (local channel, similar to pipes), AF_ISO (ISO protocols), and AF_NS (Xerox Network Systems protocols).
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind((localIP, localPort))
    print("UDP server up and listening")

    # Listen for incoming datagrams
    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        
        print(clientMsg)
        print(clientIP)

        # Sending a reply to client
        UDPServerSocket.sendto(bytesToSend, address)

def udp_client_send_message(message):
    bytesToSend         = str.encode(message)
    serverAddressPort   = ("127.0.0.1", 20001)
    bufferSize          = 1024

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Message from Server {}".format(msgFromServer[0])

    print(msg)