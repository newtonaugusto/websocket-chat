from os import environ
import socket
import select

IP = environ.get("IP")
PORT = int(environ.get("PORT"))
HEADER_LENGTH = int(environ.get("HEADER_LENGTH"))

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
    except BaseException:
        # Mensagens vazias ou cliente abortou a conexão abruptamente
        return False


def send_message(client_socket):
    pass


while True:
    read_sockets, _, excetion_sockets = select.select(
        socket_list, [], socket_list)

    for notified_socket in read_sockets:
        # if notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            data = receive_message(client_socket)
            if data is False:
                continue

            socket_list.append(client_socket)
            clients[client_socket] = data

            print(f"Accepted new connection from \
                  {client_address}:{data['data'].decode('utf-8')}")
        # Else existing socket is sending a message
        else:
            message = receive_message(notified_socket)

            if message is False:
                print(f"Closed connection from  \
                      {clients[notified_socket]['data'].decode('utf-8')}")
                socket_list.remove(notified_socket)

                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8").split(",")[0]}: {message["data"].decode("utf-8")}')
            receiver = user["data"].decode("utf-8").split(",")[0]
            for client_socket in clients:
                print(client_socket)
                # print(receiver+','+client_socket.getpeername()[1])
                # print("1: ",receiver)
                client_socket.send("teste".encode("utf-8"))
                if client_socket != notified_socket:
                    # Send user and message (both with their headers)
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # handle some socket exceptions
    for notified_socket in excetion_sockets:
        # Remove from list for socket.socket()
        socket_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
