import socket
from threading import Thread

port = 6000
ip = '127.0.0.1'

SERVER = None

clients = {}

def handleShowList(client):
    global clients

    for i in clients:
        connected_with = clients[i]['connected_with']
        if connected_with:
            msg = f"{i}, connected with, {connected_with},: New"
        else:
            msg = f"{i}: Available"
        
        client.send(msg.encode())

def removeClient(client_name):
    print('func')

def handleMessages(client, message, client_name):
    if message == 'Show list':
        handleShowList(client)

def handleClient(client, client_name):
    global SERVER
    global clients

    msg = "Welcome, you have been connected to the server. Click on refresh to see all available users."
    client.send(msg.encode())

    while True:
        try:
            msg_all = client.recv(2048).decode()

            if msg_all:
                handleMessages(client, msg_all, client_name)
            else:
                removeClient(client_name)
                break
        except:
            break

def acceptConnections():
    global SERVER
    global clients

    while True:
        client, addr = SERVER.accept()

        client_name = client.recv(2048).decode()

        clients[client_name] = {
            'client': client,
            'addr': addr,
            'connected_with': client_name,
            'file_name': '',
            'file_size': 2048
        }

        print(f'Connection established with {client_name} at {addr}')

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

server_thread = Thread(target=setup)
server_thread.start()