from curses.ascii import isdigit
import socket
import os
import pickle


header_size = 6
packet_size = 1024
header = "!header!"

client_dir_path = './client-directory'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(),5432))

def get_input_from_user():
    option = 0
    while option not in range(1,6):

        print("""
        Select one of the functions:
        1. Download file from server
        2. Upload file to the server
        3. Rename file in the server
        4. Delete file from the server
        5. Quit
        """)
        option = input("Enter number of selected function: ")
        try:
            option = int(option)
        except:
            option = 0
        if option not in range(1,6):
            print("\n--- Invalid option provided. Please select again. ---")
        return option

def list_of_files(location):
    if location == "server":
        function_name = "list_of_files"
        data = function_name + header
        client_socket.send(data.encode('utf-8'))
        files = client_socket.recv(packet_size)
        files = pickle.loads(files)
    else:
        files =  os.listdir(client_dir_path)
    print(f"\nList of files in {location} directory: ")
    for file in files:
        print(" ",file)
    return files
    # if files do  not exist print empty directory

def download_file():
    files = list_of_files("server")
    while True:
        file_dw = input("To download enter the file name: ")
        if file_dw in files:
            #print(file_dw)

            function_name = "download_file"
            data = function_name + header + file_dw
            client_socket.send(data.encode('utf-8'))
            
            file_size = client_socket.recv(packet_size).decode('utf-8')
            file_size = int(file_size)

            client_socket.send("File size received".encode('utf-8'))
            
            data = ''
            with open(client_dir_path + '/'+ file_dw, 'wb') as writer:
                curr_size = 0
                while curr_size < file_size:                    
                    data = client_socket.recv(packet_size)
                    if not data:
                        break
                    writer.write(data)
                    curr_size = curr_size + len(data)
                    
                    
            print(f"{file_dw} downloaded successfully")  
            return

        print("--- Invalid file name. Please enter again. ---")
        
    

def upload_file():
    files = list_of_files("client")


def rename_file():
    pass
def delete_file():
    pass

while True:
    option = 0
    while option != 5:
        option = get_input_from_user()
        if option == 1:
            download_file()

        elif option == 2:
            upload_file()

        elif option == 3:
            rename_file()

        elif option == 4:
            delete_file()

    if option == 5:
        print("--- Closed the connection. ---")
        client_socket.close()
        exit()

