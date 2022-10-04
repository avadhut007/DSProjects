from http import client
import socket
import asyncio
import math
import pickle


packet_size = 1024


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(),9999))

async def defsyncfunction():
    for i in range(0,20):
        await asyncio.sleep(.5)
        print("performing client actions")


async def client_add(i,j):
    function_name = "add"
    data = {"function_name": function_name,"first":i, "second":j}
    data = pickle.dumps(data)
    client_socket.send(data)
    add_result = client_socket.recv(packet_size)
    add_result = pickle.loads(add_result)
    await asyncio.sleep(0.5)
    print(f"\n Sum of the two numbers is: {add_result}")    
    return add_result

async def client_sort(arrayA):
    function_name = "sort"
    data = {"function_name": function_name, "arr": arrayA}
    data = pickle.dumps(data)
    client_socket.send(data)

    sort_result  = client_socket.recv(packet_size)
    sort_result = pickle.loads(sort_result)

    #sort_result = client_socket.bubblesort(arrayA)
    await asyncio.sleep(0.5)
    print(f"\nSorted array is : {sort_result}")
    return sort_result

async def client_multi(matrix_A,matrix_B,Ra,Cb):
    
    function_name = "matrix_multiply"
    data = {"function_name":function_name,"first": matrix_A, "second": matrix_B, "third": [Ra,Cb] }
    data = pickle.dumps(data)
    client_socket.send(data)
    
    result_multiply = client_socket.recv(packet_size)
    result_multiply = pickle.loads(result_multiply)
    await asyncio.sleep(1)
    print(f"\nMatrix multiplication is : {result_multiply}")
    return result_multiply

async def asynchronous():

    print('Calculate pi ')
    function_name = "calculate_pi"
    data = {"function_name": function_name}
    data = pickle.dumps(data)
    client_socket.send(data)
    pi_value = client_socket.recv(packet_size)
    pi_value = pickle.loads(pi_value)
    print('Value of pi is : ', pi_value)

    print('Addition of two numbers')
    first = int(input('Enter first number : '))
    second = int(input('Enter second number : '))

    function_name = "add"
    data = {"function_name": function_name,"first":first, "second":second}
    data = pickle.dumps(data)
    client_socket.send(data)
    add_result = client_socket.recv(packet_size)
    add_result = pickle.loads(add_result)
    print(f"\n Sum of the two numbers is: {add_result}")


    print('Sort an array')
    arr = []
    n = input("Enter the array length: ")
    print("Enter the array values: ")
    n = int(n)
    for i in range(0, n):
       value = input()
       arr.append(int(value))
    #print(arr)

    
    task = asyncio.create_task(client_sort(arr))

    print('Matrix multiplication')
    Ra = int(input("Enter number of rows: "))
    Ca = int(input("Enter number of columns: "))
    matrix_A = []
    print(" Enter values for matrix A : ")
    for i in range(Ra):
        mata = []
        for j in range(Ca):
            mata.append(int(input()))
        matrix_A.append(mata)
    for i in range(Ra):
        for j in range(Ca):
            print(matrix_A[i][j], end = " ")
        print() 

    Rb =  Ca
    print("The number of rows in matrixB is same as maxtrixA's columns: ",Rb)
    Cb = int(input("Enter number of columns: "))
    matrix_B = []
    print(" Enter values for matrix B : ")
    for i in range(Rb):
        matb = []
        for j in range(Cb):
            matb.append(int(input()))
        matrix_B.append(matb)
    for i in range(Rb):
        for j in range(Cb):
            print(matrix_B[i][j], end = " ")
        print()

    task2 = asyncio.create_task(client_multi(matrix_A,matrix_B,Ra,Cb))
    sort_result = await task
    result_multiply = await task2
    
async def deffsync():

    print('Calculate pi ')
    function_name = "calculate_pi"
    data = {"function_name": function_name}
    data = pickle.dumps(data)
    client_socket.send(data)
    pi_value = client_socket.recv(packet_size)
    pi_value = pickle.loads(pi_value)
    print('Value of pi is : ', pi_value)

    print('Addition of two numbers ')
    first = int(input('Enter the first number: '))
    second = int(input('Enter the second number: '))

    print('Sorting an array ')
    arr = []
    n = input("Enter the array length: ")
    print("Enter the array values: ")
    n = int(n)
    for i in range(0, n):
       value = input()
       arr.append(int(value))
    #print(arr)

    print('Matrix multiplication')
    Ra = int(input("Enter number of rows: "))
    Ca = int(input("Enter number of columns: "))
    matrix_A = []
    print(" Enter values for matrix A : ")
    for i in range(Ra):
        mata = []
        for j in range(Ca):
            mata.append(int(input()))
        matrix_A.append(mata)
    for i in range(Ra):
        for j in range(Ca):
            print(matrix_A[i][j], end = " ")
        print() 

    Rb =  Ca
    print("The number of rows in matrixB is same as maxtrixA's columns: ",Rb)
    Cb = int(input("Enter number of columns: "))
    matrix_B = []
    print(" Enter values for matrix B : ")
    for i in range(Rb):
        matb = []
        for j in range(Cb):
            matb.append(int(input()))
        matrix_B.append(matb)
    for i in range(Rb):
        for j in range(Cb):
            print(matrix_B[i][j], end = " ")
        print()


    task3 = asyncio.create_task(client_sort(arr))
    task4 = asyncio.create_task(defsyncfunction())

    task5 = asyncio.create_task(client_multi(matrix_A,matrix_B,Ra,Cb))
    task6 = asyncio.create_task(defsyncfunction())

    task7 = asyncio.create_task(client_add(first,second))
    task8 = asyncio.create_task(defsyncfunction())

    await asyncio.sleep(2.2)
    add_result = await task7
    sort_result = await task3
    matrix_multiply = await task4

def get_input_from_user():

    print("1.Async")
    print("2.Deferred Sync")
    val = int(input("select a operation to perform: "))
    print(val)

    if(val==1):
        asyncio.run(asynchronous()) 
    elif(val==2):
        asyncio.run(deffsync())
    
    return val


while True:
    option = 0
    while option !=3:
        option = get_input_from_user()
        if option == 1:
           asynchronous() 
        elif option ==2:
            deffsync()
    
    if option == 3:
        print("---closed the conncection.---")
        client_socket.close()
        exit()