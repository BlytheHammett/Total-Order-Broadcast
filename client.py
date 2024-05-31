import threading
import socket
import os
import time
import math

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

local_timestamp = 0
pid = os.getpid()
queue = []
n_processes = 0

# waits for messages to be received
def client_receive():
    global n_processes
    while True:
        message = client.recv(1024).decode('utf-8')
        #print(f'client recv msg: {message}')
        #print('end of message')
        split_message = message.split('\n')

        for msg in split_message:
            if msg:
                #print(f'one msg: {msg}')
                temp_message = msg.split(' ')
                if temp_message[0] == 'n':
                    n_processes = temp_message[1]
                    #print(f'# of processes: {n_processes}')
                else:
                    handle_receive(msg)

# middleware that handles the message and sends an ack if necessary
def handle_receive(message):
    global queue
    global local_timestamp
    split_message = message.split(' ')
    timestamp_part = split_message[-1]
    split_message.remove(timestamp_part)
    full_message = ""
    for word in split_message:
        full_message += f'{word} '
    full_message = full_message.strip()

    queue.append((timestamp_part, full_message))
    #print(queue)
    #print('\n')

    queue.sort()

    if split_message[0] != 'ack':
        local_timestamp = max(local_timestamp, math.floor(float(timestamp_part)))
        client_send(f'ack {full_message}')

    check_serve()

# determines if a message can be served by looking at the head of the queue and counting all acks
def check_serve():
    global queue
    global n_processes
    peek = queue[0]
    #print(peek[1])
    peek_message = peek[1].split(' ')
    #print(f'peek message: {peek_message}')
    #print(f'there are {n_processes} processes')

    if peek_message[0] != 'ack':
        #print('checking if this message can be served')

        ack_count = 0
        tuples = []
        for tuple in queue:
            msg = tuple[1].split(' ')
            if msg[0] == 'ack':
                full_msg = ''
                for word in msg:
                    if word != 'ack':
                        full_msg += f'{word} '
                full_msg = full_msg.strip()
                #print(f'ack message: {full_msg}')
                if full_msg == peek[1]:
                    #print('received an ack')
                    ack_count += 1
                    tuples.append(tuple)
        
        if ack_count == int(n_processes) and n_processes != 0:
            #print('ready to deliver a message')
            #print(f'ack count: {ack_count} n processes: {n_processes}')
            
            print(f'[DELIVERING] {queue[0]}')

            for tuple in tuples:
                queue.remove(tuple)

            del queue[0]

            #print(f'new queue: {queue}')


# function for sending a message which will be broadcasted to all processes including itself
def client_send(message):
    global local_timestamp
    local_timestamp += 1
    message += f' {local_timestamp}.{pid}\n'
    client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target = client_receive)
receive_thread.start()

'''
time.sleep(5)
client_send('greetings')
client_send('how are you doing?')
'''

'''
client_send('hello')
time.sleep(3)
client_send('goodbye')
'''