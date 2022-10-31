from asg1 import TotalOrderMultiCast
proces_name = "P2"
pid = 2
port_num = 5431
event_id = "E2"
print(f"This is process: {proces_name}")

lamport2 = TotalOrderMultiCast(pid,port_num,event_id)
lamport2.start_process()
