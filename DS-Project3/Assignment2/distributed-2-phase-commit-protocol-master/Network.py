from Process import Process
from helper import create, send_message
from random import randint
from random import choice
import threading
import socket
import time


class Network:
    current_port = randint(10000, 60000)
    node_list = []
    coordinator = None
    consistency_history = []
    queue_list = []

    def __init__(self, nodes, history):
        self.consistency_history = history
        for node in nodes:
            self.handleCreation(node[0], node[1], history[-1])
            self.current_port += 1

    def handleCreation(self, id_, is_coordinator, lastValue):
        # add each node to the network with Node class
        node_id = int(id_.replace("P", ""))
        # Create Node obj to store in the node_list
        node_obj = Process(node_id, is_coordinator,
                           self.current_port, self.consistency_history[-1])
        create(node_obj.id_, node_obj.is_coordinator,
               node_obj.port, node_obj.value)

        reply = send_message("here?", node_obj.port)
        #print(reply,"=reply in Network file")
        if reply == "ok":
            self.node_list.append(node_obj)
            if node_obj.is_coordinator:
                self.coordinator = node_obj

            print(
                f"Node {node_obj.label} has been created on PORT {self.current_port}")

    def timeFailure(self, node, seconds):
        if(node in self.queue_list):
            print("Process already frozen or failed")
            return
        self.queue_list.append(node)
        send_message("freeze", node.port)
        time.sleep(seconds)
        send_message("unfreeze", node.port)
        print(f"P{node.id_} is unfrozen")
        self.queue_list.remove(node)

    def arbFailure(self, node, seconds):
        if(node in self.queue_list):
            print("Process already frozen or failed")
            return
        self.queue_list.append(node)
        send_message("fail", node.port)
        time.sleep(seconds)
        send_message("unfail", node.port)
        print(f"P{node.id_} is no longer failing at life")
        self.queue_list.remove(node)

    # not checking if coordinator is active

    def checkOnProcesses(self):
        if(self.coordinator == None or send_message("here?", self.coordinator.port) != "ok"):
            print("No coordinator, no progress")
            return False
        ok = True
        for node in self.node_list:
            if(node != self.coordinator):
                if(send_message("here?", node.port) != "ok"):
                    ok = False
                    break
        return ok

    def findProcess(self, label):
        for node in self.node_list:
            if node.label == label:
                return node
        return None

    def process_command(self, command):
        message = ""
        if(command == 'list'):
            for node in self.node_list:
                message += send_message("list", node.port) + "\n"
        elif(command == 'history' or command == 'hist'):
            message = self.consistency_history
        # this is problematic, the coordinator isn't doing anything, he is treated just like other nodes
        # if you remove the -, you need to change the split function in Process
        elif(command.startswith('set-value') or command.startswith("st")):
            value = int(command.split(" ")[1])
            if(self.checkOnProcesses()):
                for node in self.node_list:
                    message += send_message(f"value {value}", node.port) + "\n"
                self.consistency_history.append(value)
            else:
                message = "Aborted, not all nodes are active"

        elif(command.startswith("rollback")):
            N = int(command.split(" ")[1])
            if(N >= len(self.consistency_history)):
                message = "Aborted, N value too big"
            elif(N <= 0):
                message = "Aborted, N value must be bigger than 0"
            elif(self.checkOnProcesses()):
                self.consistency_history = self.consistency_history[:N]
                newValue = self.consistency_history[-1]
                for node in self.node_list:
                    message += send_message(f"value {newValue}",
                                            node.port) + "\n"
            else:
                message = "Aborted, not all nodes are active"

        elif(command.startswith("add")):
            nd = command.split(" ")[1]
            check = True
            for node in self.node_list:
                if(send_message("id", node.port) == str(nd[1])):
                    message = "Aborted, such a Process already exists"
                    check = False
                    break
            if(check):
                self.handleCreation(nd, False, self.current_port)
                message = f"{nd} added"
        elif command.startswith('remove') or command.startswith("rm"):  # Solved?
            try:
                id_ = int(command.split(' ')[1][1])
            except:
                print("Please specify the process id")
                return
            print(id_)
            for node in self.node_list:
                if node.id_ == id_:
                    send_message("kill", node.port)
                    print(f"Process {node.id_} is going to leave")
                    self.node_list.remove(node)
                    # should check algorithm later
                    if node.is_coordinator:
                        self.coordinator = None
                    break
        elif command.startswith("Time-failure") or command.startswith("tf"):
            # smug
            process_, secs = command.split(" ")[1], int(command.split(" ")[2])
            node = self.findProcess(process_)
            if(node != None):
                t = threading.Thread(
                    target=self.timeFailure, args=(node, secs,))
                t.start()
                message = f"P{node.id_} is frozen for {secs} seconds"
            else:
                message = "No such process"

        elif command.startswith("Arbitrary-failure") or command.startswith("af"):
            # smug
            process_, secs = command.split(" ")[1], int(command.split(" ")[2])
            node = self.findProcess(process_)
            if(node != None):
                t = threading.Thread(
                    target=self.arbFailure, args=(node, secs,))
                t.start()
                message = f"P{node.id_} is a failure for {secs} seconds"
            else:
                message = "No such process"

        print(message)
