#Abdullah barghouti 
#CS494 IRC project

import socket, sys, select


PORT = 12345
MESSAGE_SIZE = 2048

#class to handle the different cases associated with channels
class Channel:
    def __init__(self, name):
        self.name = name
        self.client_list = []

    def get_started(self, new_client):
        message = "a new user has joined!\n"
        self.broadcast_all(new_client, message)
        message = "say hello to"+ " " + new_client.name + "!\n"
        self.broadcast_all(new_client, message)
        new_client.socket.sendall(message.encode())

    #broadcast function
    #takes the message and the name of teh person who is sending the message
    def broadcast_all(self, current_client, message):
        #send to everyone
        client_count = 0
        if len(self.client_list) > 0:
            #find everyone. but dont send it to the person that sent it initially 
            while client_count < len(self.client_list):
                if not self.client_list[client_count] == current_client:
                    self.client_list[client_count].socket.sendall(b'' + message.encode())
                client_count += 1

    #handle a user leaving a channel
    def client_exit(self, current_client):
        message = current_client.name + " left\n"
        self.broadcast_all(current_client, message)
        message = "You have exited the channel\n"
        current_client.socket.sendall(message.encode())
        #remove the user from the list
        self.client_list.remove(current_client)

class Server:
    def __init__(self):
        #randomized variables
        self.randomized = []
        #channel list
        self.channel_list = {}
        #user list
        self.client_list = []

    def broadcast_all(self, current_client, message):
        #broscast a message to all available clinets except the sender of the message
        client_count = 0
        print(self.client_list)
        print(message)
        if len(self.client_list) > 0:
            while client_count < len(self.client_list):
                if not self.client_list[client_count] == current_client:
                    self.client_list[client_count].socket.sendall(message.encode())
                client_count += 1

    #broadcast a message when a user disconnects from teh channel/ server
    def disconnect(self, disconnecting_client):
        message = disconnecting_client.name + " has disconnected from the server\n"
        self.broadcast_all(disconnecting_client, message)
        if not len(disconnecting_client.member):
            for channel in disconnecting_client.member:
                self.channel_list[channel].client_list.remove(disconnecting_client)
        self.client_list.remove(disconnecting_client)

    #this function will handle the message
    #all message that start with / will be speciic commands

    def userspace(self, current_client, msg):
        message = msg.split() if not len(msg) == 0 else print("Blank message received\n")

        #JOIN [ARG1 channel TO JOIN]
        if "$j" == message[0]:
            if len(message) == 2:
                channel_name = message[1]
                if channel_name in self.channel_list and channel_name in current_client.member:
                    temp_message = "cant join a channel you are already a member in\n"
                    current_client.socket.sendall(temp_message.encode())
                elif channel_name in self.channel_list:
                    self.channel_list[channel_name].client_list.append(current_client)
                    self.channel_list[channel_name].get_started(current_client)
                    current_client.member.append(channel_name)
                else:
                    temp_message = "ERROR. No channel with that name. Create it to join it\n"
                    current_client.socket.sendall(temp_message.encode())
            else:
                temp_message = "this command take in one arguemnt, the name of the channel you would like to join\n"
                current_client.socket.sendall(temp_message.encode())

        #CREATE [ARG1 channel TO CREATE]
        elif "$c" == message[0]:
            if len(message) == 2:
                #check if the channel exists
                channel_name = message[1]
                if channel_name in self.channel_list:
                    temp_message = "ERROR. a channel with that name exists\n"
                    current_client.socket.sendall(temp_message.encode())
                #if the channel doesnt exist, create it and add it to the list
                else:
                    new_channel = Channel(channel_name)
                    self.channel_list[channel_name] = new_channel
                    self.channel_list[channel_name].client_list.append(current_client)
                    current_client.member.append(channel_name)
                    temp_message = channel_name + " has been created!\n" 
                    current_client.socket.sendall(temp_message.encode())
            else:
                temp_message = "this command take in one arguemnt, the name of the channel you would like to create\n"
                current_client.socket.sendall(temp_message.encode())

        #CREATE [ARG1 channel TO DELETE]
        elif "$d" == message[0]:
            if len(message) == 2:
                channel_name = message[1]
                if channel_name in self.channel_list:
                    del dict(self.channel_list)[channel_name]
                    temp_message = channel_name + " has been removed \n"
                    current_client.socket.sendall(temp_message.encode())
                else:
                    temp_message = "ERROR. That channel doesn't exist\n"
                    current_client.socket.sendall(temp_message.encode())
            else:
                temp_message = "this command take in one arguemnt, the name of the channel you would like to delete\n"
                current_client.socket.sendall(temp_message.encode())

        #EXIT [ARG1 channel TO LEAVE]
        elif "$e" == message[0]:
            if len(message) == 2:
                channel_name = message[1]
                #are you in the channel? 
                if channel_name in self.channel_list and channel_name in current_client.member:
                    self.channel_list[channel_name].client_exit(current_client)
                    current_client.member.remove(channel_name)
                    temp_message = "you left " + channel_name + "\n"
                #you are not in the channel
                elif channel_name in self.channel_list and channel_name not in current_client.member:
                    temp_message = "ERROR. you cant leave a group that you are not apart of \n"
                    current_client.socket.sendall(temp_message.encode())
                else:
                    temp_message = "ERROR. no channel with that name\n"
                    current_client.socket.sendall(temp_message.encode())
            else:
                temp_message = "this command take in one arguemnt, the name of the channel you would like to leave\n"
                current_client.socket.sendall(temp_message.encode())

        #GROUP MESSAGE [ARG1 channel NAME] [ARG2 THE MESSAGE YOU WANT TO SEND]
        elif "$m" == message[0]:
            #send a group message to a specific channel
            if len(message) > 2:
                channel_name = message[1]
                #find the channel
                if channel_name in self.channel_list and current_client in self.channel_list[channel_name].client_list:
                        channel_message = channel_name + " " + current_client.name + ": " + msg.split(' ', 2)[2]
                        self.channel_list[channel_name].broadcast_all(current_client, channel_message)
                        current_client.socket.sendall(b'#' + channel_message.encode())
                elif current_client not in self.channel_list[channel_name].client_list:
                        temp_message = "you dont have access to that group. try joining it it to broadcast to it\n"
                        current_client.socket.sendall(temp_message.encode())
                else:
                        temp_message = "ERROR. No channel with that name\n"
                        current_client.socket.sendall(temp_message.encode())
            else:
                temp_message = "this command take in two arguemnts, the name of the channel you would like to send a message to and the message\n"
                current_client.socket.sendall(temp_message.encode())

        #PERSONAL MESSAGE [ARG1 USERNAME] [ARG2 THE MESSAGE YOU WANT TO SEND]
        elif "$p" == message[0]:
            if len(message) > 2:
                receiving_client = message[1]
                sent = False
                for x in self.client_list:
                    if x.name == receiving_client:
                        temp_message = "@" + current_client.name + ": " + msg.split(' ', 2)[2]
                        x.socket.sendall(temp_message.encode())
                        current_client.socket.sendall(temp_message.encode())
                        sent = True
                if sent is False:
                    temp_message = "That user doesn't exist\n"
                    current_client.socket.sendall(temp_message.encode())
            else:
                temp_message = "this command take in two arguemnts, the name of the user you would like to send a message to and the message\n"
                current_client.socket.sendall(temp_message.encode())
        
        #LIST 
        elif "$l" == message[0]:
                #display all the channels currently available for the server
                #if there arent any to list
                if len(self.channel_list) == 0:
                    message = "sorry. no channels exist"
                    current_client.socket.sendall(message.encode())
                else:
                    message = "here is the list of available channels:\n"
                    current_client.socket.sendall(message.encode())
                    for channel in self.channel_list:
                        message = self.channel_list[channel].name + '\n'
                        current_client.socket.sendall(message.encode())

        #display the list of users that are currently conntect to the server
        #AVAILABLE 
        elif "$a" == message[0]:
            #users in this channel
            if len(message) == 1:
                temp_message = "users in this channel: "
                for x in self.client_list:
                    temp_message += x.name + ", "
                temp_message += "\n"
            #users in another channel
            elif len(message) == 2:
                channel_name = message[1]
                if channel_name in self.channel_list:
                    temp_message = "users in *" + channel_name + "* include: "
                    for x in self.channel_list[channel_name].client_list:
                        temp_message += x.name + ", "
                    temp_message += "\n"
                else:
                    temp_message = "ERROR! channel doesnt exist\n"
            else:
                temp_message = "\n This command only takes a maximum of two arguments\n"
            current_client.socket.sendall(temp_message.encode())

