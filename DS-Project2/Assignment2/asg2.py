
import threading
import socket
import time
import pickle

class Event:
    def __init__(self,vector_clock=[0,0,0], pid=0, eid = '') -> None:
        self.vector_clock = vector_clock
        self.pid = pid
        self.eid = eid

    def __lt__(self, other):
        flag = []
        for i in range(len(self.vector_clock)):
            if self.vector_clock[i] != other.vector_clock[i]:
                flag.append(self.vector_clock[i] < other.vector_clock[i])
            else:
                flag.append(True)
        return all(flag)

 
class VectorAlgorithm:
    
    def __init__(self,pid=0, port_num=5432, event_id ='') -> None:
        self.TOTAL_PROCESSES = 3
        self.port_list = [5432,5431,5430]
        self.pid = pid
        self.port_num = port_num
        self.event_id = event_id
        self.vector_clock = [0,0,0]
        self.event_queue = []
        self.events_delivered = 0
        self.communication_thread = None

    def start_process(self):

        self.communication_thread = threading.Thread(target=self.create_communication)
        self.communication_thread.start()

        print(f"At start of process: vector clock: {self.vector_clock}")
        print()

        time.sleep(4)
        event1 = Event(self.vector_clock, self.pid, self.event_id)
        self.send_event(event1)

        time.sleep(2)

        event2 = Event(self.vector_clock, self.pid, self.event_id+self.event_id[-1])
        self.send_event(event2)

    def create_communication(self):
        #print("This is create communication") 
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((socket.gethostname(),self.port_num))


        while True:
            data = server_socket.recvfrom(1024)[0]
            event = pickle.loads(data)

            lock = threading.Lock()
            lock.acquire()

            self.event_queue.append(event)           
            self.event_queue = sorted(self.event_queue)
            i = 0
            while i < len(self.event_queue):
                is_delivered = False
                event = self.event_queue[i]
                # ts(m)[event's pid] = VCj [event's pid ] +1
                if event.vector_clock[event.pid] != (self.vector_clock[event.pid]+1):
                    i = 0
                    continue
                for j in range(len(event.vector_clock)):
                    #ts(m)[k] <= VCj [k] for any k !=(event's pid)    
                    if (j != event.pid) and event.vector_clock[j] > self.vector_clock[j]:
                        print(f"From P{event.pid} received message's Vector Clock: {event.vector_clock} Local Vector Clock: {self.vector_clock}. This message needs delayed delivery")
                        print() 
                        break
                
                    if j == len(event.vector_clock)-1:
                        temp = self.vector_clock[:]
                        # need to take max of all k's
                        self.vector_clock =  [max(k1, k2) for k1, k2 in zip(self.vector_clock, event.vector_clock)]
                        is_delivered = True
                        print(f"From P{event.pid} received message's Vector Clock: {event.vector_clock} Local Vector Clock: {temp}")
                        print(f"After message is delivered to the current process, Local Vector Clock: {self.vector_clock}")
                        self.events_delivered+=1
                        print(f"---------- Total {self.events_delivered} messages delivered to the current Process P{self.pid} ----------")
                        print()
                        if is_delivered:
                            self.event_queue.pop(i)
                            i = -1

                i+=1
            lock.release()

        server_socket.close()

    def send_event(self, event):
        #print("clock",self.vector_clock)

        self.vector_clock[self.pid] +=1
        event.vector_clock = self.vector_clock[:]
        print(f"After message is sent, Local Vector Clock:{self.vector_clock}")
        print()
        for port in self.port_list:
            if port != self.port_num:                
                send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data = pickle.dumps(event)
                # delay event e00 or e11 for a particular process p2 to check if causal order is working
                if event.eid in ['E00','E11'] and event.vector_clock in [[1,2,2],[1,2,1], [2,1,2], [2,1,1]] and port == 5430:
                    time.sleep(2)
                send_event_socket.sendto(data, (socket.gethostname(), port))
                send_event_socket.close()
        
