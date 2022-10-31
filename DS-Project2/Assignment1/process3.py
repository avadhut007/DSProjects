from asg1 import TotalOrderMultiCast
proces_name = "P3"
pid = 3
port_num = 5430
event_id = "E3"
print(f"This is process: {proces_name}")

lamport3 = TotalOrderMultiCast(pid,port_num,event_id)
lamport3.start_process()
