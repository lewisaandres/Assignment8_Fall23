from pymongo import MongoClient, database
import subprocess
import threading
import pymongo
from datetime import datetime, timedelta
import time

DBName = "test" #Use this to change which Database we're accessing
connectionURL = "mongodb+srv://0000:0000@cluster0.cxagbxv.mongodb.net/?retryWrites=true&w=majority" #Put your database URL here
sensorTable = "traffic_collection" #Change this to the name of your sensor data table

def QueryToList(query):
	#TODO: Convert the query that you get in this function to a list and return it
	#HINT: MongoDB queries are iterable
	list = []
	for i in query: 
		list.append(i)
	
	return list 
	


def QueryDatabase() -> []:
	global DBName
	global connectionURL
	global currentDBName
	global running
	global filterTime
	global sensorTable
	cluster = None
	client = None
	db = None
	try:
		# cluster = connectionURL
		# client = MongoClient(cluster)
		# db = client[DBName]
		# print("Database collections: ", db.list_collection_names())
		connection = pymongo.MongoClient(connectionURL)
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

		# #We first ask the user which collection they'd like to draw from.
		# sensorTable = db[sensorTable]
		# print("Table:", sensorTable)
		# #We convert the cursor that mongo gives us to a list for easier iteration.
		# timeCutOff = datetime.now() - timedelta(minutes=0) #TODO: Set how many minutes you allow

		# oldDocuments = QueryToList(sensorTable.find({"time":{"$gte":timeCutOff}}))
		# currentDocuments = QueryToList(sensorTable.find({"time":{"$lte":timeCutOff}}))

		# print("Current Docs:",currentDocuments)
		# print("Old Docs:",oldDocuments)

		# #TODO: Parse the documents that you get back for the sensor data that you need
		# #Return that sensor data as a list
		connection.close()
		return average_list


	except Exception as e:
		print("Please make sure that this machine's IP has access to MongoDB.")
		print("Error:",e)
		exit(0)


QueryDatabase()