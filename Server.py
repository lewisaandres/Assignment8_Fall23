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

db_connection = str(input("Type in the mongodb connection url"))

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

    return best_freeway

def GetServerData() -> []:
    return mongo.QueryDatabase()


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
        
        # Uncomment below to check 5 min interval queries of documents
        # tcpSocket.send(str(data).encode())
        print("data sent to client")
    except: 
        print("didnt send data from ListenOnTCP()")



def CreateTCPSocket() -> socket.socket:
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpPort = defaultPort
    print("Server is running...\nTCP Port:",tcpPort)
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
