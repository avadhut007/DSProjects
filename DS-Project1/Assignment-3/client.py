import socket
import pickle
import math
import numpy as np

packet_size = 1024


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(),5432))

def get_input_from_user():
    option = 0
    while option not in range(1,6):

        print("""
            Select one of the functions:
            1. Calculate the Pi value
            2. Addition of two numbers
            3. Sort an array
            4. Matrix multiplication
            5. Quit
            """)
        option = input("Enter number of selected function: ")
        try:
            option = int(option)
        except:
            option = 0
        if option not in range(1,6):
            print("\n--- Invalid option provided. Please select again. ---")
        return option

def calculate_pi():
    function_name = "calculate_pi"
    data = {"function_name": function_name }
    data = pickle.dumps(data)
    client_socket.send(data)
    
    pi_val = client_socket.recv(packet_size)
    pi_val = pickle.loads(pi_val)
    print(f"\nThe Pi value received from the server is: {pi_val} ")
    return

def add():
    first = input("Enter the first integer number: ")
    first = int(first)
    second = input("Enter the Secondinteger number: ")
    second = int(second)

    function_name = "add"
    data = {"function_name": function_name, "first": first, "second": second}
    data = pickle.dumps(data)            
    client_socket.send(data)

    addition_res = client_socket.recv(packet_size)
    addition_res = pickle.loads(addition_res)
    print(f"\nSum of the two numbers is: {addition_res}")
    return
    
def sort():
    arr = []
    n = input("enter the array length: ")
    print("enter the array values: ")
    n = int(n)
    for i in range(0, n):
        # print(i)
        value = input()
        arr.append(int(value))

    function_name = "sort"
    data = {"function_name": function_name, "arr": arr} 
    data = pickle.dumps(data)            
    client_socket.send(data)

    sorted_res = client_socket.recv(packet_size)
    sorted_res = pickle.loads(sorted_res)
    print(f"\nThe sorted array received from the server is: {sorted_res}")
    return

def matrix_multiply():

    Ra = int(input("Enter number of rows in matrixA: "))
    Ca = int(input("Enter number of columns in matrixA: "))
    matrixA = []
    print(" Enter values for matrixA: ")
    for i in range(Ra):
        mata = []
        for j in range(Ca):
            mata.append(int(input()))
        matrixA.append(mata)
    print("matrixA: ") 
    for i in range(Ra):
        for j in range(Ca):
            print(matrixA[i][j], end = " ")
        print() 

    Rb =  Ca
    print("The number of rows in matrixB is same as maxtrixA's columns: ",Rb)
    Cb = int(input("Enter number of columns in matrixB: "))
    matrixB = []
    print("Enter values for matrixB: ")
    for i in range(Rb):
        matb = []
        for j in range(Cb):
            matb.append(int(input()))
        matrixB.append(matb)
    print("matrixB: ")     
    for i in range(Rb):
        for j in range(Cb):
            print(matrixB[i][j], end = " ")
        print()

    print("\nThe number of rows in matrixC:",Ra)
    print("The number of columns  in matrixC:",Cb)

    function_name = "matrix_multiply"
    data = {"function_name": function_name, "first": matrixA,  "second": matrixB, "third": [Ra,Cb]} 
    data = pickle.dumps(data)            
    client_socket.send(data)

    result_matrixC = client_socket.recv(packet_size)
    result_matrixC = pickle.loads(result_matrixC)
    print(f"\nThe matrixC: multiplication of the matrices received from the server is: {result_matrixC}")
    return


while True:
    option = 0
    while option != 5:
        option = get_input_from_user()
        if option == 1:
            calculate_pi()

        elif option == 2:
            add()

        elif option == 3:
            sort()

        elif option == 4:
            matrix_multiply()

    if option == 5:
        print("--- Closed the connection. ---")
        client_socket.close()
        exit()
