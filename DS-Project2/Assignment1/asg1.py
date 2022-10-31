
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
    
    def __init__(self,pid=0, port_num=5432, event_id ='') -> None:
        self.TOTAL_PROCESSES = 3
        self.port_list = [5432,5431,5430]
        self.pid = pid
        self.port_num = port_num
        self.event_id = event_id
        self.logical_clock = 0
        self.event_queue = []
        self.acknowledge_receive = defaultdict(list)
        self.events_sent = 0

    def start_process(self):
        #print(f"This is Process: {self.pid}") 
        communication_thread = threading.Thread(target=self.create_communication)
        communication_thread.start()
        
        order_thread = threading.Thread(target=self.create_order)
        order_thread.start()

        delivery_thread = threading.Thread(target=self.deliver_ack)
        delivery_thread.start()

        time.sleep(4)

        firstEvent = Event(self.logical_clock, self.pid, self.event_id)
        firstEvent.type_is_ack = False

        self.send_event(firstEvent)

    def create_communication(self):
        #print("This is create communication") 
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((socket.gethostname(),self.port_num))

        while self.events_sent != self.TOTAL_PROCESSES:

            data = server_socket.recvfrom(1024)[0]
            event = pickle.loads(data)
            
            manage_event_thread = threading.Thread(target=self.manage_events, args=[event])
            manage_event_thread.start()
            
        
        server_socket.close()
        

    def manage_events(self, event):
        lock = threading.Lock()
        lock.acquire()
        if event.type_is_ack:
            self.acknowledge_receive[event.eid].append(event.pid)
        else:
            heappush(self.event_queue,event)
        lock.release()

    def create_order(self):
        #print("This is create order") 
        while self.events_sent != self.TOTAL_PROCESSES:
            if self.event_queue:
                #print("creation",self.event_queue)
                event = self.event_queue[0]
                if event.eid in self.acknowledge_receive:
                    if len(self.acknowledge_receive[event.eid]) == self.TOTAL_PROCESSES:
                        print(f"Current Process PID P{self.pid}: Processed event P{event.pid}.{event.eid}")
                        self.events_sent+=1
                        heappop(self.event_queue)

    def deliver_ack(self):
        #print("This is deliver ack") 
        while self.events_sent != self.TOTAL_PROCESSES:
            if self.event_queue:
                #print("del",self.event_queue)
                event = self.event_queue[0]
                if self.check_ack_constraints(event):
                    AckTypeEvent = Event(self.logical_clock, self.pid, event.eid)
                    AckTypeEvent.type_is_ack = True
                    self.send_event(AckTypeEvent)
                    self.acknowledge_receive[event.eid].append(event.pid)

    def check_ack_constraints(self, event):
        if self.acknowledge_receive and event.eid in self.acknowledge_receive:
            if self.pid in self.acknowledge_receive[event.eid]:
                return False
        if event.pid == self.pid:
            return True
        
        if self.event_id in self.acknowledge_receive and len(self.acknowledge_receive[self.event_id]) == self.TOTAL_PROCESSES:
            return True
        
        if self.logical_clock == event.logical_clock:
            if self.pid > event.pid:
                return True
        elif self.logical_clock > event.logical_clock:
            return True

        return False


    def send_event(self, event):
        print("clock",self.logical_clock)
        if not event.type_is_ack:
            self.logical_clock+=1
        
        event.logical_clock = self.logical_clock
        for port in self.port_list:
            send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data = pickle.dumps(event)
            send_event_socket.sendto(data, (socket.gethostname(), port))
            send_event_socket.close()
        