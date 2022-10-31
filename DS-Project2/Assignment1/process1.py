from asg1 import TotalOrderMultiCast
import multiprocessing as mp

if __name__ == "__main__":
    proces_name = "P1"
    pid = 1
    port_num = 5432
    event_id = "E1"
    print(f"This is process: {proces_name}")

    lamport1 = TotalOrderMultiCast(pid,port_num,event_id)
    lamport1.start_process()

    lamport1.communication_thread.join()

    lamport1.delivery_thread.join()