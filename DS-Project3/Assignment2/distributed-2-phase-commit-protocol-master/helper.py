import socket
import subprocess
import os
import time


def send_message(message, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sc:
        sc.settimeout(2)
        try:
            time.sleep(0.2)
            sc.connect(('127.0.0.1', port))
            #print("sending mesg conn success",port)
        except Exception as e:
            #print("sending mesg conn failed",e)
            return ''

        sc.send(message.encode('utf-8'))
        r_msg = sc.recv(2048).decode('utf-8')
        #print("received messg=",r_msg)
        return r_msg


def create(id_, is_coordinator, port, value):
    python_run_command = 'python3 Process.py --id {} --port {} --isCoordinator {} --value {}'.format(
        id_, port, is_coordinator, value)
    #print(python_run_command,"Helper file")
    subprocess.Popen(python_run_command, shell=True, stdout=subprocess.PIPE)
