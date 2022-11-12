from asg3 import TokenRingAlgorithm

if __name__ == "__main__":
    process_name = " P2"
    pid = 2
    port_num = 5430
    print(f"This is process: {process_name}")
    token2 = TokenRingAlgorithm(pid, port_num)
    token2.start_process()
    token2.communication_thread.join()

