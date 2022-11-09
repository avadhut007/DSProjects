
import threading
import socket
from heapq import heappop, heappush
from collections import defaultdict
import time
import pickle

class Event:
    def __init__(self,logical_clock=0, pid=0, eid = '') -> None:
        self.logical_clock = logical_clock
        self.pid = pid
        self.eid = eid
        self.type_is_ack = False
    
    def __lt__(self, other):
        if self.logical_clock == other.logical_clock:
            return self.pid < other.pid
        
        return self.logical_clock < other.logical_clock
 
class TotalOrderMultiCast:
    
    def __init__(self,pid=0, port_num=5432, event_id ='', event_id2= '') -> None:
        self.TOTAL_PROCESSES = 3
        self.port_list = [5432,5431,5430]
        self.pid = pid
        self.port_num = port_num
        self.event_id = event_id
        self.event_id2 = event_id2
        self.logical_clock = 0
        self.event_queue = []
        self.acknowledge_receive = defaultdict(set)
        self.events_sent = 0
        self.is_my_event_exists_or_not_processed = False
        self.communication_thread = None
        self.delivery_thread = None

    def start_process(self):
        #print(f"This is Process: {self.pid}") 
        self.communication_thread = threading.Thread(target=self.create_communication)
        self.communication_thread.start()
                
        self.delivery_thread = threading.Thread(target=self.deliver_ack)
        self.delivery_thread.start()

        time.sleep(1)

        firstEvent = Event(self.logical_clock, self.pid, self.event_id)
        firstEvent.type_is_ack = False

        self.send_event(firstEvent)
        self.is_my_event_exists_or_not_processed = True

        time.sleep(1)

        secondEvent = Event(self.logical_clock, self.pid, self.event_id2)
        secondEvent.type_is_ack = False

        self.send_event(secondEvent)
        self.is_my_event_exists_or_not_processed = True


    def create_communication(self):
        #print("This is create communication") 
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((socket.gethostname(),self.port_num))


        while self.events_sent != 2*self.TOTAL_PROCESSES:
            data = server_socket.recvfrom(1024)[0]
            event = pickle.loads(data)
            if not event.type_is_ack:
                print(f"Timestamp of received msg {event.eid} is {event.logical_clock}")
                self.logical_clock = max(self.logical_clock, event.logical_clock) + 1
                heappush(self.event_queue,event)
            else:
                self.acknowledge_receive[event.eid].add(event.pid)
            
            if self.event_queue:
                #print("creation",self.acknowledge_receive,"send event",self.events_sent)
                event = self.event_queue[0]
                if event.eid in self.acknowledge_receive:
                    #print("creation",self.acknowledge_receive)
                    if len(self.acknowledge_receive[event.eid]) == self.TOTAL_PROCESSES:
                        print(f"Current Process PID P{self.pid}: Processed event P{event.pid}.{event.eid}")
                        self.events_sent+=1
                        if event.eid == self.event_id:
                            self.is_my_event_exists_or_not_processed = False 
                        heappop(self.event_queue)
                                
        server_socket.close()

    def send_event(self, event):
        #print("clock",self.logical_clock)
        self.logical_clock+=1            
        event.logical_clock = self.logical_clock
        for port in self.port_list:
            send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data = pickle.dumps(event)
            send_event_socket.sendto(data, (socket.gethostname(), port))
            send_event_socket.close()

    def deliver_ack(self):
        #print("This is deliver ack") 
        while self.events_sent != 2*self.TOTAL_PROCESSES:
            try:
                if self.event_queue:
                    #print("del",self.acknowledge_receive,"send event",self.events_sent)
                    event = self.event_queue[0]
                    if self.check_ack_constraints(event):
                        AckTypeEvent = Event(self.logical_clock, self.pid, event.eid)
                        AckTypeEvent.type_is_ack = True
                        for port in self.port_list:
                            #Pi’s update has been processed condition and Pi has not made an update request condition
                            if event.eid != self.event_id:
                                if self.is_my_event_exists_or_not_processed:
                                    if self.logical_clock < event.logical_clock:
                                        continue
                                    elif self.logical_clock == event.logical_clock:
                                            if self.pid < event.pid:
                                                continue                                       
                            self.send_ack(AckTypeEvent,port)
                        self.acknowledge_receive[event.eid].add(event.pid)
            except:
                pass

    def check_ack_constraints(self, event):

        if event.pid == self.pid:
            return True

        #Pi’s identifier is greater than Pj’s identifier
        if self.logical_clock > event.logical_clock:
            return True

        if self.logical_clock == event.logical_clock:
            if self.pid > event.pid:
                return True

        return False

    def send_ack(self, event, port):
        send_ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = pickle.dumps(event)
        send_ack_socket.sendto(data, (socket.gethostname(), port))
        send_ack_socket.close()