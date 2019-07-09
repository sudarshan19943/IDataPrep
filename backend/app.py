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
headers_flag  = False
task_flag = False
allow_negative_flag = False
allow_zero_flag = False
features_data = []
original_dataframe = pd.DataFrame()

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg , broadcast=True)

@socketio.on('loaddata')
def handleData(data,json_data,h_flag,t_flag):
	
	headers_flag = h_flag
	task_flag = t_flag
	read_the_csv(data,headers_flag)
	process_data(headers_flag)
	print(original_dataframe.head(10))
	send_header()
	check_column_type()
	parseJsonData(json_data)
	print(original_dataframe.head(400))


def read_the_csv(data,flag):
	csvList = data.split('\n')
	with open('uncleaned.csv', 'w', newline='') as myfile:
		for i in range(0,len(csvList)):
			wr = csv.writer(myfile)
			wr.writerow(csvList[i].split(','))

	myfile.close()

def get_dic_from_two_lists(keys, values):
	return { keys[i] : values[i] for i in range(len(keys)) }

def process_data(flag):
	
	print("inside process data")

	if(flag):
		original_dataframe = pd.read_csv('uncleaned.csv',header=0)
		print("inside headers ", original_dataframe)
	else :
		names = []
		original_dataframe = pd.read_csv('uncleaned.csv')
		for i in range(len(original_dataframe.columns)):
			names.append(str(i))
		original_dataframe = pd.read_csv('uncleaned.csv', names=names)


def send_header():
	print("inside send header")
	headers = list(original_dataframe.columns.values)
	socketio.emit('headers',{'headers':headers})

def check_column_type():
	data_list = []
	featuresReceivedFromBackend = []
	print(original_dataframe)
	for columnName in original_dataframe:
		if(is_numeric_dtype(original_dataframe[columnName])):
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


def parseJsonData(json_data):
	print("inside parse")
	for json_itr in range(len(json_data)):
		if(json_data[json_itr]['type']=='numeric'):
			numeric_json = json_data[json_itr]
			clean_numeric_cols(numeric_json)
		else:
			categorical_json = json_data[json_itr]
			clean_categorical_cols(categorical_json)
	

def clean_numeric_cols(numeric_json):


	print("inside numeric")
	isZeroAllowed = numeric_json['preferences']['zeroAllowed']
	print(isZeroAllowed)
	isNegativeAllowed = numeric_json['preferences']['negativeAllowed']
	numericColumnName = numeric_json['name']
	print(original_dataframe)

	if(isZeroAllowed == False):
		original_dataframe[numericColumnName] = original_dataframe[numericColumnName].replace({0:np.nan})
		original_dataframe[numericColumnName].dropna()

	if(isNegativeAllowed == False):
		original_dataframe[numericColumnName] = original_dataframe[numericColumnName].abs()
	
	
def clean_categorical_cols(categorical_json):

	print("inside cat")
	
	modifiedList =[]
	validCategories = categorical_json['preferences']['categories']
	catColumnName = categorical_json['name']
	original_dataframe[catColumnName] = original_dataframe[catColumnName].astype(str)

	for i in range(len(original_dataframe[catColumnName])):
		if(re.match(r'[A-Za-z0-9]+',original_dataframe[catColumnName][i])):
			original_dataframe[catColumnName][i] = original_dataframe[catColumnName][i]
		else:
			original_dataframe[catColumnName][i] = '?'

	original_dataframe[catColumnName].replace({'?':np.nan},inplace=True)
	original_dataframe[catColumnName].dropna(inplace=True)
	original_dataframe[catColumnName].reset_index(drop=True, inplace=True)
		
	original_dataframe[catColumnName].to_csv('untitled.csv',index=False)
	
	for j in range(len(validCategories)):

		modifiedstr=validCategories[j].lower()
		modifiedstr = re.sub(r'\W+', '', modifiedstr)
		modifiedList.append(modifiedstr)

	# print(modifiedList)
	# print(original_dataframe[catColumnName].shape[0])

	for i in range(len(original_dataframe[catColumnName])):

		modifiedRowValue = re.sub(r'\W+', '', original_dataframe[catColumnName][i])
		modifiedRowValue=modifiedRowValue.lower()
		original_dataframe[catColumnName].replace({original_dataframe[catColumnName][i]:modifiedRowValue},inplace=True)	

	# print(original_dataframe[catColumnName])	


	for i in range(len(original_dataframe[catColumnName])):

		for j in range(len(validCategories)):

			if(original_dataframe[catColumnName][i] == modifiedList[j]):
				original_dataframe[catColumnName].replace({original_dataframe[catColumnName][i]:validCategories[j]},inplace=True)
				break
			elif((difflib.SequenceMatcher(None,original_dataframe[catColumnName][i],modifiedList[j]).ratio()) >= 0.87):
				original_dataframe[catColumnName].replace({original_dataframe[catColumnName][i]:validCategories[j]},inplace=True)
				break
				
	for i in range(len(original_dataframe[catColumnName])):
		if(original_dataframe[catColumnName][i] not in validCategories):
			original_dataframe[catColumnName].replace({original_dataframe[catColumnName][i]:'?'},inplace=True)
	
	

	
if __name__ == '__main__':
    socketio.run(app)