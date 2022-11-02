from asg2 import VectorAlgorithm

if __name__ == "__main__":
    proces_name = "P1"
    pid = 1
    port_num = 5431
    event_id = "E1"
    print(f"This is process: {proces_name}")

    vector1 = VectorAlgorithm(pid,port_num,event_id)
    vector1.start_process()

    vector1.communication_thread.join()