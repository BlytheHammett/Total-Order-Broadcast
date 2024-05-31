import threading
import socket

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

clients = []

# broadcasts a message to all processes
def broadcast(message):
    for client in clients:
        #print(f'BROADCASTING: {message}')
        message += '\n'
        client.send(message.encode('utf-8'))

def handle_client(client):
    while True:
        message = client.recv(1024).decode('utf-8')
        split_message = message.split('\n')

        if (len(split_message) > 2):
            #print('sent more than one message')
            split_message.remove(split_message[-1])
            for msg in split_message:
                #print(msg)
                broadcast(msg)
                broadcast(f'n {len(clients)}')
        else:
            #print('sent one message')
            #print(split_message[0])
            broadcast(split_message[0])
            broadcast(f'n {len(clients)}')

def receive():
    while True:
        print('server is running and listening...')
        client, address = server.accept()
        print(f'connection is established with {str(address)}')
        clients.append(client)
        thread = threading.Thread(target = handle_client, args = (client,))
        thread.start()

receive()