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

def GetBestFreeway(average_list: dict): 
    min_average = min(average_list["91 Freeway"], average_list["110 Freeway"], average_list["405 Freeway"])

    best_freeway = next((key, value) for key, value in average_list.items() if value == min_average)
    #document = collection.find({"time": {"$gte": recent_time - timedelta(minutes=5)}}).sort("time", pymongo.DESCENDING)
    # list = []
    # for i in document:
    #     list.append([i.get("payload").get("91_sensor"), i.get("time")])
    return best_freeway

def GetServerData() -> []:
    connection = pymongo.MongoClient(db_connection)
    database = connection["test"]
    collection = database["traffic_collection"]

    recent_document = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
    recent_time = recent_document.get("time")
    document = collection.find({"time": {"$gte": recent_time - timedelta(minutes=5)}}).sort("time", pymongo.DESCENDING)

    list_91, list_110, list_405 = [], [], []

    for i in document:
        payload_data = i.get("payload")
        list_91.append(payload_data["91_sensor"])
        list_110.append(payload_data["110_sensor"])
        list_405.append(payload_data["405_sensor"])


    average_110 = sum(list_110) / len(list_110)
    average_91 = sum(list_91) / len(list_91)
    average_405 = sum(list_405) / len(list_405)

    average_list = {
        "110 Freeway": average_110,
        "91 Freeway" : average_91, 
        "405 Freeway": average_405
    }
    
    return average_list


def ListenOnTCP(tcpSocket: socket.socket, socketAddress):
    #TODO: Implement TCP Code, use GetServerData to query the database.
    
    client_message = str(tcpSocket.recv(1024).decode())

    print(f"Client's message: {client_message}")

    data = GetServerData()
    data2 = GetBestFreeway(GetServerData())
    try: 
        list_freeways = str("\nList of freeways with average values:\n").encode()
        best_freeway = str("\n\nBest freeway to use: \n").encode()
        tcpSocket.send(list_freeways + str(data).encode() + best_freeway + str(data2).encode())
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
