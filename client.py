from http import client
import socket
import select
import errno
from os import environ
import sys

HEADER_LENGTH = environ.get("HEADER_LENGTH")
IP = environ.get("IP")
PORT = environ.get("PORT")

_username = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = _username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header + username)

while True:
    message = input(f"{_username} > ")

    if message:
        #Encode messagem em bytes, prepara o header, converte em bytes e envia
        message = message.encode("utf-8")
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(message_header + message)

    try:
        # Loop para receber messagens
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)

            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()
            
            username_length = int(username_header.decode("utf-8").strip())
            username = client_socket.recv(username_length).decode("utf-8")

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode("utf-8").strip())
            message = client_socket.recv(message_length).decode("utf-8")

            print(f"{username} > {message}")
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print(f"Reading error: {str(e)}")
            sys.exit()
        continue
    except Exception as e:
        print(f"Reading error: {str(e)}")
        sys.exit()