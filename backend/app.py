from flask import Flask, session
from flask_session import Session
from flask_socketio import SocketIO, send
from pandas.api.types import is_numeric_dtype
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot 
import re
import difflib 
import csv
import json
import pickle

app = Flask(__name__)
Session(app)
socketio = SocketIO(app) 
headers_flag  = False
task_flag = False
allow_negative_flag = False
allow_zero_flag = False
features_data = []

def read_pkl():
	df = pd.DataFrame()
	with open("original_df.pkl", "rb") as f:
		df = pickle.load(f)
	f.close()
	return df

def write_pkl(df):
	with open("original_df.pkl", "wb") as f:
		pickle.dump(df,f)
	f.close()

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg , broadcast=True)

@socketio.on('loaddata')
def handleData(data,h_flag,t_flag):

	headers_flag = h_flag
	task_flag = t_flag
	read_the_csv(data,headers_flag)
	process_data(headers_flag)
	send_header()
	check_column_type()
	original_dataframe = read_pkl()
	original_dataframe.to_csv('dataset1_processed.csv', header=False,index=False,line_terminator='')
	
@socketio.on('loadFeaturesPayload')
def parseDataOnPayload(json_data):
	socketio.emit('cleaningStep', 'Cleaning')
	cleanData(json_data)
	cleaned_dataframe  = read_pkl()
	socketio.emit('cleaningStepComplete', 'Cleaning complete')
	socketio.emit('cleanedDatasetOutput',cleaned_dataframe.to_csv('cleaned.csv', index=False))

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

	else :
		names = []
		original_dataframe = pd.read_csv('uncleaned.csv')
		for i in range(len(original_dataframe.columns)):
			names.append(str(i))
		original_dataframe = pd.read_csv('uncleaned.csv', names=names)
		
	write_pkl(original_dataframe)

def send_header():
	original_dataframe = read_pkl()
	print("inside send header")
	headers = list(original_dataframe.columns.values)
	socketio.emit('headers',{'headers':headers})

def check_column_type():
	data_list = []
	featuresReceivedFromBackend = []
	original_dataframe = read_pkl()

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


def cleanData(json_data):
	print("inside parse")
	newHeaders = []
	
	original_dataframe = read_pkl()

	for i in range(len(json_data)):
		newHeaders.append(json_data[i]['name'])

	original_dataframe.columns  = newHeaders

	for json_itr in range(len(json_data)):	
		if(json_data[json_itr]['type']=='numeric'):
			numeric_json = json_data[json_itr]
			clean_numeric_cols(numeric_json)
		else:
			categorical_json = json_data[json_itr]
			clean_categorical_cols(categorical_json)
	
	write_pkl(original_dataframe)
	

def clean_numeric_cols(numeric_json):

	original_dataframe = read_pkl()
	print("inside numeric")
	isZeroAllowed = numeric_json['preferences']['zeroAllowed']
	isNegativeAllowed = numeric_json['preferences']['negativeAllowed']
	numericColumnName = numeric_json['name']

	if(isZeroAllowed == False):
		original_dataframe[numericColumnName] = original_dataframe[numericColumnName].replace({0:np.nan})
		original_dataframe[numericColumnName].dropna(inplace = True)
		original_dataframe.reset_index(drop=True, inplace=True)

	if(isNegativeAllowed == False):
		original_dataframe[numericColumnName] = original_dataframe[numericColumnName].abs()

	write_pkl(original_dataframe)
	
	
def clean_categorical_cols(categorical_json):
	original_dataframe = read_pkl()
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
		
	for j in range(len(validCategories)):

		modifiedstr=validCategories[j].lower()
		modifiedstr = re.sub(r'\W+', '', modifiedstr)
		modifiedList.append(modifiedstr)

	for i in range(len(original_dataframe[catColumnName])):

		modifiedRowValue = re.sub(r'\W+', '', original_dataframe[catColumnName][i])
		modifiedRowValue=modifiedRowValue.lower()
		original_dataframe[catColumnName].replace({original_dataframe[catColumnName][i]:modifiedRowValue},inplace=True)	

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


	original_dataframe[catColumnName].replace({'?':np.nan},inplace=True)
	original_dataframe.dropna(inplace=True)
	original_dataframe.reset_index(drop=True, inplace=True)
	write_pkl(original_dataframe)
	

if __name__ == '__main__':
    socketio.run(app)