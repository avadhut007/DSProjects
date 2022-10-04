Notes before running files
-------------------------------
- Each time you close client you should close server as well.

- Before starting the client, restart the server always.

- File names containing svr are server directory files.
- File names containing cli are client directory files.

Steps:
-------------------------------

1. Start two or more terminals and change directory to Assignment-2

2. Run server.py in the first terminal.
python3 server.py

3. Run client.py in the second terminal.
python3 client.py

4. Run client.py in the third terminal as well to check multithreading.
python3 client.py

4. Select options from list of instructions on the terminal. To select type the number of option and enter.

5. Select download or upload options on both client terminals Do not enter files yet.
   And now type required files names on both clients. Then quickly press enter on both clients.

6. On the server you can see new threads for each client and also timestamp of operations which proves they were started seperately but at same time.

7. To check the the list of files in the server or client use respective options.

8. In the end, select last option to close the clients. Close the server as well.