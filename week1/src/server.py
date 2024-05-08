import socket
import threading
import argparse

buffer_size = 20480

def check_numb_clients(client_socket, client_address, seqno):
    if len(clients) < args.max_clients:
        if client_address not in clients:
            clients[len(clients)] = client_address
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        return client_handler
    else:
        client_socket.sendto(f"n|{seqno}".encode('utf-8'), client_address)
        return None

def handle_client(client_socket, client_address):
    file = None
    filename = None
    expected_seqno = 0
    chunk = 0
    while True:
        message = client_socket.recv(buffer_size).decode('utf-8')
        msg_type, seqno, data = message.split('|', 2)
        seqno = int(seqno)
        if msg_type == 's':
            filename, filesize = data.split('|')
            filesize = int(filesize)
            file = open(filename, 'wb')
            client_socket.sendto(f"a|{expected_seqno}".encode('utf-8'), client_address)
            expected_seqno = (seqno + 1) % 2
        elif msg_type == 'd':
            if seqno == expected_seqno:
                file.write(data.encode('utf-8'))
                chunk += 1
                client_socket.sendto(f"a|{expected_seqno}".encode('utf-8'), client_address)
                expected_seqno = (seqno + 1) % 2
                if chunk == filesize:
                    file.close()
                    print(f"File {filename} received from {client_address}")
                    del clients[client_address]
                    break
        else:
            print("Message type is not correct")
            break

parser = argparse.ArgumentParser(description='UDP Server')
parser.add_argument('port', type=int, help='The port number to listen on')
parser.add_argument('max_clients', type=int, help='The maximum number of simultaneously connected clients')
args = parser.parse_args()

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('0.0.0.0', args.port))

print(f"[*] Listening on 0.0.0.0:{args.port}")

clients = {}

while True:
    data, client_address = server.recvfrom(buffer_size)
    client_handler = check_numb_clients(server, client_address, 0)
    if client_handler is not None:
        client_handler.start()