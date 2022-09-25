import socket
import os
import pickle


# use header to keep stream open when sending file in multiple packets
header_size = 6
packet_size = 1024
server_dir_path = './server-directory'
header = "!header!"


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To resuse the address if we rerun server

server_socket.bind((socket.gethostname(),5432))
server_socket.listen(5)

client_socket, client_addr = server_socket.accept()
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







