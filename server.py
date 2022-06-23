from os import environ
import socket
import select

IP = environ.get("IP")
PORT = int(environ.get("PORT"))
HEADER_LENGTH = environ.get("HEADER")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

socket_list = [server_socket]
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Lida com as mensagens recebidas
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        context = {
            'header': message_header,
            'data': client_socket.recv(message_length)
        }
        return context
    except:
        # Mensagens vazias ou cliente abortou a conexão abruptamente
        return False