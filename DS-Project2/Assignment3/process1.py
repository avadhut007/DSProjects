from asg3 import TokenRingAlgorithm

if __name__ == "__main__":
    process_name = " P1"
    pid = 1
    port_num = 5431
    print(f"This is process: {process_name}")
    token1 = TokenRingAlgorithm(pid, port_num)
    token1.initialize()
    token1.connection_thread.join()
