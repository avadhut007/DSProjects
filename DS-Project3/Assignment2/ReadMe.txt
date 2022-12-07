Commands to execute:
Used Python 3.8.10 on Ubuntu

Other two test case files are based on 2pc_main.py basic test case file so there is repeated code.

1. Basic Test Case -- Results in Global Commit or Global Abort based on randomness
run command: python3 2pc_main.py

2. P1 fails Test Case -- Results in Global Abort due to time out during voting reason: failure of P1 node
run command: python3 2pc_main-P1fails.py

3. Coordinator fails Test Case -- Results in Global Abort due to time out during voting reason: failure of Coordinator node
run command: python3 2pc_main-Cordntrfails.py

