from asg1 import TotalOrderMultiCast


if __name__ == "__main__":
    proces_name = "P3"
    pid = 3
    port_num = 5430
    event_id = "E3"
    event_id2 = "E33"
    print(f"This is process: {proces_name}")

    lamport3 = TotalOrderMultiCast(pid, port_num, event_id, event_id2)
    lamport3.start_process()

    lamport3.communication_thread.join()

    lamport3.delivery_thread.join()

