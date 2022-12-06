import random, socket, logging, time, pickle
from threading import Thread, Semaphore, Lock

logging.basicConfig(format='%(participant)s:%(levelname)s ===> %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

NUM_OF_PARTICIPANTS = 3

class coordinator_class(Thread):
    def __init__(self, port_num):
        Thread.__init__(self)
        self.start_sem = Semaphore(0)
        self.port_num = port_num
        self.participant_list = []
        self.votes = []
        self.acknowdgements = []
        self._log_extra = dict(participant='-- Coordinator --')

    def acknowdge(self):
        self.acknowdgements.append(True)

    def start_voting(self, participant):
        self.participant_list.append(participant)
        self.start_sem.release()

    def run(self):
        time.sleep(0.5)
        self.start_sem.acquire(NUM_OF_PARTICIPANTS)

        # Vote Phase:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((socket.gethostname(),self.port_num))

        for participant in self.participant_list:
            LOG.info('VOTE_REQUEST sent to {}'.format(participant.p_name), extra=self._log_extra)
            participant.commit_query()
            data = server_socket.recvfrom(1024)[0]
            event = pickle.loads(data)
            if event['vote']:
                self.votes.append(True)
            else:
                self.votes.append(False)
        server_socket.close()
        # Commit Phase:
        while len(self.votes) < NUM_OF_PARTICIPANTS:
            time.sleep(1)
            
        send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
        if all(self.votes):
            LOG.debug('vote list {}'.format(self.votes), extra=self._log_extra)
            LOG.info('multicasting GLOBAL_COMMIT', extra=self._log_extra)
            for participant in self.participant_list:
                data = pickle.dumps({'decision':True})
                
                send_event_socket.sendto(data, (socket.gethostname(), participant.port_num))
                participant.receive_decision()

        else:
            LOG.debug('vote list {}'.format(self.votes), extra=self._log_extra)
            LOG.info('multicasting GLOBAL_ABORT', extra=self._log_extra)
            for participant in self.participant_list:
                data = pickle.dumps({'decision':False})
                
                send_event_socket.sendto(data, (socket.gethostname(), participant.port_num))
                participant.receive_decision()  

        send_event_socket.close()

        if all(self.acknowdgements):
            LOG.info('EXIT', extra=self._log_extra)
        else:
            LOG.error('error receiving an acknowdgement', extra=self._log_extra)

        for participant in self.participant_list:
            participant.end()

class participant(Thread):
    def __init__(self, p_name, coordinator, port_num):
        Thread.__init__(self)
        self.p_name = p_name
        self.port_num = port_num
        self.coordinator = coordinator
        self.transaction = None
        self.sem = Semaphore(0)
        self.lock = Lock()
        self.record = 1000
        self._log_extra = dict(participant=p_name)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((socket.gethostname(),self.port_num))

    def commit_query(self):
        #Voting phase
        send_event_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if self.res:
            LOG.info('VOTE_COMMIT', extra=self._log_extra)
            
            data = pickle.dumps({'vote':True})
            send_event_socket.sendto(data, (socket.gethostname(), self.coordinator.port_num))

        else:
            LOG.info('VOTE_ABORT', extra=self._log_extra)
            
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

    def end(self):
        self.sem.release()

    def run(self):
        LOG.debug('Before Transaction content {}'.format(self.record), extra=self._log_extra)

        self.lock.acquire()

        self.res = random.random() < 0.8
        #LOG.debug('Result {}'.format(self.res), extra=self._log_extra)
        self.coordinator.start_voting(self)

        # waiting till the end of voting phase
        self.sem.acquire()

        if self.commit:
            self.transaction()
            LOG.info('Received GLOBAL_COMMIT', extra=self._log_extra)
        else:
            LOG.info('Received GLOBAL_ABORT', extra=self._log_extra)

        self.lock.release()

        self.coordinator.acknowdge()

        LOG.debug('After Transaction content {}'.format(self.record), extra=self._log_extra)


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

