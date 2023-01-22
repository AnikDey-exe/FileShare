import socket
from threading import Thread
from tkinter import *
from tkinter import ttk

port = 6000
ip = '127.0.0.1'

SERVER = None

user_list = None
chat_box = None
name = None

def recvMsg():
    global SERVER
    global user_list

    while True:
        msg = SERVER.recv(2048).decode()

        if 'New' in msg:
            ab = msg.split(',')
            user_list.insert(ab[0], ab[1])
        else:
            chat_box.insert(msg)

def connectToServer():
    global SERVER
    
    global port
    global ip
    
    global name

    name_s = name.get()

    SERVER.send(name_s.encode())

def showClientsList():
    global SERVER
    global user_list

    SERVER.send("Show list".encode())

def openChatWindow():
    global user_list
    global chat_box
    global name
    
    window = Tk()
    window.title('File Share')
    window.geometry('500x375')
    window.resizable(False, False)

    top_separator = ttk.Separator(window, orient='horizontal')
    top_separator.place(x=0,y=0, relheight=0.01, relwidth=1)

    name_label = Label(window, text='Enter Your Name', font=('Calibri', 10))
    name_label.place(x=10, y=10)

    name = Entry(window, width=30, font=('Calibri', 10))
    name.place(x=115, y=10)

    connect_button = Button(window, text='Connect to Chat Server', width=20, font=('Calibri', 10), command=connectToServer)
    connect_button.place(x=340, y=7.5)

    mid_separator = ttk.Separator(window, orient='horizontal')
    mid_separator.place(x=0,y=40, relheight=0.01, relwidth=1)

    user_label = Label(window, text='Active Users', font=('Calibri', 10))
    user_label.place(x=10, y=50)

    user_list = Listbox(window, height=5, width=68, font=('Calibri', 10))
    user_list.place(x=10, y=75)

    connect = Button(window, text='Connect', width=8, font=('Calibri', 10))
    connect.place(x=260, y=170)

    disconnect = Button(window, text='Disconnect', width=9, font=('Calibri', 10))
    disconnect.place(x=340, y=170)

    refresh = Button(window, text='Refresh', width=8, font=('Calibri', 10), command=showClientsList)
    refresh.place(x=425, y=170)

    chat_label = Label(window, text='Chat Window', font=('Calibri', 10))
    chat_label.place(x=9, y=200)

    chat_box = Text(window, height=6, width=68, font=('Calibri', 10))
    chat_box.place(x=10, y=225)

    attach_button = Button(window, text='Attach & Send', width=15, font=('Calibri', 10))
    attach_button.place(x=10, y=330)

    chat_entry = Entry(window, width=30, font=('Calibri', 13))
    chat_entry.place(x=130, y=330)

    send_button = Button(window, text='Send', width=10, font=('Calibri', 10))
    send_button.place(x=410, y=330)

    window.mainloop()

def setup():
    global SERVER

    global port
    global ip

    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client = SERVER.connect((ip, port))

    client_thread = Thread(target=recvMsg)
    client_thread.start()

    openChatWindow()

setup()