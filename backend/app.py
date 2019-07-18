from flask import Flask, session
from flask_socketio import SocketIO, send
from pandas.api.types import is_numeric_dtype
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot 
import re
import difflib 
import csv
import json
import base64
from sklearn.model_selection import train_test_split
from sklearn import preprocessing as sk
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
socketio = SocketIO(app ,ping_interval=500, ping_timeout=55000,async_mode='threading') 
headers_flag  = False
task_flag = False
allow_negative_flag = False
allow_zero_flag = False
features_data = []
base64_string = ''
original_dataframe = pd.DataFrame()
clean_data = pd.DataFrame()
target = pd.DataFrame()


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

@socketio.on('loadFeaturesPayload')
def parseDataOnPayload(json_data):
	global clean_data
	cleanData(json_data)
	global original_dataframe
	original_dataframe.to_csv('dataset1_processed.csv',index=False,line_terminator='\n')
	with open("dataset1_processed.csv", "rb") as csvfile:
		base64_string = base64.b64encode(csvfile.read())
	csvfile.close()
	
	socketio.emit('cleaningStepComplete', 'Cleaning complete')
	socketio.emit('cleanedDatasetOutput',base64_string)

	clean_data.to_csv('encoded.csv',index=False,line_terminator='\n')


	print(original_dataframe.shape)
	print(clean_data.shape)
	
	call_machine_learning_models()

	# ####### ML part #########

def call_machine_learning_models():
	global original_dataframe
	global target
	global clean_data

	clean_data.dropna(inplace=True)
	#Encode the target variable
	target = encode_labels(original_dataframe.iloc[:,-1])

	print(f"DATA: {clean_data}")
	print(f"TARGET: {target}")

	X_train, X_val, y_train, y_val = train_test_split(clean_data, target, test_size=0.3)

	#SVC
	clf_svc = SVC().fit(X_train, y_train)
	svc_y_pred = clf_svc.predict(X_val)
	svc_accuracy = accuracy_score(y_val, svc_y_pred)
	print(f"Accuracy score of SVC is: {svc_accuracy}")

	#MLP
	clf_mlp = MLPClassifier().fit(X_train, y_train)
	mlp_y_pred = clf_mlp.predict(X_val)
	mlp_accuracy = accuracy_score(y_val, mlp_y_pred)
	print(f"Accuracy score of MLP is: {mlp_accuracy}")

	#Decision Tree
	clf_dt = DecisionTreeClassifier().fit(X_train, y_train)
	dt_y_pred = clf_dt.predict(X_val)
	dt_accuracy = accuracy_score(y_val, dt_y_pred)
	print(f"Accuracy score of Decision Tree Classifier is: {dt_accuracy}")

	#Random Forest Classifier
	clf_rf = RandomForestClassifier().fit(X_train, y_train)
	rf_y_pred = clf_rf.predict(X_val)
	rf_accuracy = accuracy_score(y_val, rf_y_pred)
	print(f"Accuracy score of Random Forest Classifier is: {rf_accuracy}")


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

	global original_dataframe

	if(flag):
		original_dataframe = pd.read_csv('uncleaned.csv',header=0)

	else :
		names = []
		original_dataframe = pd.read_csv('uncleaned.csv')
		for i in range(len(original_dataframe.columns)):
			names.append(str(i))
		original_dataframe = pd.read_csv('uncleaned.csv', names=names)
	

def send_header():
	
	global original_dataframe

	headers = list(original_dataframe.columns.values)
	socketio.emit('headers',{'headers':headers})

def check_column_type():
	data_list = []
	featuresReceivedFromBackend = []

	global original_dataframe

	isCategorical = {}
	for var in original_dataframe.columns:
		isCategorical[var] = 1.*original_dataframe[var].nunique()/original_dataframe[var].count() < 0.1

	for columnName in isCategorical:
		if(isCategorical[columnName] == True):
			dict_keys = ['name', 'type','category']
			dictCategory=original_dataframe[columnName].astype(str).str.lower().unique().tolist()
			dict_values = [columnName, 'categorical',dictCategory]
			data = get_dic_from_two_lists(dict_keys, dict_values)
			data_list.append(data)
			featuresReceivedFromBackend = json.dumps(data_list)
			print(featuresReceivedFromBackend)

		elif(is_numeric_dtype(original_dataframe[columnName])):
			dict_keys = ['name', 'type']
			dict_values = [columnName, 'numeric']
			data = get_dic_from_two_lists(dict_keys, dict_values)
			data_list.append(data)
			featuresReceivedFromBackend = json.dumps(data_list)
		else :
			dict_keys = ['name', 'type','category']
			dictCategory=original_dataframe[columnName].astype(str).str.lower().unique().tolist()
			dict_values = [columnName, 'categorical',dictCategory]
			data = get_dic_from_two_lists(dict_keys, dict_values)
			data_list.append(data)
			featuresReceivedFromBackend = json.dumps(data_list)
			print(featuresReceivedFromBackend)

	socketio.emit('featuresReceivedFromBackend', featuresReceivedFromBackend)

def cleanData(json_data):

	newHeaders = []
	global original_dataframe

	for i in range(len(json_data)):
		newHeaders.append(json_data[i]['name'])
	print('new',newHeaders)
	print('\n \n')
	print('origin',original_dataframe.columns)
	original_dataframe.columns  = newHeaders

	for json_itr in range(len(json_data)-1):	

		if(json_data[json_itr]['type']=='numeric'):
			numeric_json = json_data[json_itr]
			socketio.emit('cleaningStep', 'Cleaning numeric column ' + numeric_json['name'])
			clean_numeric_cols(numeric_json)
	
		else:
			categorical_json = json_data[json_itr]  
			socketio.emit('cleaningStep',  'Cleaning categorical column ' + categorical_json['name'])
			clean_categorical_cols(categorical_json)
			
		
def clean_numeric_cols(numeric_json):

	global original_dataframe
	global clean_data
	
	countOfNegatives = 0
	countOfZeros = 0
	validCounts = 0
	totalCounts = 0    
	isZeroAllowed = numeric_json['preferences']['zeroAllowed']
	isNegativeAllowed = numeric_json['preferences']['negativeAllowed']
	numericColumnName = numeric_json['name']
	totalCounts = original_dataframe[numericColumnName].shape[0]
	countOfNumericNan = (original_dataframe[numericColumnName] == np.nan).astype(int).sum(axis=0)
	original_dataframe.dropna(inplace=True)
	original_dataframe.reset_index(drop=True,inplace=True)
	

	if(isNegativeAllowed == False and isZeroAllowed==True): 

		countOfNegatives = (original_dataframe[numericColumnName] <= 0).astype(int).sum(axis=0)
		original_dataframe[numericColumnName][original_dataframe[numericColumnName] < 0] = np.nan
		original_dataframe.dropna(inplace=True)
		original_dataframe.reset_index(drop=True,inplace=True)
		validCounts  = totalCounts - (countOfNumericNan + countOfNegatives)
		socketio.emit('cleaningStepDataUpdate', {'name': numericColumnName, 'type': 'numeric',
		 'validCount' : int(validCounts), 'dirtyStats' : {'nan': int(countOfNumericNan), 'neg': int(countOfNegatives)}})

	elif(isZeroAllowed == False and isNegativeAllowed == True):
		
		countOfZeros = (original_dataframe[numericColumnName] == 0).astype(int).sum(axis=0)
		median = original_dataframe[numericColumnName].median(skipna=True)
		original_dataframe[numericColumnName][original_dataframe[numericColumnName] == 0] = median
		validCounts  = totalCounts - (countOfNumericNan + countOfZeros)
		socketio.emit('cleaningStepDataUpdate', {'name': numericColumnName, 'type': 'numeric',
		 'validCount' : int(validCounts), 'dirtyStats' : {'nan': int(countOfNumericNan), 'zero': int(countOfZeros)}})


	elif(isZeroAllowed == False and isNegativeAllowed == False):

		countOfZeros = (original_dataframe[numericColumnName] == 0).astype(int).sum(axis=0)
		countOfNegatives = (original_dataframe[numericColumnName] <= 0).astype(int).sum(axis=0)
		median = original_dataframe[numericColumnName].median(skipna=True)
		original_dataframe[numericColumnName][original_dataframe[numericColumnName] == 0] = median
		original_dataframe[numericColumnName][original_dataframe[numericColumnName] < 0] = np.nan
		original_dataframe.dropna(inplace=True)
		original_dataframe.reset_index(drop=True,inplace=True)
		countOfNegatives = (original_dataframe[numericColumnName] <= 0).astype(int).sum(axis=0)
		validCounts  = totalCounts - (countOfNumericNan + countOfZeros + countOfNegatives)
		socketio.emit('cleaningStepDataUpdate', {'name': numericColumnName, 'type': 'numeric', 
		'validCount' : int(validCounts), 'dirtyStats' : {'nan': int(countOfNumericNan), 'zero': int(countOfZeros),
		 'neg': int(countOfNegatives)}})

	else:
		validCounts  = totalCounts - countOfNumericNan 
		socketio.emit('cleaningStepDataUpdate', {'name': numericColumnName, 'type': 'numeric', 'validCount' : int(validCounts), 'dirtyStats' : {'nan': int(countOfNumericNan)}})
	
	numeric_matrix = original_dataframe[numericColumnName].as_matrix() 
	scaled_numeric_col = scale_to_zero_mean_and_unit_variance(numeric_matrix)
	scaled_numeric_col = pd.DataFrame(scaled_numeric_col)
	clean_data = pd.concat([clean_data,	scaled_numeric_col], axis=1)

def scale_to_zero_mean_and_unit_variance(column):
	scaled_data = sk.scale(column)
	scaled_data = np.reshape(scaled_data,(scaled_data.shape[0],1))
	return scaled_data

def one_hot_encoding_of_column(column):
    # First, use LabelEncoder to convert Strings to numeric values as OHE does not accept Strings
	lab_enc = sk.LabelEncoder()
	lab_enc.fit(column)
	label_encoded = lab_enc.transform(column)

    # Reshape the label_encoded array into a Nx1 matrix as OHE requires a 2-D matrix as input
	label_encoded = np.reshape(label_encoded, (label_encoded.shape[0],1))
	OHE_encoder = sk.OneHotEncoder(sparse=False)
	OHE_encoder.fit(label_encoded)
	OHE_result = OHE_encoder.transform(label_encoded)
	OHE_df = pd.DataFrame(OHE_result)
	return OHE_df

def encode_labels(data):
	lab_enc = sk.LabelEncoder()
	lab_enc.fit(data)
	labels_encoded = lab_enc.transform(data)
	labels_encoded = np.reshape(labels_encoded, (labels_encoded.shape[0],1))
	labels_encoded = pd.DataFrame(labels_encoded)
	return labels_encoded

def remove_chars(col):
    if(re.match(r'[^A-Za-z0-9]+',col)):
        return '?'
    else:
        return col

def modify_categories(col):
	modifiedRowValue = re.sub(r'\W+', '', col)
	modifiedRowValue=modifiedRowValue.lower()
	col = modifiedRowValue
	return col

def check_valid_categories(col, validCategories):
	if(col not in validCategories):
		col = '?'
	return col

def clean_categorical_cols(categorical_json):
	global clean_data
	global original_dataframe
	dirtyCount = 0
	validCount = 0
	totalCount = 0
	modifiedList =list()
	validCategories = (categorical_json['preferences']['categories'])[0].split(',')
	catColumnName = categorical_json['name']
	totalCounts = original_dataframe[catColumnName].shape[0]
	original_dataframe[catColumnName] = original_dataframe[catColumnName].astype(str).apply(remove_chars)
	dirtyCount = original_dataframe[catColumnName].str.count('\?').sum()
	
	original_dataframe[catColumnName].replace({'?':np.nan},inplace=True)
	original_dataframe.dropna(inplace=True)
	original_dataframe.reset_index(drop=True, inplace=True)
		
	for j in range(len(validCategories)):
		modifiedstr = re.sub(r'\W+', '', validCategories[j].lower())
		modifiedList.append(modifiedstr)

	print(f"modified list is is: {modifiedList}")

	original_dataframe[catColumnName] = original_dataframe[catColumnName].apply(modify_categories)

	for i in range(len(original_dataframe[catColumnName])):

		for j in range(len(validCategories)):

			if(original_dataframe[catColumnName][i] == modifiedList[j]):
				original_dataframe[catColumnName].replace({original_dataframe[catColumnName][i]:validCategories[j]},inplace=True)
				break
			elif((difflib.SequenceMatcher(None,original_dataframe[catColumnName][i],modifiedList[j]).ratio()) >= 0.87):
				original_dataframe[catColumnName].replace({original_dataframe[catColumnName][i]:validCategories[j]},inplace=True)
				break
	
	original_dataframe[catColumnName] = original_dataframe[catColumnName].apply(lambda col: check_valid_categories(col,validCategories))	
	dirtyCount = dirtyCount + (original_dataframe[catColumnName] == '?').astype(int).sum(axis=0)
				

	original_dataframe[catColumnName].replace({'?':np.nan},inplace=True)
	original_dataframe.dropna(inplace=True)
	original_dataframe.reset_index(drop=True, inplace=True)

	
	validCount = totalCount - dirtyCount
	dict1={}
	values = original_dataframe[catColumnName].value_counts().index.tolist()
	for i in range(len(values)):
		dict1[values[i]]=original_dataframe[catColumnName].value_counts()[i].astype(str)
    
	print({'name': catColumnName, 'type': 'categorical', 'validCount' : validCount, 'categoryStats' : dict1})
	socketio.emit('cleaningStepDataUpdate',	{'name': catColumnName, 'type': 'categorical', 'validCount' : int(validCount), 'categoryStats' : dict1})

	clean_data = pd.concat([clean_data,	one_hot_encoding_of_column(original_dataframe[catColumnName]) ], axis=1)

if __name__ == '__main__':
	socketio.run(app) 