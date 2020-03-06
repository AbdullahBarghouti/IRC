#Abdullah barghouti 
#CS494 IRC project


import socket, sys, select, random, time
import supp


host_name = socket.gethostname()
host_port = 12345
MESSAGE_SIZE = 1000
MAX_ClIENTS = 25

class Client:
    def __init__(self, soc):
        self.member = []
        self.socket = soc
        self.name = "New_Client_" + str(random.randint(1, 100))

    def fileno(self):
        return self.socket.fileno()

def create_socket(server_address):
    # Create the server socket
    try:
        #tcp socket ipv4
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #mititage "address already in use" error
        new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #non-blocking socket
        new_socket.setblocking(False)
        #connect socket to network
        new_socket.bind(server_address)
        #listen to a maximum of 25 users
        new_socket.listen(MAX_ClIENTS)

        print("SUCCESSFUL!! SOCKET CREATION AT PORT",host_port)
        return new_socket
    except:
        print("****SOCKET FALURE!!!****\n")
        sys.exit()

socket = create_socket((host_name, host_port))
supplementary = supp.Server()
client_list = [socket]

while True:
    try:
        client_read, client_write, errors = select.select(client_list, [], [])
        for client in client_read:
            #new client 
            if client is socket:
                new_socket, server_address = client.accept()
                print("server_address ", server_address)
                #create new client
                new_client = Client(new_socket)
                #add client to list
                client_list.append(new_client)
                message = ">>> SUCCESS! You have joined the server!\n"
                new_client.socket.sendall(message.encode())
            #not a new client
            #new message to come
            else:
                message = client.socket.recv(MESSAGE_SIZE)
                print(message)
                if message:
                    #send the message to the client
                    supplementary.userspace(client, message.decode())
                else:
                    #user disconnected
                    print("User disconnected\n")
                    client.socket.close()
                    supplementary.disconnect(client)
                    client_list.remove(client)

    except KeyboardInterrupt:
        supplementary.broadcast_all(socket, "BYEEEE")
        socket.close()
        client_list.remove(socket)
        sys.exit()
