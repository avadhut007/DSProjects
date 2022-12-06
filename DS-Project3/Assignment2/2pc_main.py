import random, logging, time
from threading import Thread, Semaphore, Lock


_format = '%(participant)s:%(levelname)s --> %(message)s'
logging.basicConfig(format=_format)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

# Task 2: Need to add timeout -- 

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
            LOG.info('commiting_to {}'.format(participant.p_name), extra=self._log_extra)
            participant.commit_query()

        # Commit Phase:
        while len(self.votes) < NUM_OF_PARTICIPANTS:
            time.sleep(1)
            
        if all(self.votes):
            LOG.debug('vote list {}'.format(self.votes), extra=self._log_extra)
            LOG.info('Committing', extra=self._log_extra)
            for participant in self.participant_list:
                participant.commit()
        else:
            # Abort Phase
            LOG.debug('vote list {}'.format(self.votes), extra=self._log_extra)
            LOG.warning('Rolling back', extra=self._log_extra)
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
        self.do = None
        self.undo = None
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
        LOG.debug('Before Transaction STATE {}'.format(self.record), extra=self._log_extra)

        #run and save
        self.lock.acquire()

        for do in self.do:
            do()

        self.res = random.random() < 0.8
        #LOG.debug('Result {}'.format(self.res), extra=self._log_extra)
        self.coordinator.start_voting(self)

        LOG.debug('DURING STATE {}'.format(self.record), extra=self._log_extra)

        # waiting till the end of voting phase
        self.sem.acquire()

        if self.commit:
            # Each participant commits
            LOG.info('GLOBAL_COMMIT', extra=self._log_extra)
        else:
            # Each participant aborts
            for undo in self.undo:
                undo()
            LOG.info('GLOBAL_ABORT', extra=self._log_extra)
        #releases all the acquired locks and resources
        self.lock.release()

        #participant returns an acknowledgment to the coordinator
        self.coordinator.acknowdge()

        LOG.debug('After Transaction STATE {}'.format(self.record), extra=self._log_extra)


if __name__ == '__main__':
    coordinator = coordinator_class()
    p1 = participant('participant1', coordinator)
    p2 = participant('participant2', coordinator)
    p3 = participant('participant3', coordinator)
    count = random.randint(1, 100)
 
    def p1_do():
        p1.record -= count

    def p1_undo():
        p1.record += count

    def p2_do():
        p2.record -= count

    def p2_undo():
        p2.record += count
        
    def p3_do():
        p3.record -= count

    def p3_undo():
        p3.record += count

    p1.do = [p1_do, ]
    p2.do = [p2_do, ]
    p3.do = [p3_do, ]
    p1.undo = [p1_undo, ]
    p2.undo = [p2_undo, ]
    p3.undo = [p3_undo, ]

    coordinator.start()
    p1.start()
    p2.start()
    p3.start()

    coordinator.join()
    p1.join()
    p2.join()
    p3.join()

