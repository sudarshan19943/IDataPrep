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
	dataframe_with_headers = process_data(headers_flag)
	send_header(dataframe_with_headers)
	check_column_type(dataframe_with_headers)
	parseJsonData(json_data,dataframe_with_headers)


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

	if(flag):
		dataframe_with_headers = pd.read_csv('uncleaned.csv',header=0, index_col=False)

	else :
		names = []
		dataframe_without_headers = pd.read_csv('uncleaned.csv', index_col=False)
		for i in range(len(dataframe_without_headers.columns)):
			names.append(i)
		dataframe_with_headers = pd.read_csv('uncleaned.csv', names=names, index_col=False)

	return dataframe_with_headers


def send_header(dataframe):
	headers = dataframe.columns.tolist()
	socketio.emit('headers',{'headers':headers})

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


def parseJsonData(json_data, dataframe):
	cleaned_df = pd.DataFrame()
	
	for json_itr in range(len(json_data)):
		if(json_data[json_itr]['type']=='numeric'):
			numeric_json = json_data[json_itr]
			cleaned_df = pd.concat([cleaned_df,clean_numeric_cols(numeric_json,dataframe)], axis=1)	
		else:
			categorical_json = json_data[json_itr]
			cleaned_df = pd.concat([cleaned_df,clean_categorical_cols(categorical_json,dataframe)],axis=1)
	
	cleaned_df.dropna(inplace=True)
	print(cleaned_df.isna().sum())			

def clean_numeric_cols(numeric_json, df):
	column_name = int(numeric_json['name'])
	tempNumColDf = df[column_name].to_frame()
	if(numeric_json['preferences']['zeroAllowed'] == False):
		tempNumColDf = tempNumColDf.replace({0:np.nan})

	if(numeric_json['preferences']['negativeAllowed'] == False):
		tempNumColDf = tempNumColDf.abs()
	
	df = tempNumColDf
	return df

def clean_categorical_cols(categorical_json,df):

	tempCatColumnDf = df[int(categorical_json['name'])].to_frame()
	print(type(tempCatColumnDf[1][1]))
	modifiedList =[]
	validCategories = categorical_json['preferences']['categories']

	for i in range(len(tempCatColumnDf)):
		if(re.match(r'[A-Za-z0-9]+',str(tempCatColumnDf[1][i]))):
			tempCatColumnDf[1][i] = tempCatColumnDf[1][i]
		else:
			tempCatColumnDf[1][i] = '?'

	tempCatColumnDf.replace({'?':np.nan},inplace=True)
	
	for j in range(len(validCategories)):

		modifiedstr=validCategories[j].lower()
		modifiedstr = re.sub(r'\W+', '', modifiedstr)
		modifiedList.append(modifiedstr)
		
	for i in range(len(tempCatColumnDf)):

		modifiedRowValue = re.sub(r'\W+', '', str(tempCatColumnDf[1][i]))
		modifiedRowValue=modifiedRowValue.lower()
		tempCatColumnDf.replace({tempCatColumnDf[1][i]:modifiedRowValue},inplace=True)	

	for i in range(len(tempCatColumnDf)):

		for j in range(len(validCategories)):

			if(tempCatColumnDf[1][i] == modifiedList[j]):
				tempCatColumnDf.replace({tempCatColumnDf[1][i]:validCategories[j]},inplace=True)
				break
			elif((difflib.SequenceMatcher(None,tempCatColumnDf[1][i],modifiedList[j]).ratio()) >= 0.87):
				tempCatColumnDf.replace({tempCatColumnDf[1][i]:validCategories[j]},inplace=True)
				break
				
	for i in range(len(tempCatColumnDf)):
		if(tempCatColumnDf[1][i] not in validCategories):
			tempCatColumnDf.replace({tempCatColumnDf[1][i]:'?'},inplace=True)
	
	tempCatColumnDf.replace({'?':np.nan},inplace=True)
	
	return tempCatColumnDf

	
if __name__ == '__main__':
    socketio.run(app)