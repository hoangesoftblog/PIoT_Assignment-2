import socket

def tcp_start_server():
    ADDRESS = ("localhost", 65433)  
    # Standard loopback interface address (localhost)
    # Port to listen on (non-privileged ports are > 1023)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(ADDRESS)
        s.listen()

        print("Listening on {}...".format(ADDRESS))
        conn, addr = s.accept()
        with conn:
            print("Connected to {}".format(addr))

            while True:
                data = conn.recv(1024)
                # data = conn.recv(4096)
                if(not data):
                    break
                print("Received {} bytes of data decoded to: '{}'".format(len(data), data.decode()))
                print("Sending data back.")
                conn.sendall(data)
            
            print("Disconnecting from client.")
        print("Closing listening socket.")
    print("Done.")

def tcp_client_send_message(message):
    # HOST = input("Enter IP address of server: ")

    #HOST = "127.0.0.1" # The server's hostname or IP address.
    HOST = "localhost" # The server's hostname or IP address.
    PORT = 65433        # The port used by the server.
    ADDRESS = (HOST, PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("Connecting to {}...".format(ADDRESS))
        s.connect(ADDRESS)
        print("Connected.")

        while True:
            if(not message):
                break
            
            s.sendall(message.encode())
            # data = s.recv(4096)
            data = s.recv(1024)
            print("Received {} bytes of data decoded to: '{}'".format(
                len(data), data.decode()))
        
        print("Disconnecting from server.")
    print("Done.")

if __name__ == "__main__":
    # tcp_start_server()
    tcp_client_send_message("Hey")
