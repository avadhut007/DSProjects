import socket
import sys
import os
import threading
import time
import pickle

class TokenRingFrame: 
    def __init__(self, pid):
      
        self.pid = pid
        self.ownership = False


class TokenRingAlgorithm:

    def __init__(self, pid, port_num):
        
       # self.process_name = process_name
        self.pid = pid
        self.process_portList = []
        self.num_processes = 3
        self.initialStage = 0
        self.port_list = [5432,5431,5430]
        self.port_num = port_num
        self.token = TokenRingFrame(self.pid)
        self.lock = threading.Lock()
        self.connection_thread = None
        #self.server_host_addr = socket.gethostbyname()
        #self.file = open('token_count.txt')
       

       
    def manageConnections(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((socket.gethostname(),self.port_num))

        while True:
            data = server_socket.recvfrom(1024)[0]
            self.token = pickle.loads(data)
            print(f"Received the token from process P{self.token.pid}")
            
            self.token.ownership = True
            self.token.pid = self.pid
            self.handleTokenRing()

        server_socket.close()

    def initialize(self):
        print(f"Process :P{self.pid} ")
        if (self.pid == 0 and self.initialStage == 0):
            self.token.ownership = True
            with open('token_count.txt', "w") as f:
                f.write('0')
            self.initialStage = 1

        self.connection_thread = threading.Thread(target=self.manageConnections)
        self.connection_thread.start()
        
        try:
            time.sleep(2)
        except:
            print('exception. Rerun the program')

        self.handleTokenRing()

    def handleTokenRing(self):

            if(self.token.ownership and self.token.pid == self.pid):
                option = 0
                while True:
                    option = int(input('To access the shared file, Please enter 1 for yes and 0 for no '))
                    if(option ==1):
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
                        print(f'Passing token to process P{next_pid}')
                        send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        data = pickle.dumps(self.token)
                        send_event_socket.sendto(data, (socket.gethostname(), self.port_list[next_pid]))
                        send_event_socket.close()
                        break