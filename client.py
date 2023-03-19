import socket
from threading import Thread
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from ftplib import FTP
import ntpath
from pathlib import Path
import os

port = 6000
ip = '127.0.0.1'

SERVER = None

user_list = None
chat_box = None
chat_entry = None
file_label = None
chat_label = None
name = None

sending_file = None
downloading_file = None
file_to_download = None
file_size = None

def connectWithClient():
    global SERVER
    global user_list

    text = user_list.get(ANCHOR)
    list_item = text.split(":")
    msg = "Connect "+list_item[1]

    SERVER.send(msg.encode('ascii'))

def disconnectWithClient():
    global SERVER
    global user_list

    text = user_list.get(ANCHOR)
    list_item = text.split(":")
    msg = "Disconnect "+list_item[1]

    SERVER.send(msg.encode('ascii'))

def recvMsg():
    global SERVER
    global user_list
    global file_size
    global chat_label
    global downloading_file
    global file_to_download

    while True:
        chunk = SERVER.recv(2048)

        try:
            if("tiul" in chunk.decode() and "1.0," not in chunk.decode()):
                letter_list = chunk.decode().split(",")
                user_list.insert(letter_list[0],letter_list[0]+":"+letter_list[1]+": "+letter_list[3]+" "+letter_list[5])
                print(letter_list[0],letter_list[0]+":"+letter_list[1]+": "+letter_list[3]+" "+letter_list[5])
            elif(chunk.decode() == "Access granted"):
                chat_label.configure(text="")

                chat_box.insert(END, "\n"+chunk.decode('ascii'))
                chat_box.see('end')
            elif(chunk.decode() == "Access denied"):
                chat_label.configure(text="")

                chat_box.insert(END, "\n"+chunk.decode('ascii'))
                chat_box.see('end')
            elif("download (Y/N)?" in chunk.decode()):
                downloading_file = chunk.decode('ascii').split(" ")[0].strip()
                file_size = int(chunk.decode('ascii').split(" ")[5])

                chat_box.insert(END, "\n"+chunk.decode('ascii'))
                chat_box.see('end')
            elif("Download:" in chunk.decode()):
                get_file_name = chunk.decode('ascii').split(":")
                file_to_download = get_file_name[1].strip()
            else:
                chat_box.insert(END,"\n"+chunk.decode('ascii'))
        except:
            pass

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

    user_list.delete(0, "end")
    SERVER.send("show list".encode("ascii"))

def getFileSize(path, file_name):
    with open(file_name, 'rb') as f:
        chunk = f.read()
        return len(chunk)

def browseFiles():
    global chat_box
    global file_label
    global sending_file

    try:
        file_name = filedialog.askopenfilename()
        file_label.configure(text=file_name)

        host_name = '127.0.0.1'
        user_name = "User"
        password = "abcd12345"

        ftp_server = FTP(host_name, user_name, password)
        ftp_server.encoding = "utf-8"
        ftp_server.cwd('utils')

        f_name = ntpath.basename(file_name)

        with open(file_name, 'rb') as f:
            ftp_server.storbinary(f"stored {f_name}", f)
        
        ftp_server.dir()
        ftp_server.quit()

        message = "send "+f_name
        if message[:4] == "send":
            chat_box.insert(END, "\n Please wait")
            chat_box.see("end")

            sending_file = message[5:].strip()
            file_size = getFileSize("utils/"+sending_file)
            final_msg = message+" "+str(file_size)

            SERVER.send(final_msg.encode())
            chat_box.insert(END, "Processing file")
    except FileNotFoundError:
        print("Cancel button pressed")

def sendMessage():
    global SERVER
    global chat_entry
    global chat_box

    msg = chat_entry.get()

    SERVER.send(msg.encode('ascii'))
    chat_box.insert(END, "\n"+"You ->"+msg)
    chat_box.see('end')
    chat_entry.delete(0, 'end')

    if msg == 'Y':
        chat_box.insert(END, "\nFile is downloading")
        chat_box.see("end")

        host_name = '127.0.0.1'
        user_name = "User"
        password = "abcd12345"

        home = str(Path.home())
        download_path = home+"\Downloads"

        ftp_server = FTP(host_name, user_name, password)
        ftp_server.encoding = "utf-8"
        ftp_server.cwd('utils')

        f_name = file_to_download
        local_file_name = os.path.join(str(download_path, f_name))

        with open(local_file_name, 'wb') as f:
            ftp_server.retrbinary(f"stored {f_name}", f.write)
        
        ftp_server.dir()
        f.close()
        ftp_server.quit()
        chat_box.insert(END, "\nFile downloaded successfully at "+download_path)
        chat_box.see('end')

def openChatWindow():
    global user_list
    global chat_box
    global chat_entry
    global file_label
    global chat_label
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

    connect = Button(window, text='Connect', width=8, font=('Calibri', 10), command=connectWithClient)
    connect.place(x=260, y=170)

    disconnect = Button(window, text='Disconnect', width=9, font=('Calibri', 10), command=disconnectWithClient)
    disconnect.place(x=340, y=170)

    refresh = Button(window, text='Refresh', width=8, font=('Calibri', 10), command=showClientsList)
    refresh.place(x=425, y=170)

    chat_label = Label(window, text='Chat Window', font=('Calibri', 10))
    chat_label.place(x=9, y=200)

    chat_box = Text(window, height=6, width=68, font=('Calibri', 10))
    chat_box.place(x=10, y=225)

    attach_button = Button(window, text='Attach & Send', width=15, font=('Calibri', 10), command=browseFiles)
    attach_button.place(x=10, y=330)

    chat_entry = Entry(window, width=30, font=('Calibri', 13))
    chat_entry.place(x=130, y=330)

    send_button = Button(window, text='Send', width=10, font=('Calibri', 10), command=sendMessage)
    send_button.place(x=410, y=330)

    file_label = Label(window, text="", fg="blue", font=('Calibri', 10))
    file_label.place(x=10, y=350)

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
