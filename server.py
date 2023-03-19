import socket
from threading import Thread
import time
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

port = 6000
ip = '127.0.0.1'

SERVER = None

clients = {}

is_dir_exist = os.path.isdir('utils')

if not is_dir_exist:
    os.makedirs('utils')


def connectClient(msg, client, client_name):
    global clients

    entered_client_name = msg.split(" ")[1]
    if entered_client_name in clients:
        if not clients[client_name]["connected_with"]:
            clients[entered_client_name]["connected_with"] = client_name
            clients[client_name]["connected_with"] = entered_client_name

            greet_msg = f"Hello, {entered_client_name} {client_name} connected with you"
            target_client = clients[entered_client_name]["client"]
            target_client.send(greet_msg.encode())

            msg = f"You are connected with {entered_client_name}"
            client.send(msg.encode())
        else:
            target_client_name = clients[client_name]["connected_with"]
            msg= f"You are already connected with {target_client_name}"

            client.send(msg.encode())

def disconnectClient(msg, client, client_name):
    global clients

    entered_client_name = msg.split(" ")[1]
    if entered_client_name in clients:
        clients[entered_client_name]["connected_with"] = ""
        clients[client_name]["connected_with"] = ""

        goodbye_msg = f"You have been disconnected"
        target_client = clients[entered_client_name]["client"]
        target_client.send(goodbye_msg.encode())
        client.send(goodbye_msg.encode())  
    else:
        msg= f"You are already disconnected"

        client.send(msg.encode())

def handleShowList(client):
    global clients

    counter = 0
    for c in clients:
        counter +=1
        client_address = clients[c]["address"][0]
        connected_with = clients[c]["connected_with"]
        message =""
        if(connected_with):
            message = f"{counter},{c},{client_address}, connected with {connected_with},tiul,\n"
        else:
            message = f"{counter},{c},{client_address}, Available,tiul,\n"
        client.send(message.encode())
        time.sleep(1)

def removeClient(client_name):
    print('func')

def sendTextMessage(client_name, message):
    global clients
    other_client_name = clients[client_name]["connected_with"]

    other_client_socket = clients[other_client_name]["client"]
    final_message = client_name + "-> " +message

    other_client_socket.send(final_message.encode())

def handleErrorMessage(client):
    global clients

    message = "User error 1xcd34: Client has no active connection"
    client.send(message.encode())

def handleSendFile(client_name, file_name, file_size):
    global clients

    clients[client_name]["file_name"] = file_name
    clients[client_name]["file_size"] = file_size

    other_client_name = clients[client_name]["connected_with"]
    other_client_addr = clients[other_client_name]["client"]

    message = f'\n{file_name} with a size of {file_size} bytes wants to be sent from {client_name}. Do you want to download (Y/N)?'
    other_client_addr.send(message.encode())

    message2 = f'Download: {file_name}'
    other_client_addr.send(message2.encode())

def grantAccess(client_name):
    global clients

    other_client_name = clients[client_name]["connected_with"]
    other_client_addr = clients[other_client_name]["client"]

    message = "Access granted"
    other_client_addr.send(message.encode())

def declineAccess(client_name):
    global clients

    other_client_name = clients[client_name]["connected_with"]
    other_client_addr = clients[other_client_name]["client"]

    message = "Access denied"
    other_client_addr.send(message.encode())

def handleMessages(client, message, client_name):
    if message == 'show list':
        handleShowList(client)
    elif message[:7] == "connect":
        connectClient(message, client, client_name)
    elif message[:10] == "disconnect":
        disconnectClient(message, client, client_name)
    elif message[:4] == "send":
        file_name = message.split(" ")[1]
        file_size = int(message.split(" ")[2])
        handleSendFile(client_name, file_name, file_size)
    elif message == "Y":
        grantAccess(client_name)
    elif message == "N":
        declineAccess(client_name)
    else:
        connected = clients[client_name]["connected_with"]
        if connected:
            sendTextMessage(client_name, message)
        else:
            handleErrorMessage(client)

def handleClient(client, client_name):
    global SERVER
    global clients

    msg = "Welcome, you have been connected to the server. Click on refresh to see all available users."
    client.send(msg.encode())

    while True:
        try:
            chunk = client.recv(2048)
            msg_all = chunk.decode().strip().lower()

            if msg_all:
                handleMessages(client, msg_all, client_name)
        except:
            break

def acceptConnections():
    global SERVER
    global clients

    while True:
        client, addr = SERVER.accept()

        client_name = client.recv(2048).decode().lower()

        clients[client_name] = {
            "client"         : client,
            "address"        : addr,
            "connected_with" : "",
            "file_name"      : "",
            "file_size"      : 2048
        }

        print(f'Connection established with {client_name} at {addr}')
        print(clients)

        thread = Thread(target=handleClient, args=(client, client_name))
        thread.start()

def setup():
    global SERVER

    global port
    global ip

    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((ip, port))

    SERVER.listen()
    print('Server is active')

    acceptConnections()
    
def ftp():
    global ip

    authorizer = DummyAuthorizer()
    authorizer.add_user("User", "abcd12345", ".", perm="elradfwm")

    handler = FTPHandler
    handler.authorizer = authorizer

    ftp_server = FTPServer((ip, 21), handler)
    ftp_server.serve_forever()

server_thread = Thread(target=setup)
server_thread.start()

ftp_thread = Thread(target=ftp)
ftp_thread.start()
