import socket
import os
import pickle


packet_size = 1024
header = "!header!"

client_dir_path = './client-directory'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(),5432))

def get_input_from_user():
    option = 0
    while option not in range(1,8):

        print("""
        Select one of the functions:
        1. Download file from server
        2. Upload file to the server
        3. Delete file from the server 
        4. Rename file in the server
        5. Print List of files in the server
        6. Print List of files in the client
        7. Quit
        """)
        option = input("Enter number of selected function: ")
        try:
            option = int(option)
        except:
            option = 0
        if option not in range(1,8):
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
    if len(files) == 0:
        print("The Directory is Empty")
        return    
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
    if len(files) == 0:
        print("The Directory is Empty")
        return    
    while True:
        file_dw = input("To upload enter the file name: ")
        if file_dw in files:

            function_name = "upload_file"
            file_size = os.path.getsize(client_dir_path + '/' + file_dw)
            file_size = str(file_size)  
            data = function_name + header + file_dw + header + file_size
            client_socket.send(data.encode('utf-8'))
            ack_file_size = client_socket.recv(packet_size).decode('utf-8')

            with open(client_dir_path + '/' + file_dw, 'rb') as reader:
                while True:
                    data = reader.read(packet_size)

                    if not data:
                        break
                    
                    client_socket.send(data)
            print(f"{file_dw} uploaded successfully") 
            return          

        print("--- Invalid file name. Please enter again. ---")

def delete_file():
    files = list_of_files("server")
    if len(files) == 0:
        print("The Directory is Empty")
        return
    while True:
        file_dw = input("To delete enter the file name: ")
        if file_dw in files:
            function_name = "delete_file"
            data = function_name + header + file_dw
            client_socket.send(data.encode('utf-8'))
            print(f"{file_dw} deleted successfully") # take delete msg from server -
            return
        print("--- Invalid file name. Please enter again. ---")

def rename_file():
    files = list_of_files("server")
    if len(files) == 0:
        print("The Directory is Empty")
        return   
    while True:
        file_dw = input("To rename enter the orginal file name: ")
        if file_dw in files:
            file_new_name = input(f"for {file_dw}, enter the new file name: ")
            file_new_name = file_new_name.strip()
            function_name = "rename_file"
            data = function_name + header + file_dw + header + file_new_name
            client_socket.send(data.encode('utf-8'))
            print(f"{file_dw} to {file_new_name} renamed successfully")
            return
        print("--- Invalid file name. Please enter again. ---")
        


while True:
    option = 0
    while option != 7:
        option = get_input_from_user()
        if option == 1:
            download_file()

        elif option == 2:
            upload_file()

        elif option == 3:
            delete_file()

        elif option == 4:
            rename_file()
        elif option == 5:
            list_of_files("server")
        elif option == 6:
            list_of_files("client")
    if option == 7:
        print("--- Closed the connection. ---")
        client_socket.close()
        exit()

