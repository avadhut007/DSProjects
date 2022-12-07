import socket, logging, random, time, pickle, sys
from threading import Semaphore, Thread, Lock

logfile = 'logs.txt'
logging.basicConfig(level=logging.DEBUG , 
                    format='%(participant)s:%(levelname)s ===> %(message)s',
                    handlers=[logging.FileHandler('logs.txt'),logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

NUM_OF_PARTICIPANTS = 3

class coordinator_class(Thread):
    def __init__(self, port_num):
        Thread.__init__(self)
        self.cod_sem = Semaphore(0)
        self.port_num = port_num
        self.acknowdgements = []
        self.participant_list = []
        self.votes_list = []
        self.extra_logs = dict(participant='-- Coordinator --')

    def join_participant(self, participant):
        self.participant_list.append(participant)
        self.cod_sem.release()

    def acknowdge(self):
        self.acknowdgements.append(True)

    def run(self):
        time.sleep(0.5)
        self.cod_sem.acquire(NUM_OF_PARTICIPANTS)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((socket.gethostname(),self.port_num))

        for participant in self.participant_list:
            log.info('VOTE_REQUEST sent to {}'.format(participant.p_name), extra=self.extra_logs)
            participant.send_p_vote()
            data = server_socket.recvfrom(1024)[0]
            event = pickle.loads(data)
            if event['vote']:
                self.votes_list.append(True)
            else:
                self.votes_list.append(False)
        server_socket.close()
        
        while len(self.votes_list) < NUM_OF_PARTICIPANTS:
            time.sleep(1)
            
        send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
        if all(self.votes_list):
            log.debug('vote list {}'.format(self.votes_list), extra=self.extra_logs)
            log.info('multicasting GLOBAL_COMMIT', extra=self.extra_logs)
            for participant in self.participant_list:
                data = pickle.dumps({'decision':True})
                
                send_event_socket.sendto(data, (socket.gethostname(), participant.port_num))
                participant.receive_decision()

        else:
            log.debug('vote list {}'.format(self.votes_list), extra=self.extra_logs)
            log.info('multicasting GLOBAL_ABORT', extra=self.extra_logs)
            for participant in self.participant_list:
                data = pickle.dumps({'decision':False})
                
                send_event_socket.sendto(data, (socket.gethostname(), participant.port_num))
                participant.receive_decision()  

        send_event_socket.close()

        if all(self.acknowdgements):
            log.info('EXIT', extra=self.extra_logs)
        else:
            log.error('acknowdgement not received', extra=self.extra_logs)

        for participant in self.participant_list:
            participant.sem_release()

class participant(Thread):
    def __init__(self, p_name, coordinator, port_num):
        Thread.__init__(self)
        self.p_name = p_name
        self.port_num = port_num
        self.coordinator = coordinator
        self.transaction = None
        self.part_sem = Semaphore(0)
        self.lock = Lock()
        self.record = 1000
        self.extra_logs = dict(participant=p_name)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((socket.gethostname(),self.port_num))

    def send_p_vote(self):
        # vote request
        send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if self.my_vote:
            log.info('VOTE_COMMIT', extra=self.extra_logs)
            
            data = pickle.dumps({'vote':True})
            send_event_socket.sendto(data, (socket.gethostname(), self.coordinator.port_num))

        else:
            log.info('VOTE_ABORT', extra=self.extra_logs)
            
            data = pickle.dumps({'vote':False})
            send_event_socket.sendto(data, (socket.gethostname(), self.coordinator.port_num))

        send_event_socket.close()

    def receive_decision(self):
        data = self.server_socket.recvfrom(1024)[0]
        event = pickle.loads(data)
        if event['decision']:
            self.commit = True
        else:
            self.commit = False
        self.server_socket.close()

    def sem_release(self):
        self.part_sem.release()

    def run(self):
        log.debug('INIT - Before Transaction content {}'.format(self.record), extra=self.extra_logs)

        self.lock.acquire()

        self.my_vote = random.random() < 0.8
        #log.debug('Result {}'.format(self.my_vote), extra=self.extra_logs)
        self.coordinator.join_participant(self)

        # waiting untill voting phase is complete
        self.part_sem.acquire()

        if self.commit:
            self.transaction()
            log.info('Received GLOBAL_COMMIT', extra=self.extra_logs)
        else:
            log.info('Received GLOBAL_ABORT', extra=self.extra_logs)

        self.lock.release()

        self.coordinator.acknowdge()

        log.debug('After Transaction content {}'.format(self.record), extra=self.extra_logs)


if __name__ == '__main__':

    coordinator = coordinator_class(5430)
    
    p1 = participant('Participant 1', coordinator, 5431)
    p2 = participant('Participant 2', coordinator, 5432)
    p3 = participant('Participant 3', coordinator, 5433)
    
    update = random.randint(1, 100)
 
    def p1_run_transaction():
        p1.record -= update

    def p2_run_transaction():
        p2.record -= update
  
    def p3_run_transaction():
        p3.record -= update

    p1.transaction = p1_run_transaction
    p2.transaction = p2_run_transaction
    p3.transaction = p3_run_transaction

    coordinator.start()
    p1.start()
    p2.start()
    p3.start()

    coordinator.join()
    p1.join()
    p2.join()
    p3.join()

log.info('---------- END OF TRANSACTION ----------', extra=coordinator.extra_logs)