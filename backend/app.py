from flask import Flask 
from flask_socketio import SocketIO, send
from pandas.api.types import is_numeric_dtype
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot 
import re
import difflib 
import csv
import json

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg , broadcast=True)

@socketio.on('loaddata')
def handleData(data,flag):
	read_the_csv(data,flag)
	

def read_the_csv(data,flag):
	csvList = data.split('\n')
	with open('uncleaned.csv', 'w', newline='') as myfile:
		for i in range(0,len(csvList)):
			wr = csv.writer(myfile)
			wr.writerow(csvList[i].split(','))
			
	myfile.close()
	process_data(flag)


def send_header(dataframe):
	headers = dataframe.columns.to_list()
	socketio.emit('headers',{'headers':headers})

def get_dic_from_two_lists(keys, values):
	return { keys[i] : values[i] for i in range(len(keys)) }


def check_column_type(dataframe):
	data_list = []
	for columnName in dataframe:
		if(is_numeric_dtype(dataframe[columnName])):
			dict_keys = ['name', 'type']
			dict_values = [columnName, 'numeric']
			data = get_dic_from_two_lists(dict_keys, dict_values)
			data_list.append(data)
			featuresReceivedFromBackend = json.dumps(data_list)
		else:
			dict_keys = ['name', 'type']
			dict_values = [columnName, 'categorical']
			data = get_dic_from_two_lists(dict_keys, dict_values)
			data_list.append(data)
			featuresReceivedFromBackend = json.dumps(data_list)
	socketio.emit('featuresReceivedFromBackend', featuresReceivedFromBackend)

def process_data(flag):
	if(flag):
		dataframe_with_headers = pd.read_csv('uncleaned.csv',header=0)
		send_header(dataframe_with_headers)
		check_column_type(dataframe_with_headers)	

	else :
		names = []
		dataframe_without_headers = pd.read_csv('uncleaned.csv')
		print(len(dataframe_without_headers.columns))
		for i in range(len(dataframe_without_headers.columns)):
			names.append(i)
		dataframe_with_headers = pd.read_csv('uncleaned.csv', names=names)
		send_header(dataframe_with_headers)
		check_column_type(dataframe_with_headers)





		
	





	
if __name__ == '__main__':
    socketio.run(app)