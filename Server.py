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

def GetServerData() -> []:
    connection = pymongo.MongoClient(db_connection)
    database = connection["test"]
    collection = database["traffic data"]
    payload = collection.find({"topic":"Lewis/RoadA/Sensor"})
    list = []

    for i in payload:
        payload_data = i.get("payload")
        time_object = i.get("time")
        just_time = time_object.time().strftime('%H:%M:%S')

        if "Traffic Sensor 110" in payload_data:
             list.append([payload_data["Traffic Sensor 110"], just_time])

    return list 

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
