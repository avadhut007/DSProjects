import socket
import sys
import os
import threading
import time
import pickle

class TokenRingEvent: 
    def __init__(self, pid):      
        self.pid = pid
        self.ownership = False


class TokenRingAlgorithm:
    def __init__(self, pid, port_num):        
        self.pid = pid
        self.starting_state = 0
        self.port_list = [5432,5431,5430]
        self.port_num = port_num
        self.token = TokenRingEvent(self.pid)
        self.lock = threading.Lock()
        self.communication_thread = None


    def start_process(self):
        
        if (self.pid == 0 and self.starting_state == 0):
            self.token.ownership = True
            with open('token_count.txt', "w") as f:
                f.write('0')
            self.starting_state = 1

        self.communication_thread = threading.Thread(target=self.create_communication)
        self.communication_thread.start()
        
        time.sleep(2)

        self.use_or_pass_token()

    def create_communication(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((socket.gethostname(),self.port_num))

        while True:
            data = server_socket.recvfrom(1024)[0]
            self.token = pickle.loads(data)
            print(f"From Process P{self.token.pid}, received the token ")
            
            self.token.ownership = True
            self.token.pid = self.pid
            self.use_or_pass_token()

        server_socket.close()

    def use_or_pass_token(self):

            if(self.token.ownership and self.token.pid == self.pid):
                choice = 0
                while True:
                    choice = int(input('To access the shared file, Please enter 1 for yes and 0 for no '))
                    if(choice ==1):
                        print('Lock acquired on the shared file')
                        self.lock.acquire()
                        with open('token_count.txt', "r") as f:
                            count = int(f.read())
                        count = int(count)+1
                        with open('token_count.txt', "w") as f:
                            f.write(str(count))
                        
                        with open('token_count.txt', "r") as f:
                            file_content = f.read()
                        print('Counter in the shared file is increased to ',file_content)
                        self.lock.release()
                        print('Lock released on the shared file')
                        print('---------------------------------------------------------')
                    else:
                        next_pid = (self.pid+1)%3                       
                        print(f'Passing the token to Process P{next_pid}')
                        send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        data = pickle.dumps(self.token)
                        send_event_socket.sendto(data, (socket.gethostname(), self.port_list[next_pid]))
                        send_event_socket.close()
                        break