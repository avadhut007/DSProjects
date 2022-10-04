import socket
import pickle
import asyncio
import math 
import numpy as np


packet_size = 1024
#server_dir_path = './server-directory'
#header = "!header!"


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To resuse the address if we rerun server

server_socket.bind((socket.gethostname(),9999))
server_socket.listen(5)

def calculate_pi():

    return math.pi


def asyadd(a,b):
    return a+b

def sort(arr1):
    return sorted(arr1)

def matrix_multiply(matrixA,matrixB):

    res = np.dot(matrixA,matrixB).tolist()
    return res

while True:
    client_socket, client_addr = server_socket.accept()
    print(f'Server has connected with the client {client_addr}')

    while True:
        packet = client_socket.recv(packet_size)
        if len(packet)==0:
            continue
        packet = pickle.loads(packet)

        function_name = packet["function_name"]
        if function_name == 'calculate_pi':
            pi_value = calculate_pi()
            pi_value = pickle.dumps(pi_value)
            client_socket.send(pi_value)

        elif function_name == 'add':
            i = packet['first']
            j = packet['second']
            addition = asyadd(i,j)
            addition = pickle.dumps(addition)
            client_socket.send(addition)

        elif function_name == 'sort':
            arrayA = packet['arr']
            sorted_array = sort(arrayA)
            sorted_array = pickle.dumps(sorted_array)
            client_socket.send(sorted_array)
            
        elif function_name == 'matrix_multiply':
            matrixA = packet['first']
            matrixB = packet['second']
            Rc, Cc = packet['third'][0], packet['second'][1]
            matrixC = matrix_multiply(matrixA,matrixB)
            matrixC = pickle.dumps(matrixC) 
            client_socket.send(matrixC)

