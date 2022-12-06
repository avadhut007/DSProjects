import random, socket, logging, time
from threading import Thread, Semaphore, Lock

_format = '%(participant)s:%(levelname)s ===> %(message)s'
logging.basicConfig(format=_format)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

# Task 2: Need to add timeout -- 
# Task 3: Need to add Socket

NUM_OF_PARTICIPANTS = 3

class coordinator_class(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start_sem = Semaphore(0)
        self.participant_list = []
        self.votes = []
        self.acknowdgements = []
        self._log_extra = dict(participant='coordinator')

    def commit(self):
        self.votes.append(True)

    def abort(self):
        self.votes.append(False)

    def acknowdge(self):
        self.acknowdgements.append(True)

    def start_voting(self, participant):
        self.participant_list.append(participant)
        self.start_sem.release()

    def run(self):
        time.sleep(0.5)
        self.start_sem.acquire(NUM_OF_PARTICIPANTS)

        # Vote Phase:
        for participant in self.participant_list:
            LOG.info('VOTE_REQUEST sent to {}'.format(participant.p_name), extra=self._log_extra)
            participant.commit_query()

        # Commit Phase:
        while len(self.votes) < NUM_OF_PARTICIPANTS:
            time.sleep(1)
            
        if all(self.votes):
            LOG.debug('vote list {}'.format(self.votes), extra=self._log_extra)
            LOG.info('multicasting GLOBAL_COMMIT', extra=self._log_extra)
            for participant in self.participant_list:
                participant.commit()
        else:
            # Abort Phase
            LOG.debug('vote list {}'.format(self.votes), extra=self._log_extra)
            LOG.info('multicasting GLOBAL_ABORT', extra=self._log_extra)
            for participant in self.participant_list:
                participant.abort_ack()

        if all(self.acknowdgements):
            LOG.info('END', extra=self._log_extra)
        else:
            LOG.error('error receiving an acknowdgement', extra=self._log_extra)

        for participant in self.participant_list:
            participant.end()

class participant(Thread):
    def __init__(self, p_name, coordinator):
        Thread.__init__(self)
        self.p_name = p_name
        self.coordinator = coordinator
        self.transaction = None
        self.sem = Semaphore(0)
        self.lock = Lock()
        self.record = 1000
        self._log_extra = dict(participant=p_name)

    def commit_query(self):
        # Vote phase:
        # If all three participants commits, then transaction is commited
        # If anyone of them aborts, transaction is aborted
        if self.res:
            LOG.info('VOTE_COMMIT', extra=self._log_extra)
            self.coordinator.commit()
        else:
            LOG.info('VOTE_ABORT', extra=self._log_extra)
            self.coordinator.abort()

    def commit(self):
        self.commit = True

    def abort_ack(self):
        self.commit = False

    def end(self):
        self.sem.release()

    def run(self):
        LOG.debug('Before Transaction content {}'.format(self.record), extra=self._log_extra)

        #run and save
        self.lock.acquire()



        self.res = random.random() < 0.8
        #LOG.debug('Result {}'.format(self.res), extra=self._log_extra)
        self.coordinator.start_voting(self)

        #LOG.debug('During Transaction content {}'.format(self.record), extra=self._log_extra)

        # waiting till the end of voting phase
        self.sem.acquire()

        if self.commit:
            # Each participant commits
            self.transaction()
            LOG.info('Received GLOBAL_COMMIT', extra=self._log_extra)
        else:
            # Each participant aborts
            LOG.info('Received GLOBAL_ABORT', extra=self._log_extra)
        #releases all the acquired locks and resources
        self.lock.release()

        #participant returns an acknowledgment to the coordinator
        self.coordinator.acknowdge()

        LOG.debug('After Transaction content {}'.format(self.record), extra=self._log_extra)


if __name__ == '__main__':
    coordinator = coordinator_class()
    p1 = participant('participant1', coordinator)
    p2 = participant('participant2', coordinator)
    p3 = participant('participant3', coordinator)
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

