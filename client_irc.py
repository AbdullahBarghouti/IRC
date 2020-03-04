#Abdullah barghouti 
#CS494 IRC project

import socket, sys, select
import supp

# defaults are localhost and port 12345
host_name = socket.gethostname()
host_port = 12345
MESSAGE_SIZE = 1024

def create_client_socket(client_address):
    try:
        print("client address: ",client_address)
        #new socket TCP IPv4
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #metigate "address already in use"
        new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #connect socket to network
        new_socket.connect(client_address)  
        print("You were connected to the server at port:  %s\n" % (host_port))
        return new_socket
    except:
        print("Connection failed\n")
        sys.exit()

socket = create_client_socket((host_name, host_port))
soc_list = [sys.stdin, socket]
message_prefix = ''

while True:
    try:
        read_socket, write_socket, error = select.select(soc_list, [], [])
        for x in read_socket:
            if x is socket:
                message = socket.recv(MESSAGE_SIZE)
                if not message:
                    print("Server disconnected\n")
                    sys.exit()
                else:
                    sys.stdout.write(message.decode())
                    print("", end="")
            else:
                message = sys.stdin.readline()
                socket.sendall(message.encode())

    except KeyboardInterrupt:
        sys.exit()
