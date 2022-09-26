import socket
import os
import pickle
import threading
from datetime import datetime

packet_size = 1024
server_dir_path = './server-directory'
header = "!header!"


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To resuse the address if we rerun server

server_socket.bind((socket.gethostname(),5432))
server_socket.listen(5)

def run_client(client_socket, client_addr):
    print(f'Server has connected with the client {client_addr}')
    while True:        

        packet = client_socket.recv(packet_size).decode('utf-8')
        packet = packet.split(header)
        function_name = packet[0]
        if function_name == 'list_of_files':
            files = os.listdir(server_dir_path)
            files = pickle.dumps(files)
            client_socket.send(files)

        elif function_name == 'download_file':
            file_dw = packet[1]
            file_size = os.path.getsize(server_dir_path + '/' + file_dw)
            file_size = str(file_size)

            client_socket.send(file_size.encode('utf-8'))
            ack_file_size = client_socket.recv(packet_size).decode('utf-8')

            with open(server_dir_path + '/' + file_dw, 'rb') as reader:
                while True:
                    data = reader.read(packet_size)

                    if not data:
                        break
                    
                    client_socket.send(data)
            print(f"{file_dw} downloaded successfully {datetime.now().time()}")

        elif function_name == 'upload_file':
            file_dw = packet[1]
            file_size = packet[2]
            file_size = int(file_size)
            
            client_socket.send("File size received".encode('utf-8'))

            data = ''
            with open(server_dir_path + '/'+ file_dw, 'wb') as writer:
                curr_size = 0
                while curr_size < file_size:
                                 
                    data = client_socket.recv(packet_size)
                    if not data:
                        break
                    writer.write(data)
                    curr_size = curr_size + len(data)
            print(f"{file_dw} uploaded successfully {datetime.now().time()}")

        elif function_name == 'delete_file':
            file_dw = packet[1]
            os.remove(server_dir_path + '/' + file_dw)

        elif function_name == 'rename_file':
            file_dw = packet[1]
            file_new_name = packet[2]
            os.rename(server_dir_path + '/' + file_dw, server_dir_path + '/' + file_new_name)    


while True:
    client_socket, client_addr = server_socket.accept()

    t1 = threading.Thread(target=run_client, args=[client_socket, client_addr])
    t1.start()

    print(f"New thread started. Total client threads are {threading.active_count()-1}")
    
