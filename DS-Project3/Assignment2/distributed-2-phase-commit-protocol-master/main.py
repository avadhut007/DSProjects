import sys
from Network import Network
import os

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please enter input filename...")
        exit()

    filename = sys.argv[1]
    file_content = open(filename, "r")
    nodes = []
    history = []

    for line in file_content.readlines():
        if line.startswith("#"):
            continue

        if line.startswith("P"):
            if "coordinator" in line.lower():
                splitted = line.split(";")
                # Store nodes as list of tuples (PROCESS_ID, COORDINATOR_OR_NOT)
                nodes.append((splitted[0].strip(), True))
            else:
                nodes.append((line.strip(), False))
        if line.startswith("Consistency"):
            history = line.split(";")[1].strip()
            history = history.split(",")
    # Create Network
    network = Network(nodes, history)
    print("Network has been created")

    # Receive commands and process
    while True:
        print('Enter your command: ', end='$ ')
        cmd = input()
        network.process_command(cmd)
