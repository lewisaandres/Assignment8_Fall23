from datetime import datetime, timedelta
import socket
import ipaddress
import threading
import time
import contextlib
import errno
from dataclasses import dataclass
import random
import sys
import MongoDBConnection as mongo
import pymongo

maxPacketSize = 1024
defaultPort = 1024 #TODO: Set this to your preferred port

db_connection = "mongodb+srv://0000:0000@cluster0.cxagbxv.mongodb.net/?retryWrites=true&w=majority"

def GetFreePort(minPort: int = 1024, maxPort: int = 65535):
    for i in range(minPort, maxPort):
        print("Testing port",i)
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as potentialPort:
            try:
                potentialPort.bind(('localhost', i))
                potentialPort.close()
                print("Server listening on port",i)
                return i
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    print("Port",i,"already in use. Checking next...")
                else:
                    print("An exotic error occurred:",e)

def Get405Freeway(): 
    connect = pymongo.MongoClient(db_connection)
    db = connect["test"]
    collect = db["traffic_data3"]
    doc = collect.find().sort('time', -1)
    list_405 = []

    for i in doc:
        payload_data = i.get("payload")
        if "Traffic Sensor 405" in payload_data:
            list_405.append(payload_data["Traffic Sensor 405"])

    numbers_405 = list_405[:5]

    return numbers_405

def GetServerData() -> []:
    connection = pymongo.MongoClient(db_connection)
    database = connection["test"]
    collection = database["traffic data"]
    
    document = collection.find().sort('time', -1)

    list_110 = []
    list_91 = []

    for i in document:
        payload_data = i.get("payload")

        if "Traffic Sensor 110" in payload_data:
            list_110.append(payload_data["Traffic Sensor 110"])
        if "Traffic Sensor 91" in payload_data:
            list_91.append(payload_data["Traffic Sensor 91"])

    numbers_110 = list_110[:5]
    numbers_91 = list_91[:5]

    average_110 = sum(numbers_110) / len(numbers_110)
    average_91 = sum(numbers_91) / len(numbers_91)
    average_405 = sum(Get405Freeway()) / len(Get405Freeway())

    average_list = {
        "110 Freeway average": average_110,
        "91 Freeway average" : average_91, 
        "405 Freeway average": average_405
    }
    
    min_average = min(average_110, average_91, average_405)

    matching_item = next((key, value) for key, value in average_list.items() if value == min_average)

    return matching_item

# def Get405Freeway(): 
#     connect = pymongo.MongoClient(db_connection)
#     db = connect["test"]
#     collect = db["traffic_data3"]
#     doc = collect.find().sort(['time', -1])
#     list_405 = []

#     for i in doc:
#         payload_data = i.get("payload")
#         if "Traffic Sensor 405" in payload_data:
#             list_405.append([payload_data["Traffic Sensor 405"]])

#     numbers_405 = [j[0] for i, j in enumerate(list_405[:5]) if j]

#     return numbers_405

# def GetServerData() -> []:
#     connection = pymongo.MongoClient(db_connection)
#     database = connection["test"]
#     collection = database["traffic data"]
    
#     document = collection.find().sort([('time', -1)])

#     list_110 = []
#     list_91 = []

#     for i in document:
#         payload_data = i.get("payload")

#         if "Traffic Sensor 110" in payload_data:
#             list_110.append([payload_data["Traffic Sensor 110"]])
#         if "Traffic Sensor 91" in payload_data:
#             list_91.append([payload_data["Traffic Sensor 91"]])

#     connection.close()

#     # list_110 = list_110[:5]
#     numbers_110 = [j[0] for i, j in enumerate(list_110[:5]) if j]
#     numbers_91 = [j[0] for i, j in enumerate(list_91[:5]) if j]
#     # numbers = []
#     # for i,j in enumerate(list_110):
#     #     if j: 
#     #         numbers.append(j[0])


#     average_110 = sum(numbers_110) / len(numbers_110)
#     average_91 = sum(numbers_91) / len(numbers_91)
#     average_405 = sum(Get405Freeway()) / len(Get405Freeway())

#     min_average = min(average_110, average_91, average_405)

#     return min_average

# def GetServerData() -> []:
#     connection = pymongo.MongoClient(db_connection)
#     database = connection["test"]
#     collection = database["traffic data"]
#     first_document = collection.find_one()
#     end_time = 
#     start_time = end_time - timedelta(minutes=5)

#     query = {
#         "topic": "Lewis/RoadA/Sensor",
#         "time": {"$gte": start_time, "$lt": end_time}
#     }
#     document = collection.find(query)
#     list_110 = []

#     for i in document:
#         payload_data = i.get("payload")
#         time_object = i.get("time")
#         convert_time = time_object.time().strftime('%H:%M:%S')

#         if "Traffic Sensor 110" in payload_data:
#             list_110.append([payload_data["Traffic Sensor 110"], convert_time])

#     return list_110 


def ListenOnTCP(tcpSocket: socket.socket, socketAddress):
    #TODO: Implement TCP Code, use GetServerData to query the database.
    
    client_message = str(tcpSocket.recv(1024).decode())

    print(f"Client's message: {client_message}")

    # data = ""
    # for i in GetServerData():
    #     data = "Traffic Senser: " + str(i[0]) + "\nTime: " + str(i[1])

    data = GetServerData()
    try: 
        tcpSocket.send(str(data).encode())
        print("data sent to client")
    except: 
        print("didnt send data from ListenOnTCP()")



def CreateTCPSocket() -> socket.socket:
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpPort = defaultPort
    print("TCP Port:",tcpPort)
    tcpSocket.bind(('localhost', tcpPort))
    return tcpSocket

def LaunchTCPThreads():
    tcpSocket = CreateTCPSocket()
    tcpSocket.listen(5)
    while True:
        connectionSocket, connectionAddress = tcpSocket.accept()
        connectionThread = threading.Thread(target=ListenOnTCP, args=[connectionSocket, connectionAddress])
        connectionThread.start()

if __name__ == "__main__":
    tcpThread = threading.Thread(target=LaunchTCPThreads)
    tcpThread.start()

    exitSignal = False

    while not exitSignal:
        time.sleep(1)
    print("Ending program by exit signal...")
