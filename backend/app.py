from flask import Flask 
from flask_socketio import SocketIO, send
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot 
import re
import difflib 
import csv

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

	if(flag):

		dataframe_with_headers = pd.read_csv('uncleaned.csv',header=0)
		print(dataframe_with_headers.columns)

	else :
		dataframe_without_headers = pd.read_csv('uncleaned.csv')



		
	





	
if __name__ == '__main__':
    socketio.run(app)