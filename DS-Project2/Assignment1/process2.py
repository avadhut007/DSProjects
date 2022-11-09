from asg1 import TotalOrderMultiCast


if __name__ == "__main__":
    proces_name = "P2"
    pid = 2
    port_num = 5431
    event_id = "E2"
    event_id2 = "E22"
    print(f"This is process: {proces_name}")

    lamport2 = TotalOrderMultiCast(pid, port_num, event_id, event_id2)
    lamport2.start_process()

    lamport2.communication_thread.join()

    lamport2.delivery_thread.join()