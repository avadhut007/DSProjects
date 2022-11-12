from asg3 import TokenRingAlgorithm

if __name__ == "__main__":
    process_name = " P0"
    pid = 0
    port_num = 5432
    print(f"This is process: {process_name}")
    token0 = TokenRingAlgorithm(pid, port_num)
    token0.start_process()
    token0.communication_thread.join()
