from asg2 import VectorAlgorithm

if __name__ == "__main__":
    proces_name = "P2"
    pid = 2
    port_num = 5430
    event_id = "E2"
    print(f"This is process: {proces_name}")

    vector2 = VectorAlgorithm(pid,port_num,event_id)
    vector2.start_process()

    vector2.communication_thread.join()