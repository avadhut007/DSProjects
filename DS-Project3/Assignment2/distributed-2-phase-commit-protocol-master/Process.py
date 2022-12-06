import socket
import argparse
import time


class Process:
    HOST = '127.0.0.1'
    is_coordinator = False

    def __init__(self, id_, is_coordinator, port, value):
        self.id_ = id_
        self.label = f"P{id_}"
        self.is_coordinator = is_coordinator
        self.port = port
        self.value = value
        self.frozen = False
        self.failed = False

    def make_coordinator(self):
        self.is_coordinator = True

    def undo_coordinator(self):
        self.is_coordinator = False

    def change_value(self, newVal):
        self.value = newVal

    def processMessages(self, message):
        # priority
        if message == "unfreeze":
            self.frozen = False
            return ""
        elif message == "freeze":
            self.frozen = True
            return ""
        elif(self.frozen):
            return ""

        if message == "unfail":
            self.failed = False
            return ""
        elif message == "fail":
            self.failed = True
            return ""

        if message == "here?":
            if(self.failed):
                return "CANCEL"
            return "ok"
        # helps debug
        elif message == 'list':
            if(self.is_coordinator == "True"):
                return f"{self.label}: {self.value} (coordinator)"
            else:
                return f"{self.label}: {self.value}"
        elif message.startswith("value"):
            newVal = message.split(" ")[1]
            self.change_value(newVal)
            return f"{self.label} changed value to {newVal}"
        elif message == "id":
            return str(self.id_)
        elif message == "kill":
            exit()
            return ""
        return ""

    def join(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
            _socket.bind((Process.HOST, self.port))
            _socket.listen()
            print(f'Node {self.id_} has been created on PORT {self.port}')
            while True:
                con, _ = _socket.accept()
                with con:
                    message = con.recv(2048).decode('utf-8').rstrip('\n')

                    if message == 'bye':
                        print(f'Node {self.id_}: I am going out..')
                        break
                    response = self.processMessages(message)

                    con.send(response.encode('utf-8'))


if __name__ == '__main__':
    print("Process file is running")
    parser = argparse.ArgumentParser(description="Create a new process")
    parser.add_argument('--id', type=int, help='Id of the node')
    parser.add_argument('--port', type=int, help='Port of the node')
    parser.add_argument('--isCoordinator', type=str, help='Is it coordinator?')
    parser.add_argument('--value', type=int, help='Commited value')
    args = parser.parse_args()
    node = Process(
        args.id, args.isCoordinator, args.port, args.value)
    node.join()
