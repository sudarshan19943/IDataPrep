from flask import Flask 
from flask_socketio import SocketIO, send
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot 
import re
import difflib 


app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg , broadcast=True)

@socketio.on('loaddata')
def handleData(data):
	print('Data')
	print(data)


	
if __name__ == '__main__':
    socketio.run(app)