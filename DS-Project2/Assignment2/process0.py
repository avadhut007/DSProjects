from asg2 import VectorAlgorithm

if __name__ == "__main__":
    proces_name = "P0"
    pid = 0
    port_num = 5432
    event_id = "E0"
    print(f"This is process: {proces_name}")

    vector0 = VectorAlgorithm(pid,port_num,event_id)
    vector0.start_process()

    vector0.communication_thread.join()